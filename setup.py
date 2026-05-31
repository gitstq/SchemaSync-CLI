"""
Setup script for SchemaSync-CLI
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="schemasync-cli",
    version="1.0.0",
    author="SchemaSync Team",
    author_email="",
    description="A lightweight database schema migration tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/SchemaSync-CLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "postgresql": ["psycopg2-binary>=2.9.0"],
        "mysql": ["pymysql>=1.0.0"],
        "all": [
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "schemasync=schemasync.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
