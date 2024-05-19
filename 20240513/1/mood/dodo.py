#!/usr/bin/env python3

from doit.tools import create_folder
from doit.task import clean_targets
import shutil


DOIT_CONFIG = {"default_tasks": ["html"]}


def task_po():
    return {
        "actions": [
            "pybabel extract -o ./moodserver/moodserver/server.pot ./moodserver/moodserver/server.py",
        ],
        "file_dep": [
            "./moodserver/moodserver/server.py",
        ],
        "targets": [
            "server.po",
        ],
        "clean": True,
    }


def task_pot():
    return {
        "actions": [
            "pybabel update -D server -d ./moodserver/moodserver/po -i ./moodserver/moodserver/server.pot -l ru",
        ],
        "task_dep": [
            "po",
        ],
        "targets": [
            "server.pot",
        ],
        "clean": True,
    }


def task_mo():
    return {
        "actions": [
            "pybabel compile -D server -d ./moodserver/moodserver/po -l ru",
        ],
        "task_dep": [
            "pot",
        ],
        "targets": [
            "server.mo",
        ],
        "clean": True,
    }


def task_i18n():
    return {
        "actions": [],
        "task_dep": [
            "mo",
        ],
    }


def task_html():
    return {
        "actions": ["sphinx-build -M html doc build"],
        "clean": [clean_targets, lambda: shutil.rmtree("build")],
    }


def task_test():
    return {
        "actions": ["python3 -m unittest -v test.py"],
        "task_dep": [
            "i18n",
        ],
    }


def task_whlserver():
    return {
        "actions": ["python3 -m build ./moodserver -w -n"],
        "file_dep": [
            "./moodserver/pyproject.toml",
        ],
    }


def task_whlclient():
    return {
        "actions": ["python3 -m build ./moodclient -w -n"],
        "file_dep": [
            "./moodclient/pyproject.toml",
        ],
    }


def task_wheels():
    return {
        "actions": [],
        "task_dep": [
            "whlserver",
            "whlclient"
        ],
    }