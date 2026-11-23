"""Maintain canonical GraphML, stable Markdown identities and revision history."""
import base64
import copy
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from urllib.parse import quote
import xml.etree.ElementTree as ET

from osameru import CANONICAL, git, journal, managed_path, write_file

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plan-implementation/scripts"))
from work_graph import apply_delta, decode_graph, distinct_fields, graph_bytes, tag

GRAPH = "structure/current.graphml"
INDEX = "structure/index.json"
TREE = "structure/hierarchy.md"
EVENTS = "history/changes.graphml"
ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}\Z")
MARKER = re.compile(r" {0,3}<!-- spec-node: ([A-Za-z0-9_-]+) -->[ \t]*")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*$")
RELATIONS = {"contains", "calls", "transfers", "depends", "references"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value), "Invalid identifier: %r" % value)
    return value


def packed(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def checksum(data):
    return hashlib.sha256(data).hexdigest() if data is not None else "new"


def contents(path):
    return path.read_bytes() if path.exists() else None


def load_json(path, default):
    return json.loads(path.read_bytes(), object_pairs_hook=distinct_fields) if path.exists() else default


def graph_at(folder, name):
    path = managed_path(folder, name)
    if not path.exists():
        return {}, {}
    # A duplicate ID would otherwise silently erase a previous element when decoded.
    try:
        root = ET.fromstring(path.read_bytes())
        nodes, edges = decode_graph(root)
    except (ET.ParseError, KeyError, ValueError) as error:
        raise ValueError("Invalid GraphML: " + name) from error
    graph = root.find(tag("graph"))
    ids = [item.attrib["id"] for item in graph if item.tag in (tag("node"), tag("edge"))]
    require(len(ids) == len(set(ids)) == len(nodes) + len(edges), "Duplicate GraphML ID: " + name)
    apply_delta(nodes, edges, {})
    return nodes, edges


def stamp(folder):
    values = []
    for name in (GRAPH, INDEX, EVENTS):
        data = contents(managed_path(folder, name))
        values.append(checksum(data.replace(b"\r\n", b"\n") if data is not None else None))
    return "new" if values == ["new"] * 3 else checksum(packed(values))


def body_path(folder, name):
    path = managed_path(folder, name)
    require(path.relative_to(folder).parts[0].casefold() not in {"structure", "history", ".git"}
            and path.suffix == ".md" and not path.name.endswith(".history.md"),
            "Expected a current Markdown specification: " + name)
    return path


def sections(data, path):
    """Return the marked ATX sections, ignoring sample markup in code blocks."""
    lines = data.decode("utf-8").replace("\r\n", "\n").splitlines(keepends=True)
    body_start = 0
    if lines and lines[0].rstrip() == "---":
        body_start = next((i + 1 for i in range(1, len(lines)) if lines[i].rstrip() in ("---", "...")), 0)
    active = []
    result = {}
    fence = ""
    for i in range(body_start, len(lines)):
        line = lines[i]
        clean = line.rstrip("\r\n")
        delimiter = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", clean)
        heading = marker = None
        if fence:
            if delimiter and delimiter[1].startswith(fence) and not delimiter[2].strip():
                fence = ""
        elif delimiter:
            fence = delimiter[1]
        else:
            # Only marked indented headings introduce a new boundary. Keep other
            # indented text in its original section for history and archive checks.
            if clean.startswith("#") or (i + 1 < len(lines) and MARKER.fullmatch(lines[i + 1].rstrip("\r\n"))):
                heading = HEADING.fullmatch(clean)
            if re.match(r"^ {0,3}<!-- spec-node:", clean):
                marker = MARKER.fullmatch(clean)
                require(marker, "Malformed node marker in " + path)
        if heading:
            depth = len(heading[1])
            while active and active[-1][0] >= depth:
                active.pop()
        if marker:
            key = identifier(marker[1])
            require(key not in result, "Duplicate node marker: " + key)
            previous = HEADING.fullmatch(lines[i-1].rstrip("\r\n")) if i > body_start else None
            require(previous or i == body_start, "Place marker immediately after its heading or front matter: " + key)
            depth = len(previous[1]) if previous else 0
            title = previous[2] if previous else Path(path).stem
            start = i - 1 if previous else i
            fragment = lines[:start] if body_start and not result and not any(
                part.strip() for part in lines[body_start:start]) else []
            if previous:
                # That heading belongs to the new marked section.
                if active:
                    active[-1][1].pop()
                fragment.append(lines[i-1])
            active.append((depth, fragment))
            result[key] = (title, fragment)
        if active:
            active[-1][1].append(line)
    return {k: (v[0], "".join(v[1])) for k, v in result.items()}


def inventory(folder, overlay, nodes):
    paths = set(overlay)
    for location, dirs, files in os.walk(folder):
        directory = Path(location)
        if directory == folder:
            dirs[:] = [d for d in dirs if d not in {"structure", "history", ".git"}]
        for name in files:
            if name.endswith(".md") and not name.endswith(".history.md"):
                paths.add((directory / name).relative_to(folder).as_posix())
    index = {}
    for name in sorted(paths):
        path = body_path(folder, name)
        data = overlay[name] if name in overlay else contents(path)
        if data is None or name.endswith(".screen-items.md"):
            continue
        for key, (heading, body) in sections(data, name).items():
            require(key not in index, "Node marker occurs in multiple sections: " + key)
            index[key] = {"path": name, "heading": heading, "sha256": checksum(body.encode())}
    for key, location in index.items():
        default = str(Path(location["path"]).with_suffix(".screen-items.md"))
        screen = nodes.get(key, {}).get("screen", default)
        require(screen.endswith(".screen-items.md"), "Invalid screen item definition: " + screen)
        screen_path = body_path(folder, screen)
        # Use the spelling in the inventory so an index also works on a case-sensitive checkout.
        data = None
        if screen in paths:
            data = overlay[screen] if screen in overlay else contents(screen_path)
        require(data is not None or "screen" not in nodes.get(key, {}),
                "Missing explicit screen item definition: " + screen)
        if data is not None:
            location.update(screen=screen, screen_sha256=checksum(data.replace(b"\r\n", b"\n")))
    return index


def node_notes(folder, nodes):
    notes = {}
    for key in nodes:
        path = managed_path(folder, "structure/notes/" + identifier(key) + ".md")
        if path.is_file():
            notes[key] = path.read_text(encoding="utf-8")
    return notes


def render(nodes, edges, index, notes):
    children = {key: [] for key in nodes}
    parents = {}
    for key, edge in edges.items():
        require(edge["kind"] in RELATIONS, "Unknown relation: " + key)
        if edge["kind"] == "contains":
            parent, child = edge["source"], edge["target"]
            require(child not in parents, "Multiple parents: " + child)
            parents[child] = parent
            children[parent].append(child)
    require(not (index.keys() - nodes.keys()), "Markdown contains IDs missing from current GraphML: "
            + ", ".join(sorted(index.keys() - nodes.keys())))
    require(len({key.casefold() for key in nodes}) == len(nodes), "Node IDs differ only by case")
    lines = ["# Specification hierarchy", ""]
    visited = set()
    stack = [(key, 0) for key in sorted(nodes.keys() - parents.keys(), reverse=True)]
    while stack:
        key, level = stack.pop()
        identifier(key)
        node = nodes[key]
        label = node.get("label", "")
        require(label.strip() and "\n" not in label, "Missing single-line label: " + key)
        state = node.get("status", "documented")
        require(state in ("documented", "undocumented", "group"), "Unknown documentation status: " + key)
        require(key in index or state != "documented", "Missing Markdown section: " + key)
        require(key not in index or state != "undocumented", "Found a section marked undocumented: " + key)
        location = index.get(key)
        suffix = ("[" + location["path"] + "](../" + quote(location["path"], safe="/") + ") · " + location["heading"]
                  if location else state)
        lines.append("  " * level + "- " + label + " (`" + key + "`) — " + suffix)
        if key in notes:
            lines.extend("  " * (level + 1) + part for part in notes[key].splitlines())
        visited.add(key)
        stack.extend((child, level + 1) for child in sorted(children[key], reverse=True))
    require(len(visited) == len(nodes), "Cycle in contains relations")
    return ("\n".join(lines) + "\n").encode()


def check_destinations(folder, names):
    """Check the complete file layout before a preview, journal, or resumed write."""
    files = {managed_path(folder, name) for name in names}
    siblings = {}
    for path in files:
        while path != folder:
            siblings.setdefault(path.parent, set()).add(path.name)
            path = path.parent

    existing_root = folder
    while not existing_root.exists():
        existing_root = existing_root.parent
    require(existing_root.is_dir(), "A file blocks the canonical directory")
    for directory, requested in sorted(siblings.items()):
        require(directory not in files and (not directory.exists() or directory.is_dir()),
                "Expected a directory for canonical output: " + str(directory.relative_to(folder)))
        existing = set(os.listdir(directory)) if directory.is_dir() else set()
        variants = {}
        for name in sorted(requested):
            path = directory / name
            require(not path.exists() or name in existing,
                    "Use the existing spelling of the canonical path: " + str(path.relative_to(folder)))
            key = unicodedata.normalize("NFD", name.casefold())
            variants.setdefault(key, []).append(name)
        for spellings in variants.values():
            if len(spellings) == 1 or all(name in existing for name in spellings):
                continue
            # Probe ambiguous new names on the destination volume. Distinct
            # spellings remain valid where the filesystem distinguishes them.
            ancestor = directory
            while not ancestor.is_dir():
                ancestor = ancestor.parent
            with tempfile.TemporaryDirectory(dir=ancestor) as probe:
                for name in spellings:
                    candidate = Path(probe) / name
                    require(not candidate.exists(), "Canonical paths resolve to the same name: " + ", ".join(spellings))
                    candidate.touch()


def resume(root):
    folder = managed_path(root, CANONICAL)
    pending = journal(root)
    require(pending.is_file(), "No pending canonical update")
    batch = load_json(pending, {})
    require(batch["branch"] == git(root, "symbolic-ref", "-q", "HEAD").decode().strip(),
            "Return to the original work branch before resuming")
    if batch.get("pbi"):
        from osameru import change_directory, settings, verify_e2e
        change = change_directory(root, batch["pbi"], applying=True)
        require(verify_e2e(root, change, settings(root)) == batch.get("tested_snapshot"),
                "The tested inputs differ from the pending update; reconcile in a separate worktree")
    entries = batch["files"]
    check_destinations(folder, entries)
    remaining = []
    for name, entry in entries.items():
        path = managed_path(folder, name)
        data = base64.b64decode(entry["after"], validate=True) if entry["after"] is not None else None
        current = contents(path)
        if current != data:
            require(checksum(current) == entry["before"], "Manual change at %s; reconcile in a separate worktree" % name)
            remaining.append((path, data))
    for path, data in remaining:
        if data is None:
            path.unlink()
        else:
            write_file(path, data)
    check(root, pending=True)
    pending.unlink()


def commit_files(root, folder, updates, pbi, document_bases, tested_snapshot):
    pending = journal(root)
    require(not pending.exists(), "Pending canonical update: run structure-resume")
    entries = {}
    for name, data in updates.items():
        prior = contents(managed_path(folder, name))
        if name in document_bases:
            require(checksum(prior) == document_bases[name], "Document changed during preparation: " + name)
        if prior != data:
            entries[name] = {"before": checksum(prior), "after":
                             base64.b64encode(data).decode() if data is not None else None}
    if entries:
        branch = git(root, "symbolic-ref", "-q", "HEAD").decode().strip()
        write_file(pending, packed({"branch": branch, "files": entries, "pbi": pbi,
                                    "tested_snapshot": tested_snapshot}))
        resume(root)
    return sorted(entries)


def record_path(key):
    return "history/nodes/" + identifier(key) + ".json"


def remember(history, entry):
    origin = (entry["origin"], entry["event"])
    for old in history:
        if (old["origin"], old["event"]) == origin:
            require(entry["reason"] == old["reason"], "Conflicting source revision: " + str(origin))
            sources = set(old.get("via", [])) | set(entry.get("via", []))
            if sources:
                old["via"] = sorted(sources)
            for step in entry.get("inheritance", []):
                if step not in old.setdefault("inheritance", []):
                    old["inheritance"].append(step)
            return
    history.append(entry)


def archive_section(root, folder, key, old, commit):
    revision = git(root, "rev-parse", "--verify", commit + "^{commit}").decode().strip()
    name = old["path"]
    body_path(folder, name)
    data = git(root, "show", revision + ":" + CANONICAL + "/" + name)
    parts = sections(data, name)
    require(key in parts, "Missing retired section in recorded Git revision: " + key)
    text = parts[key][1]
    require(checksum(text.encode()) == old["sha256"], "Archive revision differs from indexed section: " + key)
    path = "history/retired/" + key + "/" + revision + ".md"
    return path, text.encode(), revision


def record_event(event, label, before, after, old_index, index, changed, archives, history):
    """Represent the change as one vertex with typed links to before/after occurrences."""
    nodes, edges = history
    center = "change/" + event
    nodes[center] = label
    for side, graph, locations in (("before", before, old_index), ("after", after, index)):
        features, relations = graph
        incident = {k: e for k, e in relations.items()
                    if e["source"] in changed or e["target"] in changed}
        involved = set(changed)
        for edge in incident.values():
            involved.update([edge["source"], edge["target"]])
        parents = {edge["target"]: (key, edge) for key, edge in relations.items()
                   if edge["kind"] == "contains"}
        frontier = list(involved)
        while frontier:
            child = frontier.pop()
            if child in parents:
                key, edge = parents[child]
                incident[key] = edge
                if edge["source"] not in involved:
                    involved.add(edge["source"])
                    frontier.append(edge["source"])
        prefix = center + "/" + side + "/"
        for key in sorted(involved & features.keys()):
            nodes.setdefault(key, {"kind": "identity", "fixed_id": key})
            occurrence = prefix + key
            nodes[occurrence] = {**features[key], **locations.get(key, {}), "fixed_id": key}
            if side == "before" and key in archives:
                nodes[occurrence].update(archives[key])
            edges[occurrence] = {"kind": side, "source": center, "target": occurrence}
            edges["identity/" + occurrence] = {"kind": "occurrence", "source": key, "target": occurrence}
        for key, edge in incident.items():
            edges[prefix + "rel/" + key] = dict(edge, source=prefix + edge["source"],
                                                target=prefix + edge["target"], relation_id=key)


def changed_paths(before, after):
    children = {}
    parents = []
    for _, edges in (before, after):
        direct = {}
        for edge in edges.values():
            if edge["kind"] == "contains":
                parent, child = edge["source"], edge["target"]
                direct[child] = parent
                children.setdefault(parent, set()).add(child)
        parents.append(direct)
    moved = {key for key in before[0].keys() & after[0].keys()
             if parents[0].get(key) != parents[1].get(key) or before[0][key]["label"] != after[0][key]["label"]}
    stack = list(moved)
    while stack:
        for child in children.get(stack.pop(), ()):
            if child not in moved:
                moved.add(child)
                stack.append(child)
    return moved


def history_digest(nodes, edges):
    head = {key: value for key, value in nodes["meta/head"].items() if key != "history_sha256"}
    return checksum(packed([{**nodes, "meta/head": head}, edges]))


def verify_records(folder, identities, edges):
    if identities or managed_path(folder, GRAPH).exists() or managed_path(folder, INDEX).exists():
        head = identities.get("meta/head", {})
        if "history_sha256" in head:
            require(head["history_sha256"] == history_digest(identities, edges), "Historical GraphML differs from its recorded revision")
        for field, name in (("graph", GRAPH), ("index", INDEX)):
            data = contents(managed_path(folder, name))
            require(data is not None and checksum(data.replace(b"\r\n", b"\n")) == head.get(field),
                    "Canonical file differs from the recorded revision: " + name)
    for key, node in identities.items():
        if key.startswith("change/") and key.count("/") == 3:
            center, side, fixed_id = key.rsplit("/", 2)
            require(node.get("fixed_id") == fixed_id and center in identities and fixed_id in identities
                    and edges.get("identity/" + key) == {"kind": "occurrence", "source": fixed_id, "target": key}
                    and edges.get(key) == {"kind": side, "source": center, "target": key},
                    "Missing historical occurrence or link: " + key)
        if node.get("kind") == "identity" and "/" not in key:
            path = managed_path(folder, record_path(key))
            raw = contents(path)
            require(raw is not None and checksum(raw.replace(b"\r\n", b"\n")) == node.get("history_sha256"),
                    "Missing or changed node history: " + key)
            entries = json.loads(raw, object_pairs_hook=distinct_fields)
            require(isinstance(entries, list) and entries, "Missing history: " + key)
            for entry in entries:
                if entry["origin"] != key or "archive" not in entry:
                    continue
                occurrence = identities.get("change/" + entry["event"] + "/before/" + key, {})
                require(occurrence.get("archive") == entry["archive"] and occurrence.get("commit") == entry["commit"],
                        "Missing retirement record: " + key)
                archive = contents(managed_path(folder, entry["archive"]))
                require(archive is not None and checksum(archive.replace(b"\r\n", b"\n")) == occurrence.get("sha256"),
                        "Missing or changed retired text: " + key)


def proposed_documents(folder, nodes, old_index, plan, drafts):
    files = dict(drafts or {})
    for name, item in plan.get("documents", {}).items():
        require(name not in files and isinstance(item, dict) and set(item) == {"base", "text"},
                "Expected a unique document with base and text: " + name)
        body = item["text"]
        require(body is None or isinstance(body, str), "Invalid document text: " + name)
        files[name] = (item["base"], body.encode() if body is not None else None)
    updates = {}
    for name, (base, data) in files.items():
        prior = contents(body_path(folder, name))
        require(checksum(prior) == base, "Document base changed: " + name)
        updates[name] = data
    for name, data in updates.items():
        if data is not None and not name.endswith(".screen-items.md"):
            require(sections(data, name), "Missing stable node marker in " + name)
    index = inventory(folder, updates, nodes)
    refresh = plan.get("refresh", [])
    require(isinstance(refresh, list) and all(isinstance(x, str) for x in refresh),
            "refresh must list manually edited specification paths")
    for key in old_index.keys() | index.keys():
        previous, current = old_index.get(key), index.get(key)
        # Screen definitions have their own paths and review checks.
        if previous and current and all(previous[f] == current[f] for f in ("path", "heading", "sha256")):
            continue
        for location in (previous, current):
            if location:
                name = location["path"]
                require(name in files or name in refresh,
                        "Unplanned Markdown change; review and include in refresh: " + name)
    for name, data in updates.items():
        if name.endswith(".screen-items.md") and data is not None:
            require(any(loc.get("screen") == name for loc in index.values()),
                    "Identify the owning specification with the node's screen field: " + name)
    return updates, index, {name: base for name, (base, _) in files.items()}


def revision_updates(root, folder, old_nodes, nodes, old_index, plan, touched, updates, revision):
    event, reason = plan["event"], plan["reason"]
    archives = {}
    logs = {}

    def records(key):
        if key not in logs:
            logs[key] = load_json(managed_path(folder, record_path(key)), [])
        return logs[key]

    inheritance = plan.get("inherit", [])
    # Read inheritance from the state before this event, even in a chained reorganization.
    original = {source: copy.deepcopy(records(identifier(source))) for source in {rule["from"] for rule in inheritance}}
    for rule in inheritance:
        source, target = rule["from"], rule["to"]
        require(source in old_nodes and target in nodes and source != target,
                "Invalid revision inheritance endpoints")
        selected = rule["entries"]
        require(selected == "*" or isinstance(selected, list) and all(isinstance(x, str) for x in selected),
                "Choose a list of source revisions or *")
        found = set()
        for item in original[source]:
            identity = item["origin"] + "/" + item["event"]
            if selected == "*" or identity in selected:
                copied = dict(item, via=sorted(set(item.get("via", [])) | {source}))
                step = {"from": source, "to": target, "event": event}
                copied["inheritance"] = list(item.get("inheritance", [])) + [step]
                remember(records(target), copied)
                found.add(identity)
        require(selected == "*" or isinstance(selected, list) and set(selected) == found,
                "Unknown source revision in inheritance rule")
        touched.update((source, target))
    for rule in plan.get("legacy", []):
        name, target = rule["path"], rule["to"]
        require(target in nodes and name.endswith(".history.md")
                and name.split("/")[0] not in ("structure", "history"), "Invalid legacy history mapping")
        path = managed_path(folder, name)
        require(rule.get("base") == checksum(contents(path)), "Legacy source changed: " + name)
        text = path.read_text(encoding="utf-8")
        excerpt = rule.get("text", text)
        require(excerpt and excerpt in text, "Legacy revision text differs: " + name)
        entry = {"origin": name, "event": checksum(excerpt.encode()), "reason": excerpt,
                 "source": name, "scope": rule.get("scope", "")}
        remember(records(target), entry)
        touched.add(target)
    for key in sorted(touched):
        entry = {"origin": key, "event": event, "reason": reason}
        if revision:
            entry["revision"] = revision
        if key not in nodes and key in old_index:
            path, body, archived_revision = archive_section(root, folder, key, old_index[key], plan.get("revision", "HEAD"))
            updates[path] = body
            archives[key] = {"archive": path, "commit": archived_revision}
            entry.update(archives[key])
        remember(records(key), entry)
    for key, log in logs.items():
        updates[record_path(key)] = packed(log)
    return archives, logs


def execute(root, plan, drafts=None, preview=False, pbi=None, tested_snapshot=None):
    folder = managed_path(root, CANONICAL)
    require(not journal(root).exists(), "Pending canonical update: run structure-resume")
    require(isinstance(plan, dict) and not set(plan) - {"event", "reason", "base", "revision",
            "graph", "documents", "inherit", "legacy", "refresh", "notes"}, "Unknown structure plan field")
    event = identifier(plan.get("event"))
    reason = plan.get("reason")
    require(isinstance(reason, str) and reason.strip(), "A change reason is required")
    require(isinstance(plan.get("documents", {}), dict), "documents must map paths to proposed files")
    for field, required in (("inherit", {"from", "to", "entries"}), ("legacy", {"path", "base", "to"})):
        rules = plan.get(field, [])
        require(isinstance(rules, list) and all(isinstance(rule, dict) and required <= rule.keys()
                and all(isinstance(rule[key], str) for key in required - {"entries"}) for rule in rules),
                "Invalid " + field + " rule; required fields: " + ", ".join(sorted(required)))
    before = graph_at(folder, GRAPH)
    old_index = load_json(managed_path(folder, INDEX), {})
    history = graph_at(folder, EVENTS)
    verify_records(folder, *history)
    center = "change/" + event
    fingerprint = checksum(packed([plan, {k: checksum(data) for k, (_, data) in (drafts or {}).items()}]))
    if center in history[0]:
        require(history[0][center].get("pbi") == pbi, "Event ID belongs to another change: " + event)
        require(history[0][center]["request"] == fingerprint, "Event ID already used with different inputs: " + event)
        check(root)
        return []
    require(plan.get("base") == stamp(folder), "Canonical structure changed; reconcile the plan and refresh its base")
    graph = copy.deepcopy(before)
    apply_delta(*graph, plan.get("graph", {}))
    nodes, edges = graph
    previous_ids = {key.casefold() for key, node in history[0].items() if node.get("kind") == "identity"}
    for key in nodes:
        identifier(key)
        if key not in before[0]:
            require(key.casefold() not in previous_ids and not managed_path(folder, record_path(key)).exists(), "Retired ID already used: " + key)
    updates, index, document_bases = proposed_documents(folder, nodes, old_index, plan, drafts)
    old_screens = {loc["screen"]: loc["screen_sha256"] for loc in old_index.values() if "screen" in loc}
    current_screens = {loc["screen"] for loc in index.values() if "screen" in loc}
    reviewed_paths = set(updates) | set(plan.get("refresh", []))
    # Onboarding can index existing screen files alongside a newly documented node.
    for key, location in index.items():
        screen = location.get("screen")
        if not screen or old_screens.get(screen) == location["screen_sha256"]:
            continue
        if pbi or key in old_index or screen in old_screens:
            require(screen in reviewed_paths, "Include the changed screen item file in the reviewed change: " + screen)
    detached_screens = old_screens.keys() - current_screens - reviewed_paths
    if pbi:
        check_destinations(folder, detached_screens)
    for screen in detached_screens:
        require(body_path(folder, screen).is_file(), "Include the removed screen item file in the reviewed change: " + screen)
    notes = node_notes(folder, nodes)
    reviewed_notes = plan.get("notes", {})
    require(isinstance(reviewed_notes, dict), "notes must map current node IDs to text or null")
    for key, value in reviewed_notes.items():
        require(key in nodes and (value is None or isinstance(value, str)), "Invalid node note: " + key)
        name = "structure/notes/" + key + ".md"
        current = contents(managed_path(folder, name))
        normalized = current.replace(b"\r\n", b"\n").replace(b"\r", b"\n") if current is not None else None
        desired = value.replace("\r\n", "\n").replace("\r", "\n").encode() if value is not None else None
        require(normalized == desired or checksum(normalized) == history[0].get(key, {}).get("note_sha256", "new"),
                "Node note has an unreviewed edit: " + key)
        if desired is None:
            notes.pop(key, None)
        else:
            notes[key] = desired.decode()
        updates[name] = desired if normalized != desired else current
        document_bases[name] = checksum(current)
    tree = render(nodes, edges, index, notes)
    revision = None
    if "revision" in plan:
        require(isinstance(plan["revision"], str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", plan["revision"]),
                "Use the full analyzed commit ID for revision")
        revision = git(root, "rev-parse", "--verify", plan["revision"] + "^{commit}").decode().strip()
    touched = {k for k in before[0].keys() | nodes.keys() if before[0].get(k) != nodes.get(k)
               or old_index.get(k) != index.get(k)}
    touched.update(changed_paths(before, graph))
    note_digests = {key: checksum(text.encode()) for key, text in notes.items()}
    changed_notes = {key for key in nodes if history[0].get(key, {}).get("note_sha256") != note_digests.get(key)}
    require(not pbi or changed_notes <= reviewed_notes.keys(), "Include changed node notes in the reviewed plan")
    touched.update(changed_notes)
    for key in before[1].keys() | edges.keys():
        if before[1].get(key) != edges.get(key):
            for edge in [before[1].get(key), edges.get(key)]:
                if edge:
                    touched.update([edge["source"], edge["target"]])
    archives, logs = revision_updates(root, folder, before[0], nodes, old_index, plan, touched, updates, revision)
    changed = [name for name, data in updates.items() if contents(managed_path(folder, name)) != data]
    require(touched or changed or contents(managed_path(folder, TREE)) != tree, "No canonical change to record")
    record_event(event, {"kind": "change", "reason": reason, "request": fingerprint},
                 before, graph, old_index, index, touched, archives, history)
    if "meta/head" in history[0]:
        history[1][center + "/previous"] = {"source": center, "target": "change/" + history[0]["meta/head"]["event"],
                                           "kind": "previous"}
    if revision:
        history[0][center]["revision"] = revision
    if pbi:
        history[0][center]["pbi"] = pbi
    for key, log in logs.items():
        history[0][key]["history_sha256"] = checksum(packed(log))
        identity = history[0][key]
        for side, value in (("before", identity.get("note_sha256")), ("after", note_digests.get(key))):
            occurrence = history[0].get(center + "/" + side + "/" + key)
            if occurrence is not None and value is not None:
                occurrence.update(note="structure/notes/" + key + ".md", note_sha256=value)
        if key in note_digests:
            identity["note_sha256"] = note_digests[key]
        else:
            identity.pop("note_sha256", None)
    for rule in plan.get("inherit", []):
        source, target = rule["from"], rule["to"]
        history[1][center + "/inherit/" + source + "/" + target] = {
            "kind": "inherited", "source": center + "/before/" + source, "target": center + "/after/" + target}
    current_graph = graph_bytes(*graph, readable=True)
    current_index = packed(index)
    history[0]["meta/head"] = {"kind": "head", "event": event, "index": checksum(current_index),
                               "graph": checksum(current_graph)}
    history[0]["meta/head"]["history_sha256"] = history_digest(*history)
    updates.update({GRAPH: current_graph, EVENTS: graph_bytes(*history, readable=True), INDEX: current_index, TREE: tree})
    check_destinations(folder, updates)
    if preview:
        diff = []
        for name, data in sorted(updates.items()):
            prior = contents(managed_path(folder, name))
            if data != prior:
                diff.extend(difflib.unified_diff((prior or b"").decode().splitlines(), (data or b"").decode().splitlines(),
                            fromfile="a/" + name if prior is not None else "/dev/null",
                            tofile="b/" + name if data is not None else "/dev/null", lineterm=""))
        return diff
    require(plan["base"] == stamp(folder), "Canonical structure changed during preparation; review the updated base")
    return commit_files(root, folder, updates, pbi, document_bases, tested_snapshot)


def check(root, pending=False):
    folder = managed_path(root, CANONICAL)
    require(pending or not journal(root).exists(), "Incomplete canonical update")
    for name in (GRAPH, EVENTS, INDEX, TREE):
        require(managed_path(folder, name).is_file(), "Missing " + name)
    nodes, edges = graph_at(folder, GRAPH)
    events, history_edges = graph_at(folder, EVENTS)
    verify_records(folder, events, history_edges)
    require(all(key in events and events[key].get("kind") == "identity" for key in nodes),
            "Missing historical node identity")
    index = inventory(folder, {}, nodes)
    require(index == load_json(managed_path(folder, INDEX), {}), "Markdown locations or contents changed")
    notes = node_notes(folder, nodes)
    for key in nodes:
        expected = checksum(notes[key].encode()) if key in notes else None
        require(events[key].get("note_sha256") == expected, "Node note differs from its recorded revision: " + key)
    require(render(nodes, edges, index, notes) == managed_path(folder, TREE).read_bytes().replace(b"\r\n", b"\n"), "Stale hierarchy")
