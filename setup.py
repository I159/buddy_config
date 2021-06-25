import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="buddy-config",
    version="0.1.7",
    description="Lazy environment variable configuration of declarative style.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/I159/buddy_config",
    author="Ilya 'I159' Pekelny",
    author_email="pekelny@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["buddy_config"],
)
