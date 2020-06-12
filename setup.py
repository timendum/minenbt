"""A setup script to demonstrate build using bcrypt"""
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python

from cx_Freeze import setup, Executable

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


setup(
    name="minenbt",
    version="0.1",
    description="lib and cli script to handle Minecraft savefiles",
    author="timendum",
    url="https://github.com/timendum/minenbt/",
    packages=["minenbt"],
    executables=[Executable("minenbt/__main__.py", targetName="minenbt")],
    options={"build_exe": build_exe_options},
    install_requires=["nbtlib", "numpy"],
    license="GNU General Public License v3.0",
)
