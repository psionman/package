
import json

import psiutils as ps
from psiutils.constants import DIALOG_STATUS

from package.constants import VERSION_TEXT


def _open_text_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf8') as f_text:
            return f_text.read()
    except FileNotFoundError:
        return ''


def get_raw_version_text(path: str) -> str:
    return _open_text_file(path)


def get_history(project_name: str, history_path: str) -> str:
    text = _open_text_file(history_path)
    if not text:
        print(f'History missing for {project_name}: {history_path}')
    return text


def get_pyproject_version_text(pyproject_path: str) -> str:
    text = _open_text_file(pyproject_path)
    if not text:
        print(f'pyproject.toml missing {pyproject_path}')
    return text


def update_version_file(version_path: str, version: str) -> int:
    output = f'{VERSION_TEXT} = \'{version}\''
    try:
        with open(version_path, 'w', encoding='utf8') as f_version:
            f_version.write(output)
        return DIALOG_STATUS['ok']
    except FileNotFoundError:
        print(f'File missing {version_path}')
        return DIALOG_STATUS['error']



def update_pyproject_file(pyproject_path: str, output: str) -> int:
    try:
        with open(
                pyproject_path, 'w', encoding='utf8') as f_pyproject:
            f_pyproject.write('\n'.join(output))
        return DIALOG_STATUS['ok']
    except FileNotFoundError:
        print(f'pyproject.toml missing {pyproject_path}')
        return DIALOG_STATUS['error']


def update_history_file(history_path: str, history: str) -> int:
    try:
        with open(history_path, 'w', encoding='utf8') as f_history:
            f_history.write(history)
        return DIALOG_STATUS['ok']
    except FileNotFoundError:
        print(f'File missing {history_path}')
        return DIALOG_STATUS['error']


def get_projects(project_file) -> dict:
    try:
        with open(project_file, 'r', encoding='utf8') as f_projects:
            try:
                return json.load(f_projects)
            except json.decoder.JSONDecodeError:
                return {}
    except FileNotFoundError:
        return {}


def save_project_file(project_file:  str, output: dict) -> int:
    try:
        with open(project_file, 'w', encoding='utf8') as f_projects:
            json.dump(output, f_projects)
    except FileNotFoundError as exc:
        print(f'Project file not found: {project_file}')
