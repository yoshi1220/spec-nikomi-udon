#!/usr/bin/env python3
"""Configure and apply a reviewed specification on its PBI work branch."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from urllib.parse import quote
from uuid import uuid4


CONFIG = "designs/nikomi-udon.json"
CANONICAL = "designs/specifications"
METHODS = ("playwright", "chrome-extension", "manual")
APPROVALS = ("none", "operational", "pr")
DEFAULTS = {"design_approval": "none", "e2e_method": "manual", "screen_items": False, "screenshots": False}
CHECKS = re.compile(r"(?ms)^<!-- e2e:checks -->\n(.*?)^<!-- /e2e:checks -->$")
REVIEW = re.compile(r"(?ms)^<!-- e2e:review -->\n(.*?)^<!-- /e2e:review -->$")
DOCUMENT = re.compile(
    r"(?ms)^<!-- osameru-target: (\{[^\n]+\}) -->\n(.*?)^<!-- /osameru-target -->$"
)


class WorkflowError(Exception):
    pass


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode:
        raise WorkflowError(result.stderr.decode(errors="replace").strip() or "Git failed")
    return result.stdout


def managed_path(root, relative):
    path = PurePosixPath(relative)
    if (
        path.is_absolute()
        or not path.parts
        or relative != path.as_posix()
        or ".." in path.parts
        or "\\" in relative
        or any(ord(character) < 32 for character in relative)
    ):
        raise WorkflowError(f"Invalid relative path: {relative!r}")
    result = root.joinpath(*path.parts)
    try:
        resolved = result.resolve()
    except RuntimeError as error:
        raise WorkflowError(f"Invalid managed path: {result}") from error
    if resolved != result:
        raise WorkflowError(f"Symlink in managed path: {result}")
    return result


def change_directory(root, specified, applying=False):
    branch = git(root, "branch", "--show-current").decode().strip()
    if specified is None:
        if not branch.startswith("feature/"):
            raise WorkflowError("Specify --change specs/<change> or use its feature branch")
        specified = "specs/" + branch[len("feature/"):]
    path = managed_path(root, specified)
    if path.parent != root / "specs":
        raise WorkflowError("Use a single PBI directory under specs/")
    if applying and branch != f"feature/{path.name}":
        raise WorkflowError(f"Switch to feature/{path.name} before applying")
    if not managed_path(path, "nikomi.md").is_file():
        raise WorkflowError(f"Required input missing: {path / 'nikomi.md'}")
    return path


def read(path):
    if not path.is_file():
        raise WorkflowError(f"Required file missing: {path}")
    return path.read_text(encoding="utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def settings(root):
    path = managed_path(root, CONFIG)
    if not path.exists():
        return DEFAULTS.copy()
    value = json.loads(read(path))
    if isinstance(value, dict):
        value.setdefault("design_approval", "none")
    if (
        not isinstance(value, dict)
        or value.keys() != DEFAULTS.keys()
        or value["design_approval"] not in APPROVALS
        or value["e2e_method"] not in METHODS
        or type(value["screen_items"]) is not bool
        or type(value["screenshots"]) is not bool
    ):
        raise WorkflowError(f"Invalid project settings: {path}")
    return value


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        temporary.write_bytes(content)
        if path.exists():
            temporary.chmod(path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def lock(root):
    location = Path(os.fsdecode(git(root, "rev-parse", "--git-path", "osameru.lock").rstrip(b"\n")))
    if not location.is_absolute():
        location = root / location
    try:
        handle = location.open("x", encoding="ascii")
    except FileExistsError as error:
        raise WorkflowError(f"Another workflow operation is active or left a lock: {location}") from error
    try:
        with handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        location.unlink()


def setup(root, args):
    value = settings(root)
    if args.method is None and not (root / CONFIG).exists():
        if not sys.stdin.isatty():
            raise WorkflowError("Choose an E2E method with --method")
        print("1. Playwright\n2. Chrome extension\n3. Manual")
        choice = input("E2E method [1-3]: ").strip()
        if choice not in {"1", "2", "3"}:
            raise WorkflowError("Choose 1, 2, or 3")
        args.method = METHODS[int(choice) - 1]
    if args.method is not None:
        value["e2e_method"] = args.method
    if args.design_approval is not None:
        value["design_approval"] = args.design_approval
    for key in ("screen_items", "screenshots"):
        option = getattr(args, key)
        if option is not None:
            value[key] = option == "on"
    write_file(managed_path(root, CONFIG), (json.dumps(value, indent=2) + "\n").encode())
    print(CONFIG)


def one_block(pattern, text, label):
    matches = list(pattern.finditer(text))
    if len(matches) != 1 or matches[0]["isCrossRepository"]:
        raise WorkflowError(f"Expected one {label} block in e2e.md")
    return matches[0]


def table_cells(line):
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        raise WorkflowError("Every line in the E2E checks block must be a table row")
    cells = []
    start = 1
    backslashes = 0
    for index, character in enumerate(line[1:], start=1):
        if character == "|" and backslashes % 2 == 0:
            cells.append(line[start:index].strip())
            start = index + 1
        backslashes = backslashes + 1 if character == "\\" else 0
    if start != len(line) or len(cells) != 9:
        raise WorkflowError("The E2E checks table must have nine columns")
    return cells


def read_e2e(change):
    path = managed_path(change, "e2e.md")
    text = read(path)
    table = one_block(CHECKS, text, "checks")
    lines = table.group(1).strip().splitlines()
    if len(lines) < 3:
        raise WorkflowError("List at least one required behavior in e2e.md")
    table_cells(lines[0])
    if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in table_cells(lines[1])):
        raise WorkflowError("Invalid E2E checks table separator")
    checks = {}
    for line in lines[2:]:
        cells = table_cells(line)
        key = cells[0]
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key) or key in checks:
            raise WorkflowError(f"Invalid or duplicate behavior ID: {key!r}")
        if any(cell in {"", "-"} for cell in (cells[1], cells[3], cells[4])):
            raise WorkflowError(f"{key}: behavior, steps and expected result are required")
        checks[key] = cells
    return path, text, table, checks


def file_hash(path):
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def test_snapshot(root, change, policy, checks):
    change_name = change.relative_to(root).as_posix()
    exclude = {f"{change_name}/e2e.md", f"{change_name}/oshinagaki.md"}
    generated = (f"{CANONICAL}/", f"{change_name}/evidence/")
    files = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    # Keep snapshots from projects configured before design approval was introduced.
    snapshot_policy = policy.copy()
    if snapshot_policy["design_approval"] == "none":
        del snapshot_policy["design_approval"]
    state = hashlib.sha256(
        json_text([change_name, snapshot_policy, [row[:6] for row in checks.values()]]).encode()
    )
    for raw in sorted(set(files.split(b"\0")) - {b""}):
        name = os.fsdecode(raw)
        if name in exclude or name.startswith(generated):
            continue
        path = root / name
        if path.is_symlink():
            stamp = ["link", os.readlink(path)]
        elif path.resolve() != path:
            raise WorkflowError(f"Symlink enclosing a worktree file: {name}")
        elif path.is_file():
            stamp = ["file", file_hash(path), bool(path.stat().st_mode & 0o111)]
        elif (path / ".git").exists():
            stamp = ["submodule", git(path, "rev-parse", "HEAD").decode().strip()]
            if git(path, "status", "--porcelain"):
                raise WorkflowError(f"Commit or clean changes in submodule before testing: {name}")
        else:
            continue
        state.update(repr((name, stamp)).encode("utf-8", errors="backslashreplace"))
        state.update(b"\0")
    return state.hexdigest()


def result_digest(change, policy, checks, run_id, report):
    evidence = {}
    problems = []
    for key, row in checks.items():
        if row[7] != "OK" or row[6] in {"", "-"}:
            problems.append(f"{key}: expected an observed result and OK")
        links = re.findall(r"\]\((evidence/[^()]+)\)", row[8])
        if policy["screenshots"] and row[5] not in {"", "-"}:
            image_types = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}
            if not any(PurePosixPath(link).suffix.lower() in image_types for link in links):
                problems.append(f"{key}: link the requested screenshots under evidence/")
        for link in links:
            if not link.startswith(f"evidence/{run_id}/"):
                problems.append(f"{key}: evidence must come from the current run")
                continue
            path = managed_path(change, link)
            if path.is_file():
                evidence[link] = file_hash(path)
            else:
                problems.append(f"{key}: evidence file missing: {link}")
    if problems:
        raise WorkflowError("\n".join(problems))
    return digest(json_text([report, evidence]).encode())


def review_record(run, receipt=None):
    marker = f"<!-- e2e-run: {json_text(run)} -->\n"
    if receipt is None:
        return "-\n" + marker
    reviewer = re.sub(r"([\\`*_{}\[\]()#+.!|<>])", r"\\\1", receipt["reviewer"])
    return f"- {reviewer} ({receipt['method']})\n{marker}<!-- e2e-receipt: {json_text(receipt)} -->\n"


def read_run(review):
    markers = re.findall(r"(?m)^<!-- e2e-run: (\{[^\n]+\}) -->$", review)
    if len(markers) != 1:
        raise WorkflowError("Start a run with start-e2e before recording confirmation")
    run = json.loads(markers[0])
    if not isinstance(run, dict) or set(run) != {"id", "snapshot"} or not all(
        isinstance(run[key], str) and re.fullmatch(pattern, run[key])
        for key, pattern in (("id", r"[0-9a-f]{32}"), ("snapshot", r"[0-9a-f]{64}"))
    ):
        raise WorkflowError("Invalid E2E run record")
    return run


def start_e2e(root, change, policy):
    path, text, table, checks = read_e2e(change)
    one_block(REVIEW, text, "review")
    run = {"id": uuid4().hex, "snapshot": test_snapshot(root, change, policy, checks)}
    header = table.group(1).strip().splitlines()[:2]
    rows = ["| " + " | ".join(row[:6] + ["-", "-", "-"]) + " |" for row in checks.values()]
    updated = text[:table.start(1)] + "\n".join(header + rows) + "\n" + text[table.end(1):]
    updated = REVIEW.sub(
        lambda _: f"<!-- e2e:review -->\n{review_record(run)}<!-- /e2e:review -->", updated, count=1
    )
    write_file(path, updated.encode())
    print(run["id"])


def require_current_run(root, change, policy, checks, review, run_id):
    run = read_run(review)
    if run_id != run["id"]:
        raise WorkflowError("The run ID does not match the current E2E run")
    if run["snapshot"] != test_snapshot(root, change, policy, checks):
        raise WorkflowError("The tested worktree, test definition or project settings have changed")
    return run


def review_e2e(root, change, policy, run_id, reviewer):
    path, text, _, checks = read_e2e(change)
    block = one_block(REVIEW, text, "review")
    run = require_current_run(root, change, policy, checks, block.group(1), run_id)
    if not reviewer.strip() or any(ord(character) < 32 for character in reviewer) or "-->" in reviewer:
        raise WorkflowError("Provide the name of the person who confirmed the execution and results")
    receipt = {
        "run_id": run_id,
        "method": policy["e2e_method"],
        "results": result_digest(change, policy, checks, run_id, text[:block.start()] + text[block.end():]),
        "reviewer": reviewer,
    }
    replacement = f"<!-- e2e:review -->\n{review_record(run, receipt)}<!-- /e2e:review -->"
    updated = text[:block.start()] + replacement + text[block.end():]
    write_file(path, updated.encode())
    print(path.relative_to(root))


def verify_e2e(root, change, policy):
    _, text, _, checks = read_e2e(change)
    block = one_block(REVIEW, text, "review")
    review = block.group(1)
    run = read_run(review)
    receipts = re.findall(r"(?m)^<!-- e2e-receipt: (\{[^\n]+\}) -->$", review)
    if len(receipts) != 1:
        raise WorkflowError("Confirmation of the E2E execution and results is missing")
    results = result_digest(change, policy, checks, run["id"], text[:block.start()] + text[block.end():])
    value = json.loads(receipts[0])
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("reviewer"), str)
        or not value["reviewer"].strip()
        or value.get("run_id") != run["id"]
        or run["snapshot"] != test_snapshot(root, change, policy, checks)
        or value.get("results") != results
        or value.get("method") != policy["e2e_method"]
        or review != review_record(run, value)
    ):
        raise WorkflowError("E2E confirmation does not match the current inputs or recorded results")


def document_path(root, name):
    path = managed_path(root / CANONICAL, name)
    if path.suffix != ".md" or path.name.endswith(".history.md"):
        raise WorkflowError(f"Use a Markdown specification path under {CANONICAL}: {name}")
    return path


def base_stamp(path):
    return file_hash(path) if path.exists() else "new"


def documents(root, change, policy):
    sources = [("shitagaki.md", False)]
    draft = read(managed_path(change, "shitagaki.md"))
    if policy["screen_items"]:
        applicability = re.findall(r"(?m)^<!-- screen-items: (applicable|not-applicable) -->$", draft)
        if len(applicability) != 1:
            raise WorkflowError("Record whether screen item definitions apply in shitagaki.md")
        if applicability[0] == "applicable":
            sources.append(("screen-items.md", True))
    seen = set()
    for filename, screen in sources:
        content = read(managed_path(change, filename))
        blocks = list(DOCUMENT.finditer(content))
        if (
            not blocks
            or len(blocks) != content.count("<!-- osameru-target:")
            or len(blocks) != content.count("<!-- /osameru-target -->")
        ):
            raise WorkflowError(f"Invalid or missing specification blocks in {filename}")
        for block in blocks:
            item = json.loads(block.group(1))
            if not isinstance(item, dict) or set(item) != {"path", "base"}:
                raise WorkflowError(f"Expected path and base in {filename}")
            name, base = item["path"], item["base"]
            body = block.group(2).strip()
            if (
                not isinstance(name, str)
                or not isinstance(base, str)
                or not re.fullmatch(r"new|[0-9a-f]{64}", base)
                or not body.startswith("# ")
                or screen != name.endswith(".screen-items.md")
                or name in seen
            ):
                raise WorkflowError(f"Invalid, empty or duplicate specification in {filename}: {item}")
            seen.add(name)
            yield document_path(root, name), base, (body + "\n").encode()


def history_text(path, change, current, reason):
    identifier = change.name
    mark = f"<!-- osameru-change: {identifier} -->"
    end = "<!-- /osameru-change -->"
    old = current.decode("utf-8") if current is not None else f"# {path.stem}\n"
    pattern = rf"(?m)^{re.escape(mark)}\n(?:(?!<!-- osameru-change: )[^\n]*\n)*?^{re.escape(end)}$"
    existing = re.search(pattern, old)
    if old.count(mark) > 1 or (mark in old and existing is None):
        raise WorkflowError(f"Invalid history for {identifier}: {path}")
    if reason is None and existing is None:
        raise WorkflowError("Provide --reason with the change reason")
    if reason is None:
        return old.encode()
    if not reason.strip() or any(ord(character) < 32 for character in reason):
        raise WorkflowError("Use a non-empty, single-line change reason")
    references = []
    for filename in ("nikomi.md", "e2e.md"):
        relative = os.path.relpath(change / filename, path.parent)
        references.append(f"[{filename}]({quote(Path(relative).as_posix())})")
    entry = f"{mark}\n\n## {identifier}\n\n{reason}\n\n{' · '.join(references)}\n\n{end}"
    if existing:
        result = old[:existing.start()] + entry + old[existing.end():]
    else:
        result = old.rstrip() + "\n\n" + entry + "\n"
    return result.encode()


def apply_documents(root, change, policy, reason):
    verify_e2e(root, change, policy)
    updates = {}
    for path, base, content in documents(root, change, policy):
        history = managed_path(path.parent, path.stem + ".history.md")
        prior = path.read_bytes() if path.exists() else None
        previous_history = history.read_bytes() if history.exists() else None
        already_applied = prior == content and previous_history is not None and (
            f"<!-- osameru-change: {change.name} -->".encode() in previous_history
        )
        if not already_applied and (digest(prior) if prior is not None else "new") != base:
            raise WorkflowError(f"Base specification changed: {path.relative_to(root)}")
        updates[history] = (previous_history, history_text(history, change, previous_history, reason))
        updates[path] = (prior, content)

    written = []
    try:
        for path, (previous, content) in updates.items():
            if content != previous:
                write_file(path, content)
                written.append((path, previous))
    except OSError:
        for path, previous in reversed(written):
            if previous is None:
                path.unlink()
            else:
                write_file(path, previous)
        raise
    for path, _ in written:
        print(path.relative_to(root))
    if not written:
        print("Already applied")


def gh_json(root, *args):
    result = subprocess.run(["gh", *args], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise WorkflowError(result.stderr.strip() or "Unable to read the design PR")
    return json.loads(result.stdout)


def design_blob(root, commit, draft_path):
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit):
        raise WorkflowError("Unable to identify the design revision")
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit}:{draft_path}"],
        cwd=root, capture_output=True, text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    # Review commits can be absent from shallow or squash-merged checkouts.
    endpoint = "repos/{owner}/{repo}/contents/" + quote(draft_path) + "?ref=" + commit
    return gh_json(root, "api", endpoint).get("sha")


def check_design_review(root, change, pr_number):
    draft = managed_path(change, "shitagaki.md")
    if not draft.is_file():
        raise WorkflowError(f"Design draft missing: {draft}")
    if pr_number is None:
        branch = f"feature/{change.name}"
        matches = gh_json(root, "pr", "list", "--head", branch, "--state", "open",
                          "--limit", "2", "--json", "number,isCrossRepository")
        if len(matches) != 1 or matches[0]["isCrossRepository"]:
            raise WorkflowError(f"Unable to identify one same-repository PR for {branch}. Specify the design PR with --pr.")
        pr_number = matches[0]["number"]
    review = gh_json(root, "pr", "view", str(pr_number), "--json",
                     "url,state,files,headRefOid,reviewDecision,reviews,latestReviews")
    draft_path = draft.relative_to(root).as_posix()
    if not any(entry["path"] == draft_path for entry in review["files"]):
        raise WorkflowError(f"Unable to confirm {draft_path} in {review['url']}")
    decision = review["reviewDecision"]
    if review["state"] not in ("OPEN", "MERGED") or decision not in ("APPROVED", "", None):
        raise WorkflowError(f"{review['url']}: {review['state']}, {decision}")
    latest = review["latestReviews"]
    if not decision and (len(latest) >= 100 or any(r["state"] == "CHANGES_REQUESTED" for r in latest)):
        raise WorkflowError(f"Unable to establish approval for {review['url']}")
    local_blob = git(root, "hash-object", "--", draft_path).decode().strip()
    head = review["headRefOid"]
    if design_blob(root, head, draft_path) != local_blob:
        raise WorkflowError(f"The local draft differs from {review['url']}")
    # latestReviews identifies active approvals. reviews supplies their commits.
    approvals = {(r["author"]["login"], r["submittedAt"]) for r in latest if r["state"] == "APPROVED"}
    for entry in reversed(review["reviews"]):
        if entry["state"] == "APPROVED" and (entry["author"]["login"], entry["submittedAt"]) in approvals:
            commit = (entry.get("commit") or {}).get("oid")
            if commit and (commit == head or design_blob(root, commit, draft_path) == local_blob):
                print(f"Design review approved: {review['url']}")
                return
    raise WorkflowError(f"No current approval confirmed for this design revision: {review['url']}")


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", help="PBI directory relative to the repository root")
    commands = parser.add_subparsers(dest="command", required=True)
    configure = commands.add_parser("setup")
    configure.add_argument("--design-approval", choices=APPROVALS)
    configure.add_argument("--method", choices=METHODS)
    configure.add_argument("--screen-items", choices=("on", "off"))
    configure.add_argument("--screenshots", choices=("on", "off"))
    commands.add_parser("settings")
    design = commands.add_parser("check-design-review")
    design.add_argument("--pr", type=int, help="Design PR number in the target repository")
    commands.add_parser("start-e2e")
    check_run = commands.add_parser("check-e2e-run")
    check_run.add_argument("--tested", required=True)
    review = commands.add_parser("review-e2e")
    review.add_argument("--tested", required=True)
    review.add_argument("--reviewer", required=True)
    commands.add_parser("verify-e2e")
    base = commands.add_parser("base")
    base.add_argument("path")
    apply = commands.add_parser("apply")
    apply.add_argument("--reason")
    return parser


def main():
    args = make_parser().parse_args()
    try:
        root = Path(os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel").rstrip(b"\n"))).resolve()
        if args.command == "setup":
            with lock(root):
                setup(root, args)
            return 0
        if args.command == "settings":
            print(json_text(settings(root)))
            return 0
        if args.command == "check-design-review":
            check_design_review(root, change_directory(root, args.change), args.pr)
            return 0
        if args.command == "base":
            print(base_stamp(document_path(root, args.path)))
            return 0
        with lock(root):
            policy = settings(root)
            change = change_directory(root, args.change, applying=args.command == "apply")
            if args.command == "start-e2e":
                start_e2e(root, change, policy)
            elif args.command == "check-e2e-run":
                _, text, _, checks = read_e2e(change)
                review = one_block(REVIEW, text, "review").group(1)
                require_current_run(root, change, policy, checks, review, args.tested)
                print("E2E run matches current inputs")
            elif args.command == "review-e2e":
                review_e2e(root, change, policy, args.tested, args.reviewer)
            elif args.command == "verify-e2e":
                verify_e2e(root, change, policy)
                print("E2E results confirmed")
            elif args.command == "apply":
                apply_documents(root, change, policy, args.reason)
    except (WorkflowError, OSError, ValueError) as error:
        print(f"osameru: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
