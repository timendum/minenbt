"""A setup script to demonstrate build using bcrypt"""
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python
import os
from typing import Dict

from cx_Freeze import Executable, setup

here = os.path.abspath(os.path.dirname(__file__))

# Dependencies fine tuning
build_exe_options = {
    "excludes": [
        "curses",
        "difflib",
        "email",
        "html",
        "http",
        "multiprocessing",
        "numpy.distutils",
        "numpy.doc",
        "numpy.fft",
        "numpy.matrixlib.tests",
        "numpy.polynomial",
        "numpy.testing",
        "numpy.tests",
        "pydoc",
        "pydoc_data",
        "setuptools",
        "tarfile",
        "tcl",
        "unittest",
        "xml",
        "_bz2",
        "_lzma",
        "_socket",
        "_ssl",
    ]
}

about: Dict[str, str] = {}
with open(os.path.join(here, "minenbt", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    author=about["__author__"],
    url=about["__url__"],
    packages=["minenbt"],
    executables=[Executable("minenbt/__main__.py", targetName="minenbt")],
    options={"build_exe": build_exe_options},
    install_requires=["nbtlib", "numpy"],
    license="GNU General Public License v3.0",
)
