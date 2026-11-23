"""Configure source and wheel distribution builds."""
import sys
from tempfile import TemporaryDirectory

from setuptools import setup


options = {"sdist": {"owner": "root", "group": "wheel" if sys.platform == "darwin" else "root"}}

if "bdist_wheel" in sys.argv[1:]:
    # A fresh build directory excludes files removed since the previous wheel.
    with TemporaryDirectory(prefix="nikomi-build-") as build_dir:
        setup(options={**options, "build": {"build_base": build_dir}})
else:
    setup(options=options)
