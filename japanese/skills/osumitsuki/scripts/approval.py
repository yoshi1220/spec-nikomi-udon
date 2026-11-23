#!/usr/bin/env python3
"""Manage specification progress and design approval in a PBI's deliverable index."""

import argparse
from datetime import date
from html import escape
import os
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import urlsplit

SKILLS = Path(__file__).resolve().parents[2]
# Import the installed workflow helpers without changing its managed inventory.
sys.dont_write_bytecode = True
sys.path.insert(0, str(SKILLS / "osameru" / "scripts"))
from osameru import (WorkflowError, change_directory, check_design_review, git,
                     lock, managed_path, settings, validate_plan_binding, write_file)


TITLE = "設計承認"
STATES = {"pending": "承認待ち", "approved": "承認済み", "emergency": "緊急対応"}
DATE, APPROVER, REASON = "承認日", "承認者", "省略理由"
START = "<!-- design-approval -->"
END = "<!-- /design-approval -->"
BLOCK = re.compile(r"^" + START + r"\r?\n(.*?)^" + END + r"(?=\r?$)", re.M | re.S)
INDEX_TEMPLATE = SKILLS / "shitagaki" / "assets" / "oshinagaki.template.md"
SPEC_ROW = re.compile(
    r"^(\|[ \t]*変更仕様[ \t]*\|[^|\r\n]*\|[ \t]*)"
    r"[^|\r\n]*?([ \t]*\|[ \t]*)(?=\r?$)", re.M
)
SPEC_STATUSES = {"pending": "作成中", "confirmed": "作成済み"}


def specification_review(change):
    spec = managed_path(change, "shikomi.md")
    first = spec.read_text(encoding="utf-8-sig").partition("\n")[0]
    return "confirmed" if first == "<!-- shikomi-review: confirmed -->" else "pending"


def specification_row(text, review):
    rows = list(SPEC_ROW.finditer(text))
    if len(rows) != 1:
        raise WorkflowError("Expected one 変更仕様 row in oshinagaki.md")
    row = rows[0]
    return text[:row.start()] + row[1] + SPEC_STATUSES[review] + row[2] + text[row.end():]


def save_index(path, original, updated):
    if updated == original:
        return
    if (path.read_bytes() if path.exists() else None) != original:
        raise WorkflowError("The deliverable index changed. Read the current index and retry.")
    write_file(path, updated)


def sync_specification(change):
    path = managed_path(change, "oshinagaki.md")
    original = path.read_bytes() if path.exists() else None
    text = (INDEX_TEMPLATE.read_bytes() if original is None else original).decode("utf-8")
    review = specification_review(change)
    save_index(path, original, specification_row(text, review).encode("utf-8"))
    return review


def field(value, label):
    if not value or not value.strip() or any(
        unicodedata.category(char) in ("Cc", "Zl", "Zp") for char in value
    ):
        raise WorkflowError(f"Provide {label} on a single line")
    return value.strip()


def approval_date(value):
    value = field(value, "the approval date (YYYY-MM-DD)")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise WorkflowError("Use YYYY-MM-DD for the approval date")
    date.fromisoformat(value)
    return value


def record(text, state, details):
    lines = [START, f"## {TITLE}", "", f"**{STATES[state]}**", ""]
    for label, value in details:
        # Keep user-provided Markdown and HTML in these single-line fields literal.
        value = re.sub(r"([\\`*_\[\]|])", r"\\\1", escape(value, quote=False))
        lines.append(f"- {label}: {value}")
    lines.append(END)
    newline = "\r\n" if "\r\n" in text else "\n"
    return newline.join(lines)


def current_record(text):
    if START not in text and END not in text:
        return None, "uninitialized"
    block = BLOCK.search(text)
    if text.count(START) != 1 or text.count(END) != 1 or block is None:
        raise WorkflowError("Repair the incomplete or duplicate design approval block in oshinagaki.md")
    lines = block[1].splitlines()
    labels = {f"**{label}**": key for key, label in STATES.items()}
    states = [labels[line] for line in lines if line in labels]
    if len(states) != 1:
        raise WorkflowError("Expected one design approval state in oshinagaki.md")
    state = states[0]
    required = {"pending": (), "approved": (DATE, APPROVER), "emergency": (REASON,)}[state]
    for label in required:
        prefix = f"- {label}: "
        values = [line[len(prefix):] for line in lines if line.startswith(prefix)]
        if len(values) != 1 or not values[0].strip():
            raise WorkflowError(f"Restore the {label} in the {state} record in oshinagaki.md")
        if label == DATE:
            approval_date(values[0])
    return block, state


def set_plan_state(change, *, ready):
    path = managed_path(change, "dandori.md")
    if not ready and not path.exists():
        return
    content = path.read_bytes()
    first = content.partition(b"\n")[0]
    marker = first.rstrip(b"\r")
    pending = b"<!-- dandori-plan: pending -->"
    executable = b"<!-- dandori-plan: ready -->"
    target = executable if ready else pending
    if ready and (marker not in (pending, executable) or any(
        line.startswith(b"<!-- dandori-plan:") for line in content.splitlines()[1:]
    )):
        raise WorkflowError("Expected a single plan status marker on the first line of dandori.md")
    if marker == target:
        return
    if marker in (pending, executable):
        updated = target + content[len(marker):]
    else:
        # Keep the body of a legacy plan when putting it on hold.
        newline = b"\r\n" if first.endswith(b"\r") else b"\n"
        updated = pending + newline + content
    write_file(path, updated)


def approval_details(root, change, mode, args):
    draft = managed_path(change, "shitagaki.md")
    original_draft = draft.read_bytes() if draft.is_file() else b""
    if not original_draft.decode("utf-8-sig").strip():
        raise WorkflowError("A non-empty design draft is required to record its approval")
    validate_plan_binding(root, change)
    day, reviewer = args.date, args.approver
    url = None
    if args.action == "approve" and mode == "pr":
        if args.verified_pr:
            url, head_blob, reviewed_blob = args.verified_pr
            parts = urlsplit(field(url, "the verified PR URL"))
            if parts.scheme != "https" or not parts.hostname or parts.username is not None:
                raise WorkflowError("Use the HTTPS review URL without credentials")
            local_blob = git(root, "hash-object", "--", str(draft)).decode().strip()
            if head_blob != local_blob or reviewed_blob != local_blob:
                raise WorkflowError("The local design must match both the PR head and the approved design")
            plan = managed_path(change, "structure-plan.json")
            if plan.is_file():
                plan_blob = git(root, "hash-object", "--", str(plan)).decode().strip()
                if args.verified_plan != [plan_blob, plan_blob]:
                    raise WorkflowError("Provide matching --verified-plan blob IDs from the PR head and approved revision")
        else:
            reviewer, day, url = check_design_review(root, change, args.pr, reviewer, day)
    elif args.action == "approve" and (args.pr is not None or args.verified_pr):
        raise WorkflowError("PR options require design_approval=pr")
    details = [(DATE, approval_date(day)), (APPROVER, field(reviewer, "the approver"))]
    if url:
        details.append(("PR", url))
    if draft.read_bytes() != original_draft:
        raise WorkflowError("The design changed while checking its approval. Review the current draft and retry.")
    validate_plan_binding(root, change)
    return details


def update_index(root, change, mode, args):
    path = managed_path(change, "oshinagaki.md")
    exists = path.is_file()
    if args.action in ("status", "finish-plan"):
        state = "off"
        if mode != "none":
            state = current_record(path.read_bytes().decode("utf-8") if exists else "")[1]
        if args.action == "status":
            return state
        if state not in ("off", "approved", "emergency"):
            raise WorkflowError("The design needs approval before finishing the plan")
        set_plan_state(change, ready=True)
        return "ready"

    if mode == "none":
        if args.action in ("approve", "emergency", "migrate"):
            raise WorkflowError("Design approval is off for this project")
        if not exists and args.action in ("init", "redraft"):
            sync_specification(change)
        # Invalidate an older approval if the draft is redone while approval is off.
        if args.action != "redraft" or not exists:
            return "off"

    original = path.read_bytes() if exists else None
    if original is None:
        text = specification_row(INDEX_TEMPLATE.read_text(encoding="utf-8"), specification_review(change))
    else:
        text = original.decode("utf-8")
    block, state = current_record(text)
    if mode == "none" and block is None:
        return "off"
    # Suspend the old plan before writing an index that requires replanning.
    if args.action == "redraft" or (args.action == "init" and state in ("uninitialized", "pending")):
        set_plan_state(change, ready=False)
    if mode == "none" and state != "approved":
        return "off"
    if args.action == "init" and block:
        return state
    if args.action == "migrate" and block:
        raise WorkflowError("The index already has an approval record")
    if state == "emergency" or (state == "approved" and args.action == "approve"):
        return state

    details = []
    if args.action == "emergency":
        state = "emergency"
        details.append((REASON, field(args.reason, "the reason for the exception")))
    elif args.action in ("approve", "migrate"):
        details = approval_details(root, change, mode, args)
        state = "approved"
    else:
        state = "pending"

    replacement = record(text, state, details)
    if block:
        updated = text[:block.start()] + replacement + text[block.end():]
    else:
        newline = "\r\n" if "\r\n" in text else "\n"
        separator = newline if text.endswith("\n") else newline * 2
        updated = text + separator + replacement + newline
    save_index(path, original, updated.encode("utf-8"))
    return "off" if mode == "none" else state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", help="PBI directory relative to the repository root")
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ("status", "init", "redraft", "finish-plan", "sync-spec"):
        actions.add_parser(name)
    emergency = actions.add_parser("emergency")
    emergency.add_argument("--reason", required=True)
    approve = actions.add_parser("approve")
    pr = approve.add_mutually_exclusive_group()
    pr.add_argument("--pr", type=int)
    pr.add_argument("--verified-pr", nargs=3, metavar=("URL", "HEAD_BLOB", "REVIEWED_BLOB"),
                    help="Review URL and design file blob IDs obtained from the host PR integration")
    approve.add_argument("--verified-plan", nargs=2, metavar=("HEAD_BLOB", "REVIEWED_BLOB"),
                         help="Structure plan blob IDs for a design checked with --verified-pr")
    migrate = actions.add_parser("migrate", help="Import a verified approval from a legacy PBI")
    for action in (approve, migrate):
        action.add_argument("--date")
        action.add_argument("--approver")
    args = parser.parse_args()
    if getattr(args, "verified_plan", None) and not args.verified_pr:
        parser.error("--verified-plan requires --verified-pr")
    try:
        root = Path(os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel").rstrip(b"\n"))).resolve()
        with lock(root):
            change = change_directory(root, args.change)
            if args.action == "sync-spec":
                print(sync_specification(change))
            else:
                print(update_index(root, change, settings(root)["design_approval"], args))
    except (WorkflowError, OSError, ValueError) as error:
        parser.exit(1, f"osumitsuki: {error}\n")


if __name__ == "__main__":
    main()
