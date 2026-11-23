#!/usr/bin/env python3
"""Update and query a private, temporary directed GraphML file (Python 3.8+)."""

import argparse
from collections import deque
import fcntl
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import quote
import xml.etree.ElementTree as ET

# The installer verifies the installed skill directory, including unexpected files.
if __name__ == "__main__":
    sys.dont_write_bytecode = True
from order_tasks import order_tasks

NS = "http://graphml.graphdrawing.org/xmlns"
ET.register_namespace("", NS)


def create_scratch_dir(worktree):
    if not worktree.is_dir():
        raise ValueError("Expected an existing project directory.")
    for candidate in (tempfile.gettempdir(), "/tmp", "/var/tmp"):
        parent = Path(candidate).resolve()
        try:
            if any(worktree.samefile(path) for path in (parent, *parent.parents)):
                continue
            return tempfile.mkdtemp(prefix="nikomi-", dir=parent)
        except OSError:
            continue
    raise ValueError("No writable temporary directory outside the project.")


def tag(name):
    return "{%s}%s" % (NS, name)


def xml_id(prefix, value):
    # Domain IDs can contain characters outside GraphML's XML ID alphabet.
    return prefix + value.encode("utf-8").hex()


def domain_id(value):
    return bytes.fromhex(value[1:]).decode("utf-8")


def read_graph(path):
    return decode_graph(ET.parse(path).getroot())


def decode_graph(root):
    nodes, edges = {}, {}
    graph = root.find(tag("graph"))
    if graph is None or graph.get("edgedefault") != "directed":
        raise ValueError("Expected a directed work graph.")
    keys = {key.attrib["id"]: key.attrib["attr.name"] for key in root.findall(tag("key"))}
    for element in graph:
        fields = {keys[d.attrib["key"]]: d.text or "" for d in element.findall(tag("data"))}
        item_id = domain_id(element.attrib["id"])
        if element.tag == tag("node"):
            nodes[item_id] = fields
        elif element.tag == tag("edge"):
            fields.update({k: domain_id(element.attrib[k]) for k in ("source", "target")})
            edges[item_id] = fields
    return nodes, edges


def graph_bytes(nodes, edges, readable=False):
    root = ET.Element(tag("graphml"))
    graph = ET.Element(tag("graph"), edgedefault="directed")
    keys = {}
    for kind, items in (("node", nodes), ("edge", edges)):
        for item_id, fields in (sorted(items.items()) if readable else items.items()):
            attrs = {"id": xml_id(kind[0], item_id)}
            if kind == "edge":
                attrs.update({k: xml_id("n", fields[k]) for k in ("source", "target")})
            element = ET.SubElement(graph, tag(kind), attrs)
            for name, value in (sorted(fields.items()) if readable else fields.items()):
                if kind == "edge" and name in ("source", "target"):
                    continue
                if (kind, name) not in keys:
                    key = keys[kind, name] = (xml_id(kind[0] + "k", name) if readable else "k%d" % len(keys))
                    ET.SubElement(root, tag("key"), {
                        "id": key, "for": kind, "attr.name": name, "attr.type": "string"
                    })
                ET.SubElement(element, tag("data"), key=keys[kind, name]).text = value
    root.append(graph)
    if readable:
        # Keep current and historical graph diffs legible on Python 3.8 as well.
        def indent(element, level):
            if len(element):
                element.text = "\n" + "  " * (level + 1)
                for child in element:
                    indent(child, level + 1)
                    child.tail = element.text
                element[-1].tail = "\n" + "  " * level
        indent(root, 0)
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    data = data.replace(b"\r", b"&#13;")  # Preserve CR and CRLF in field text when XML is read.
    ET.fromstring(data)  # Reject invalid XML characters before replacing the last good file.
    return data


def save_graph(path, nodes, edges):
    data = graph_bytes(nodes, edges)
    stream = tempfile.NamedTemporaryFile(dir=path.parent, delete=False)
    pending = Path(stream.name)
    try:
        with stream:
            stream.write(data)
        os.replace(pending, path)
    finally:
        pending.unlink(missing_ok=True)


def check_id(value):
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ValueError("Expected a nonempty ID without whitespace.")


def apply_delta(nodes, edges, delta):
    if not isinstance(delta, dict) or set(delta) - {"nodes", "edges", "drop_nodes", "drop_edges"}:
        raise ValueError("Expected nodes, edges, drop_nodes or drop_edges.")
    for section, items in (("nodes", nodes), ("edges", edges)):
        removed = delta.get("drop_" + section, [])
        changes = delta.get(section, {})
        if not isinstance(removed, list) or not isinstance(changes, dict):
            raise ValueError("Expected an ID list for removals and an object for updates.")
        for item_id in removed:
            check_id(item_id)
            items.pop(item_id, None)
        for item_id, fields in changes.items():
            check_id(item_id)
            if not isinstance(fields, dict):
                raise ValueError("Each ID needs an object of fields.")
            current = items.setdefault(item_id, {})
            for name, value in fields.items():
                if value is None:
                    current.pop(name, None)
                elif isinstance(value, str):
                    current[name] = value
                else:
                    raise ValueError("Field values must be strings or null.")
    for edge_id, edge in edges.items():
        if not edge.get("kind") or any(edge.get(k) not in nodes for k in ("source", "target")):
            raise ValueError("Missing edge kind or unknown endpoint: " + edge_id)


def adjacent(nodes, edges, kinds, reverse=False):
    result = {n: [] for n in nodes}
    for edge in edges.values():
        if kinds and edge["kind"] not in kinds:
            continue
        source, target = edge["source"], edge["target"]
        if reverse:
            source, target = target, source
        result[source].append(target)
    return result


def reachable(links, start):
    seen = {start}
    todo = deque([start])
    result = []
    while todo:
        for target in links[todo.popleft()]:
            if target not in seen:
                seen.add(target)
                result.append(target)
                todo.append(target)
    return result


def distinct_fields(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("Repeated JSON field or ID: " + name)
        result[name] = value
    return result


def task_graph(tasks):
    nodes = {task["id"]: {} for task in tasks}
    edges = {}
    for task in tasks:
        for parent in task["depends_on"]:
            target = task["id"]
            edge_id = "requires/{}/{}".format(quote(parent, safe=""), quote(target, safe=""))
            edges[edge_id] = {"source": parent, "target": target, "kind": "requires"}
    return nodes, edges


def run(args):
    path = args.file
    if args.command in ("update", "tasks"):
        delta = json.load(sys.stdin, object_pairs_hook=distinct_fields)
        result = None
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            fcntl.flock(directory, fcntl.LOCK_EX)
            if args.command == "tasks":
                ordered = order_tasks(delta)
                nodes, edges = task_graph(delta)
                if args.print_order:
                    result = ordered
            else:
                nodes, edges = read_graph(path) if args.existing or path.exists() else ({}, {})
                apply_delta(nodes, edges, delta)
            save_graph(path, nodes, edges)
        finally:
            os.close(directory)
        return result
    nodes, edges = read_graph(path)
    if args.command == "show":
        selected = dict.fromkeys(args.ids or nodes)
        return {"nodes": {n: nodes[n] for n in selected},
                "edges": {i: e for i, e in edges.items()
                          if e["source"] in selected or e["target"] in selected}}
    if args.command == "affected":
        return reachable(adjacent(nodes, edges, args.via, args.reverse), args.id)
    parents = adjacent(nodes, edges, [args.relation], reverse=True)
    if args.command == "order":
        return order_tasks([{"id": n, "depends_on": list(dict.fromkeys(p))} for n, p in parents.items()])
    return [
        node for node, prerequisites in parents.items()
        if nodes[node].get("state") in ("Missing", "Partial")
        and (args.kind is None or nodes[node].get("kind") == args.kind)
        and all(nodes[parent].get("state") in ("Resolved", "Clear") for parent in prerequisites)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    scratch = commands.add_parser("scratch-dir", help="create a private directory outside the project")
    scratch.add_argument("worktree", type=Path)
    for name in ("update", "tasks", "show", "affected", "order", "ready"):
        command = commands.add_parser(name)
        command.add_argument("file", type=Path)
        if name == "tasks":
            command.add_argument("--print-order", action="store_true")
        elif name == "update":
            command.add_argument("--existing", action="store_true", help="require the previous graph")
        elif name == "show":
            command.add_argument("ids", nargs="*")
        elif name == "affected":
            command.add_argument("id")
            command.add_argument("--via", nargs="+")
            command.add_argument("--reverse", action="store_true")
        elif name in ("order", "ready"):
            command.add_argument("relation")
            if name == "ready":
                command.add_argument("--kind")
    try:
        args = parser.parse_args()
        if args.command == "scratch-dir":
            print(create_scratch_dir(args.worktree))
            return
        result = run(args)
        if result is not None:
            print(json.dumps(result, ensure_ascii=False))
    except (ValueError, KeyError, OSError, ET.ParseError) as error:
        parser.exit(1, "Work graph: %s\n" % error)


if __name__ == "__main__":
    main()
