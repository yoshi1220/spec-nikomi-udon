"""Prepare project-local Playwright tooling after the skill installation commits."""
import json
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.8–3.10
    import tomli as tomllib

NODE_PROBE = """const {chromium, expect} = require('@playwright/test');
(async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.setContent('<h1>Ready</h1>');
    await expect(page.getByRole('heading')).toHaveText('Ready');
  } finally { await browser.close(); }
})().catch(e => { console.error(e.message); process.exitCode = 1; });"""
PYTHON_PROBE = """import pytest_playwright
from playwright.sync_api import sync_playwright, expect
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    page.set_content('<h1>Ready</h1>')
    expect(page.get_by_role('heading')).to_have_text('Ready')
    browser.close()
"""


def node_package(root):
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    if not isinstance(package, dict) or not isinstance(package.get("packageManager", ""), str):
        raise ValueError("Check the project package.json and its packageManager field.")
    if any(not isinstance(package.get(key, {}), dict) for key in ("dependencies", "devDependencies")):
        raise ValueError("Check the dependencies in package.json.")
    return package


def node_commands(root):
    package = node_package(root)
    declared = package.get("packageManager", "").split("@")[0]
    locks = {name for name, file in (("npm", "package-lock.json"), ("npm", "npm-shrinkwrap.json"),
                                      ("pnpm", "pnpm-lock.yaml"), ("yarn", "yarn.lock"),
                                      ("bun", "bun.lock"), ("bun", "bun.lockb"),
                                      ("deno", "deno.lock")) if (root / file).exists()}
    if declared:
        locks.add(declared)
    if len(locks) > 1 or locks - {"npm", "pnpm", "yarn"}:
        raise ValueError("Check the project's Node package manager and configure Playwright with it.")
    manager = next(iter(locks), "npm")
    deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    add = [manager, "install"] if "@playwright/test" in deps else [
        manager, "install" if manager == "npm" else "add", "-D", "@playwright/test"]
    prefix = {"npm": ["npm", "exec", "--offline", "--"], "pnpm": ["pnpm", "exec"], "yarn": ["yarn"]}[manager]
    node = ["yarn", "node"] if manager == "yarn" else ["node"]
    return [add, prefix + ["playwright", "install", "chromium"]], node + ["-e", NODE_PROBE]


def declares_runner(dependencies):
    pattern = r"^pytest[-_.]+playwright(?=$|[\s<>=!~@;\[])"
    return any(isinstance(dep, str) and re.match(pattern, dep.strip(), re.I) for dep in dependencies)


def runner_options(config, manager):
    # An empty list selects a declared default dependency; None means it needs adding.
    project = config.get("project", {})
    poetry = config.get("tool", {}).get("poetry", {})
    if declares_runner(project.get("dependencies", [])):
        return []
    for extra, deps in project.get("optional-dependencies", {}).items():
        if declares_runner(deps):
            return ["--extra" if manager == "uv" else "--extras", extra]
    if manager == "poetry":
        if declares_runner(poetry.get("dependencies", {})):
            for extra, deps in poetry.get("extras", {}).items():
                if declares_runner(deps):
                    return ["--extras", extra]
            return []
        if declares_runner(poetry.get("dev-dependencies", {})):
            return ["--with", "dev"]
        for name, group in poetry.get("group", {}).items():
            if declares_runner(group.get("dependencies", {})):
                return ["--with", name]
    for name, deps in config.get("dependency-groups", {}).items():
        if declares_runner(deps):
            return ["--group" if manager == "uv" else "--with", name]
    if manager == "uv" and declares_runner(config.get("tool", {}).get("uv", {}).get("dev-dependencies", [])):
        return ["--group", "dev"]
    return None


def runner_install(config, manager):
    options = runner_options(config, manager)
    if options is not None:
        install = ["uv", "sync", "--inexact"] if manager == "uv" else ["poetry", "install"]
        return install + options
    return ([manager, "add", "--dev"] if manager == "uv" else [manager, "add", "--group", "dev"]) + ["pytest-playwright"]


def requirements_declare_runner(requirements):
    pending = [requirements] if requirements.is_file() else []
    seen = set()
    complete = True
    while pending:
        path = pending.pop()
        identity = path.resolve()
        if identity in seen:
            continue
        seen.add(identity)
        if not path.is_file():
            complete = False
            continue
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if declares_runner(lines):
            return True
        for line in lines:
            include = re.match(r"^\s*(?:-r\s*|--requirement(?:=|\s+))(.+)$", line)
            if include:
                names = shlex.split(include[1], comments=True)
                if len(names) == 1 and "://" not in names[0] and "${" not in names[0]:
                    pending.append(path.parent / names[0])
                else:
                    complete = False
    return False if complete else None


def project_declares_python_runner(root):
    try:
        declared = requirements_declare_runner(root / "requirements.txt")
        if declared:
            return True
        project = root / "pyproject.toml"
        if project.is_file():
            config = tomllib.loads(project.read_text(encoding="utf-8"))
            if any(runner_options(config, manager) is not None for manager in ("poetry", "uv")):
                return True
        return declared
    except (OSError, ValueError, TypeError, AttributeError, RuntimeError):
        # Leave the choice open when Python's declarations cannot be read.
        return None


def python_commands(root):
    project = root / "pyproject.toml"
    config = tomllib.loads(project.read_text(encoding="utf-8")) if project.exists() else {}
    tools = config.get("tool", {})
    if not isinstance(tools, dict):
        raise ValueError("Check the tool table in pyproject.toml.")
    managers = {name for name, lock in (("poetry", "poetry.lock"), ("uv", "uv.lock"),
                                        ("pdm", "pdm.lock"), ("pipenv", "Pipfile"),
                                        ("pixi", "pixi.lock")) if (root / lock).exists()}
    managers.update(name for name in ("uv", "poetry", "pdm", "pixi") if name in tools)
    if len(managers) > 1 or managers - {"poetry", "uv"}:
        raise ValueError("Use the project's Python dependency manager to prepare pytest-playwright and Chromium.")
    if managers:
        manager = next(iter(managers))
        try:
            install = runner_install(config, manager)
        except (TypeError, AttributeError, ValueError) as error:
            raise ValueError("Check the dependency declarations in pyproject.toml.") from error
        if manager == "poetry":
            return [install, ["poetry", "run", "playwright", "install", "chromium"]], [
                "poetry", "run", "python", "-c", PYTHON_PROBE]
        environment = root / os.environ.get("UV_PROJECT_ENVIRONMENT", ".venv")
        python = str(environment / "bin/python")
        return [install, [python, "-m", "playwright", "install", "chromium"]], [python, "-c", PYTHON_PROBE]
    python = str(root / ".venv/bin/python")
    if (root / ".venv").exists() and not Path(python).is_file():
        raise ValueError("Check the existing .venv and its Python interpreter before preparing Playwright.")
    if not (root / "requirements.txt").exists() and not Path(python).exists():
        raise ValueError("Choose the project's Python dependency manager, prepare pytest-playwright "
                         "and Chromium, then rerun init. For uv projects, run uv lock first.")
    steps = []
    if not Path(python).exists():
        steps.append(["uv", "venv", ".venv"])
    install = ["uv", "pip", "install", "--python", python]
    if (root / "requirements.txt").is_file():
        install.extend(["-r", "requirements.txt"])
    steps.extend([install + ["pytest-playwright"],
                  [python, "-m", "playwright", "install", "chromium"]])
    return steps, [python, "-c", PYTHON_PROBE]


def prepare(root, method, choose):
    if method == "manual":
        print("Manual E2E: prepare the test data and have the tester record each observed result.")
        return
    if method in ("chrome-extension", "agent-browser"):
        instruction = ("Connect the project extension." if method == "chrome-extension" else
                       "Open the Codex desktop browser or connect Claude Code with /chrome.")
        print(f"Browser connection pending / 接続確認待ち: {instruction} "
              "Open the test page in the target session and check that you can observe the expected result.")
        return
    try:
        node = (root / "package.json").is_file()
        python = any((root / p).exists() for p in ("pyproject.toml", "requirements.txt", "uv.lock", "poetry.lock", ".venv", "Pipfile", "pdm.lock"))
        kinds = []
        if node:
            kinds.append("Node.js")
        if python:
            kinds.append("Python")
        if not kinds:
            raise ValueError("Select a project test runner and set up a Node.js or Python test environment.")
        if len(kinds) == 2:
            try:
                package = node_package(root)
                existing_node = any("@playwright/test" in package.get(key, {})
                                    for key in ("dependencies", "devDependencies"))
            except (OSError, ValueError):
                existing_node = None
            existing_python = project_declares_python_runner(root)
            if existing_node is not None and existing_python is not None and existing_node != existing_python:
                kinds = ["Node.js" if existing_node else "Python"]
        kind = kinds[0] if len(kinds) == 1 else choose("Playwright runner", kinds)
        try:
            steps, probe = node_commands(root) if kind == "Node.js" else python_commands(root)
        except ValueError:
            # Projects with other dependency managers may already have a usable local runner.
            probe = (["node", "-e", NODE_PROBE] if kind == "Node.js"
                     else [str(root / ".venv/bin/python"), "-c", PYTHON_PROBE])
            if shutil.which(probe[0]) and subprocess.run(probe, cwd=root, capture_output=True).returncode == 0:
                print("Playwright ready / 実行確認済み")
                return
            raise
        check = probe
        if probe[0] == "poetry":
            # 'poetry run' can create an environment. Only probe an existing one before consent.
            check = []
            if shutil.which("poetry"):
                info = subprocess.run(["poetry", "env", "info", "--executable"], cwd=root,
                                      capture_output=True, text=True)
                if info.returncode == 0 and info.stdout.strip():
                    check = [info.stdout.strip(), "-c", PYTHON_PROBE]
        if check and shutil.which(check[0]):
            imports = ("require('@playwright/test')" if kind == "Node.js"
                       else "import pytest_playwright, playwright.sync_api")
            if subprocess.run(check[:-1] + [imports], cwd=root, capture_output=True).returncode == 0:
                if subprocess.run(check, cwd=root, capture_output=True).returncode == 0:
                    print("Playwright ready / 実行確認済み")
                    return
                steps = steps[-1:]
        for command in steps:
            print(shlex.join(command))
        if choose("Run setup / 環境を構築しますか", ("yes", "no"), "no") == "no":
            raise ValueError("Run the displayed commands when ready.")
        for command in steps:
            subprocess.run(command, cwd=root, check=True)
        subprocess.run(probe, cwd=root, check=True)
        print("Playwright ready / 実行確認済み")
    except (EOFError, KeyboardInterrupt):
        print("\nE2E preparation interrupted / 環境準備を中断しました。"
              " Skills and settings are installed. Rerun the same init to resume.")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"E2E preparation incomplete / 準備未完了: {error}\n"
              "Check the runner, Chromium and OS dependencies, then rerun init. See README.")
