"""Install a complete language edition in a Git worktree."""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from importlib.metadata import version
from pathlib import Path

from .environment import prepare

AGENTS = {"codex": ".agents/skills", "claude": ".claude/skills"}
LEGACY_SKILLS = "ajimi dandori nikomu okosu osameru saguru shikomu shitagaki torikomu yonabe".split()
SKILLS = sorted([*LEGACY_SKILLS, "koromogae"])
RECORD = "designs/nikomi-udon-install.json"
CONFIG = "designs/nikomi-udon.json"
DESIGN_TEMPLATE = "designs/basic-design.template.md"
DESIGN_POLICY = "designs/basic-design-writing.md"
DESIGN_ASSETS = "shitagaki/assets"
TARGETS = {f"{folder}/{name}" for folder in AGENTS.values() for name in SKILLS}
METHODS = ("playwright", "agent-browser", "chrome-extension", "manual")


def choose(prompt, choices, default=None):
    while True:
        print(prompt)
        for i, value in enumerate(choices, 1):
            print(f"  {i}. {value}")
        answer = input(f"[{default or '1-' + str(len(choices))}] ").strip()
        if not answer and default:
            return default
        if answer in choices:
            return answer
        if answer in map(str, range(1, len(choices) + 1)):
            return choices[int(answer) - 1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe(root, relative):
    path = root / relative
    if any(p.is_symlink() for p in [path, *path.parents]) or path.resolve() != path:
        raise ValueError(f"Linked installation path: {relative}")
    return path


def inventory(directory):
    result = {}
    pending = [directory]
    while pending:
        parent = pending.pop()
        children = list(parent.iterdir())
        if not children and parent != directory:
            result[parent.relative_to(directory).as_posix()] = "empty directory"
        for path in children:
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise ValueError(f"Unexpected file: {path}")
            if path.is_dir():
                pending.append(path)
            else:
                result[path.relative_to(directory).as_posix()] = file_stamp(path)
    return result


def file_stamp(path, normalize_crlf=False):
    if not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")
    data = path.read_bytes()
    if normalize_crlf:
        data = data.replace(b"\r\n", b"\n")
    digest = hashlib.sha256(data).hexdigest()
    return "executable:" + digest if path.stat().st_mode & 0o111 else digest


def stamp(path):
    return inventory(path) if path.is_dir() else file_stamp(path)


def distribution_files(source):
    files = {}
    for skill in SKILLS:
        folder = source / skill
        if not (folder / "SKILL.md").is_file():
            raise ValueError(f"Incomplete distribution: {skill}/SKILL.md")
        files[skill] = {name: digest for name, digest in inventory(folder).items()
                        if "__pycache__" not in Path(name).parts}
        for name in files[skill]:
            page = folder / name
            # Asset templates also link to documents created later in the user's project.
            if page.suffix != ".md" or "assets" in Path(name).parts:
                continue
            for link in re.findall(r"\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
                relative = link.partition("#")[0]
                if relative and "://" not in relative:
                    target = (page.parent / relative).resolve()
                    if source not in target.parents or not target.exists():
                        raise ValueError(f"Incomplete distribution: {skill}/{name} references {relative}")
    return files


def git(*args):
    return subprocess.check_output(["git", *args], text=True).rstrip("\n")


def clean_crlf_paths(root, directories):
    paths = ["--", *sorted(directories)]
    output = subprocess.check_output(["git", "ls-files", "--eol", "-z", *paths], cwd=root)
    converted = set()
    for entry in output.split(b"\0"):
        info, _, name = entry.partition(b"\t")
        if info.split()[:2] == [b"i/lf", b"w/crlf"]:
            converted.add(os.fsdecode(name))
    if converted:
        dirty = subprocess.check_output(
            ["git", "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", *paths], cwd=root)
        converted.difference_update(os.fsdecode(name) for name in dirty.split(b"\0"))
    return converted


def report_ignored_files(root, directories):
    result = subprocess.run(
        ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z",
         "--", CONFIG, RECORD, DESIGN_TEMPLATE, DESIGN_POLICY, *sorted(directories)],
        cwd=root, stdout=subprocess.PIPE,
    )
    if result.returncode:
        print("Check the project's Git ignore rules before sharing this installation.")
    elif result.stdout:
        ignored = os.fsdecode(result.stdout).rstrip("\0").split("\0")
        print(f"Git ignores {len(ignored)} installed file(s) / Git の共有対象外です。"
              f"\n  git check-ignore -v -- {ignored[0]}"
              "\nReview the ignore rules before sharing the skills, settings and installation record.")


@contextmanager
def locked(path):
    import fcntl
    with path.open("a+b") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Another installation is active")
        yield


def recover(root, work):
    if not work.exists():
        return
    journal = work / "pending.json"
    if journal.exists():
        entries = json.loads(journal.read_text())
        if not isinstance(entries, list) or not entries:
            raise ValueError("Invalid installation journal")
        for entry in entries:
            if (not isinstance(entry, list) or len(entry) not in (2, 3)
                    or entry[0] not in TARGETS | {CONFIG, RECORD, DESIGN_TEMPLATE, DESIGN_POLICY}
                    or type(entry[1]) is not bool):
                raise ValueError("Invalid installation journal")
        for entry in reversed(entries):
            relative, existed = entry[:2]
            target = safe(root, relative)
            backup = work / "old" / relative
            staged = work / "new" / relative
            if existed and not backup.exists():
                continue
            if not existed and staged.exists():
                continue
            if target.exists():
                # A user may have edited the new tree after an interrupted update.
                # Older journals have no stamp, so leave that tree for manual backup.
                if staged.exists() or len(entry) < 3 or stamp(target) != entry[2]:
                    raise ValueError(f"Move {relative} to a backup and rerun to finish recovery.")
                target.replace(staged)
            if existed:
                target.parent.mkdir(parents=True, exist_ok=True)
                backup.replace(target)
        journal.unlink()
    shutil.rmtree(work)


def commit(root, work, entries, previous=None):
    journal = work / "pending.json"
    write_json(work / "journal.tmp", [
        (relative, existed, stamp(work / "new" / relative)) for relative, existed in entries
    ])
    (work / "journal.tmp").replace(journal)
    for relative, existed in entries:
        target = safe(root, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not existed and target.exists():
            raise ValueError(f"New file appeared during installation: {relative}")
        if existed:
            backup = work / "old" / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            target.replace(backup)
            if previous and relative in previous and stamp(backup) != previous[relative]:
                raise ValueError(f"File changed during setup. Save local edits and retry: {relative}")
        (work / "new" / relative).replace(target)
    journal.unlink()


def install(root, work, action):
    release = version("spec-nikomi-udon")
    record = safe(root, RECORD)
    previous = {}
    if record.exists():
        previous[RECORD] = file_stamp(record)
        old = json.loads(record.read_text(encoding="utf-8"))
    else:
        old = None
    if old is None and action == "update":
        raise ValueError("Run init first")
    if record.exists() and (not isinstance(old, dict) or set(old) != {"agents", "language", "version", "files"}):
        raise ValueError("Invalid installation record")
    agents = set()
    if old is not None:
        agents = set(old["agents"])
        if not agents or not agents <= AGENTS.keys() or old["language"] not in ("english", "japanese"):
            raise ValueError("Invalid installation record")
        if action == "init" and old["version"] != release:
            raise ValueError("Run update with the desired release tag")
        language = old["language"]
        expected = {f"{AGENTS[a]}/{s}" for a in agents for s in SKILLS}
        legacy = {f"{AGENTS[a]}/{s}" for a in agents for s in LEGACY_SKILLS}
        recorded_targets = set(old["files"])
        if recorded_targets == legacy and action == "update":
            expected = legacy
        elif recorded_targets != expected:
            if recorded_targets == legacy:
                raise ValueError("Run update to add the basic design format and koromogae")
            raise ValueError("Incomplete installation record")
        converted = clean_crlf_paths(root, expected)
        conflicts = []
        for relative in sorted(expected):
            target = safe(root, relative)
            actual = inventory(target) if target.is_dir() else {}
            # The transaction must compare the actual bytes again after moving its backup.
            previous[relative] = actual
            recorded = old["files"][relative]
            if not isinstance(recorded, dict) or "SKILL.md" not in recorded:
                raise ValueError(f"Invalid inventory: {relative}")
            for name in sorted(actual.keys() | recorded.keys()):
                if actual.get(name) == recorded.get(name):
                    continue
                path = f"{relative}/{name}"
                if (name in actual and path in converted
                        and file_stamp(target / name, normalize_crlf=True) == recorded.get(name)):
                    continue
                conflicts.append(path)
        if conflicts:
            raise ValueError("Save local changes, restore the installed edition and retry:\n" + "\n".join(conflicts))
    else:
        language = choose("Skill language / 言語", ("japanese", "english"))
    if action == "init":
        prompt = "Agent / 導入先" if not agents else "Agent to add or check / 導入先（既存の配置は保持）"
        choice = choose(prompt, ("codex", "claude", "both"),
                        "both" if len(agents) == 2 else next(iter(agents), None))
        agents.update(AGENTS if choice == "both" else [choice])
    source = Path(__file__).resolve().parent / language
    distribution = distribution_files(source)
    files = {}
    entries = []
    stage = work / "new"
    for agent in sorted(agents):
        for skill in SKILLS:
            relative = f"{AGENTS[agent]}/{skill}"
            target = safe(root, relative)
            managed = old is not None and relative in old["files"]
            if target.exists() and not managed:
                raise ValueError(f"Move the existing skill before running init: {relative}")
            files[relative] = distribution[skill]
            if managed and files[relative] == old["files"][relative]:
                continue
            if managed and action == "init":
                raise ValueError(f"Release contents differ for {relative}. Use the installed release or run update.")
            shutil.copytree(source / skill, stage / relative, ignore=shutil.ignore_patterns("__pycache__"))
            entries.append((relative, managed))
    config = safe(root, CONFIG)
    if config.exists():
        if not config.is_file():
            raise ValueError(f"Expected a project settings file: {CONFIG}")
        # Validate using the same reader as the distributed workflow.
        settings = json.loads(subprocess.check_output(
            [sys.executable, str(source / "osameru/scripts/osameru.py"), "settings"], cwd=root, text=True))
    else:
        if old is not None:
            raise ValueError(f"Restore missing project settings before retrying: {CONFIG}")
        settings = dict(e2e_method=choose("E2E method / テスト方式", METHODS),
                        design_approval=choose("Design approval / 設計承認", ("none", "operational", "pr"), "none"),
                        screenshots=choose("Screenshots / 画面キャプチャ", ("off", "on"), "off") == "on",
                        screen_items=choose("Screen item definitions / 画面項目定義書", ("off", "on"), "off") == "on")
        write_json(stage / CONFIG, settings)
        entries.append((CONFIG, False))
    standard_diff = stage_design_format(root, stage, entries, source, old)
    current = dict(version=release, language=language, agents=sorted(agents), files=files)
    if old != current:
        write_json(stage / RECORD, current)
        entries.append((RECORD, old is not None))
    if entries:
        commit(root, work, entries, previous)
    print(f"Installed {release} ({language}): {', '.join(sorted(agents))}")
    if standard_diff:
        print("Standard basic design template changes / 標準書式の変更")
        print(standard_diff, end="")
        print(f"Edit {DESIGN_TEMPLATE} to adopt selected changes.")
    report_ignored_files(root, files)
    if "codex" in agents:
        print("Codex: $nikomu")
    if "claude" in agents:
        print("Claude Code: /nikomu")
    return settings


def stage_design_format(root, stage, entries, source, old):
    template = source / DESIGN_ASSETS / Path(DESIGN_TEMPLATE).name
    policy = source / DESIGN_ASSETS / Path(DESIGN_POLICY).name
    installed = None
    if old:
        agent = sorted(old["agents"])[0]
        installed = root / AGENTS[agent] / DESIGN_ASSETS / template.name
    has_standard = installed is not None and installed.is_file()

    for relative, asset in ((DESIGN_TEMPLATE, template), (DESIGN_POLICY, policy)):
        target = safe(root, relative)
        if target.exists():
            if not target.is_file():
                raise ValueError(f"Expected a project file: {relative}")
            continue
        if relative == DESIGN_TEMPLATE and (has_standard or safe(root, DESIGN_POLICY).exists()):
            raise ValueError(f"Restore the missing project template before retrying: {relative}")
        if has_standard:
            # The next design operation rebuilds missing guidance from the project template.
            continue
        staged = stage / relative
        staged.parent.mkdir(parents=True, exist_ok=True)
        if relative == DESIGN_TEMPLATE:
            shutil.copyfile(asset, staged)
        else:
            digest = subprocess.check_output(
                ["git", "hash-object", "--no-filters", "--", str(template)], cwd=root, text=True
            ).strip()
            staged.write_text(f"<!-- template-blob: {digest} -->\n\n"
                              + asset.read_text(encoding="utf-8"), encoding="utf-8")
        entries.append((relative, False))
    if not has_standard:
        return ""
    return "".join(difflib.unified_diff(
        installed.read_text(encoding="utf-8").splitlines(keepends=True),
        template.read_text(encoding="utf-8").splitlines(keepends=True),
        fromfile="previous standard", tofile="new standard",
    ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("init", "update"))
    action = parser.parse_args().action
    try:
        if os.name != "posix":
            raise ValueError("Use WSL on Windows")
        if not sys.stdin.isatty() and action == "init":
            raise ValueError("Run init in an interactive terminal")
        root = Path(git("rev-parse", "--show-toplevel")).resolve()
        os.chdir(root)
        gitdir = Path(git("rev-parse", "--absolute-git-dir"))
        work = gitdir / "nikomi-install-txn"
        with locked(gitdir / "nikomi-install.lock"):
            recover(root, work)
            work.mkdir()
            try:
                settings = install(root, work, action)
            finally:
                recover(root, work)
            if action == "init":
                if settings["design_approval"] == "pr":
                    print("PR review: connect your project's review integration. "
                          "For GitHub CLI, check gh auth status and repository access.")
                prepare(root, settings["e2e_method"], choose)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, EOFError, KeyboardInterrupt) as error:
        parser.exit(1, f"Installation: {error}\n")
