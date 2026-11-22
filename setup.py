"""Keep repeated wheel builds from including files removed from the checkout."""
import sys
from tempfile import TemporaryDirectory

from setuptools import setup


if "bdist_wheel" in sys.argv[1:]:
    with TemporaryDirectory(prefix="nikomi-build-") as build_dir:
        setup(options={"build": {"build_base": build_dir}})
else:
    setup()
