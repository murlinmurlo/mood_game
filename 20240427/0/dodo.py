def task_extract():
    return {
        "actions": ["pybabel extract -o wc.pot wc.py"],
        "file_dep": ["wc.py"],
        "targets": ["wc.pot"],
    }

def task_update():
    return {
        "actions": ["pybabel update -D wc -d po -i wc.pot"],
        "file_dep": ["wc.pot"],
        "targets": ["po/ru_RU.UTF-8/LC_MESSAGES/wc.po"],
    }

def task_compile():
    return {
        "actions": ["pybabel compile -D wc -d po -l ru_RU.UTF-8"],
        "file_dep": ["po/ru_RU.UTF-8/LC_MESSAGES/wc.po"],
        "targets": ["po/ru_RU.UTF-8/LC_MESSAGES/wc.mo"],
    }
