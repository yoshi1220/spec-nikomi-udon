#!/usr/bin/env python3
"""Validate a task graph read as JSON from stdin and print ordered task IDs."""

import heapq
import json
import sys


def read_dependencies(tasks):
    if not isinstance(tasks, list):
        raise ValueError("Expected a JSON array of tasks.")

    dependencies = {}
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object with id and depends_on.")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id or any(map(str.isspace, task_id)):
            raise ValueError("Each task needs a non-empty id without whitespace.")
        if task_id in dependencies:
            raise ValueError(f"Duplicate task ID: {task_id}")
        prerequisites = task.get("depends_on")
        if not isinstance(prerequisites, list) or any(
            not isinstance(prerequisite, str) for prerequisite in prerequisites
        ):
            raise ValueError(f"{task_id}: depends_on must be an array of task IDs.")
        if len(prerequisites) != len(set(prerequisites)):
            raise ValueError(f"{task_id}: duplicate prerequisite.")
        dependencies[task_id] = prerequisites

    for task_id, prerequisites in dependencies.items():
        for prerequisite in prerequisites:
            if prerequisite == task_id:
                raise ValueError(f"{task_id}: a task cannot depend on itself.")
            if prerequisite not in dependencies:
                raise ValueError(f"{task_id}: unknown prerequisite {prerequisite}.")
    return dependencies


def find_cycle(dependencies, remaining):
    # Each unscheduled task has at least one unscheduled prerequisite.
    current = next(task_id for task_id in dependencies if task_id in remaining)
    trail = []
    visited = {}
    while current not in visited:
        visited[current] = len(trail)
        trail.append(current)
        current = next(
            prerequisite
            for prerequisite in dependencies[current]
            if prerequisite in remaining
        )

    # The walk follows prerequisites backwards. Report edges forwards.
    cycle = trail[visited[current] :] + [current]
    return " -> ".join(reversed(cycle))


def order_tasks(tasks):
    dependencies = read_dependencies(tasks)
    task_ids = list(dependencies)
    priority = {task_id: index for index, task_id in enumerate(task_ids)}
    dependents = {task_id: [] for task_id in task_ids}
    unmet = {}
    ready = []

    for task_id, prerequisites in dependencies.items():
        unmet[task_id] = len(prerequisites)
        if not prerequisites:
            heapq.heappush(ready, priority[task_id])
        for prerequisite in prerequisites:
            dependents[prerequisite].append(task_id)

    ordered = []
    while ready:
        task_id = task_ids[heapq.heappop(ready)]
        ordered.append(task_id)
        for dependent in dependents[task_id]:
            unmet[dependent] -= 1
            if unmet[dependent] == 0:
                heapq.heappush(ready, priority[dependent])

    if len(ordered) != len(task_ids):
        remaining = {task_id for task_id in task_ids if unmet[task_id]}
        raise ValueError(f"Dependency cycle: {find_cycle(dependencies, remaining)}")
    return ordered


def main():
    try:
        ordered = order_tasks(json.load(sys.stdin))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(ordered))
    return 0


if __name__ == "__main__":
    sys.exit(main())
