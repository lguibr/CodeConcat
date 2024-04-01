# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

url = "https://github.com/lguibr/CodeConcat"

setup(
    name="codeconcat",
    version="0.1.5",
    author="Luis Guilherme",
    author_email="lgpelin92@gmail.com",
    description="A tool to concatenate a folders into a single text file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url=url,
    project_urls={
        "Bug Tracker": f"{url}/issues",
        "Documentation": f"{url}/blob/main/README.md",
        "Source Code": url,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "python-magic",
    ],
    entry_points={
        "console_scripts": [
            "codeconcat=codeconcat.main:main",
        ],
    },
)
