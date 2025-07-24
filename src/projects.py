"""Project data for Compare."""
import os
import json
from pathlib import Path
from datetime import datetime
import re
from typing import NamedTuple

import psiutils as ps
from psiutils.constants import DIALOG_STATUS
from config import config
from constants import (PYPROJECT_TOML, DATA_DIR,
                        HISTORY_FILE, VERSION_FILE, VERSION_TEXT)


class EnvironmentData(NamedTuple):
    name: str
    dir: str
    python_version: str


class EnvironmentVersion():
    def __init__(self, data: EnvironmentData = None) -> None:
        self.name = ''
        self.dir = ''
        self.python_version = ''
        self.type = ''

        if data:
            self.deserialize(data)

        self.version = self._get_version()

    def serialize(self) -> tuple:
        """Return a tuple of the version for json serialization."""
        return (
            self.name,
            str(self.dir),
            self.python_version,
        )

    def deserialize(self, data: list | tuple) -> None:
        """Deserialize the version from json."""
        environ = EnvironmentData(*data)

        self.name = environ.name
        self.dir = environ.dir
        self.python_version = environ.python_version
        self.version = self._get_version()
        self.venv_python = self._get_venv_python()

    def _get_version(self):
        version_re = r'[0-9]{1,}.[0-9]{1,}.[0-9]{1,}'
        path = Path(self.dir, '_version.py')
        try:
            with open(path, 'r', encoding='utf8') as f_version:
                text = f_version.read()
                if match := re.search(version_re, text):
                    return match.group()
        except FileNotFoundError:
            return 'No version file'
        return 'Version error'

    def _get_venv_python(self) -> str:
        parts = Path(self.dir).parts
        if '.venv' in parts:
            index = parts.index('.venv')
            project_dir = Path(*parts[:index])
            return os.path.join(project_dir, '.venv', 'bin', 'python')
        if '.pyenv' in parts:
            index = parts.index('versions')
            project_dir = Path(*parts[:index+2])
            return os.path.join(project_dir, 'bin', 'python')
        return ''


class Project():
    """Project class to support the package module."""

    # base_dir is the base directory containing, e.g. HISTORY.md

    def __init__(self) -> None:
        self.name: str = ''
        self.dev_dir: str = ''
        self.project_dir: str = ''
        self._dev_dir_short: str = ''
        self._project_dir_short: str = ''
        self.dev_version: str = ''
        self.project_version: str = ''
        self.pyproject_version: str = ''
        self._base_dir: Path = None
        self.history = ''
        self.new_history = ''
        self._pyproject_list = []
        self.dev_versions: dict = {}
        self.py_project_missing = True
        # self._version_list = ['__version__ = 0.0.0']

    def __repr__(self) -> str:
        return f'Project: {self.name}'

    @property
    def dev_dir_short(self) -> str:
        return self._short_dir(self.dev_dir)

    @property
    def project_dir_short(self) -> str:
        return self._short_dir(self.project_dir)

    def serialize(self) -> list[str]:
        return [self.project_dir, self.dev_dir]

    @staticmethod
    def _short_dir(dir: str) -> str:
        return dir.replace(str(Path.home()), '~')

    def _get_dev_version(self) -> str:
        return self._get_version_text(Path(self.dev_dir, VERSION_FILE))

    def _get_project_version(self) -> str:
        return self._get_version_text(Path(self.project_dir, VERSION_FILE))

    @property
    def base_dir(self) -> Path:
        if not self._base_dir:
            self._base_dir = Path(self.project_dir).parent
            if not Path(self._base_dir, 'pyproject.toml').is_file():
                self._base_dir = self._base_dir.parent
        return self._base_dir

    @property
    def history_path(self) -> Path:
        return Path(self.base_dir, HISTORY_FILE)

    @property
    def version_path(self) -> Path:
        return Path(self.project_dir, VERSION_FILE)

    @property
    def pyproject_path(self) -> Path:
        return Path(self.base_dir, PYPROJECT_TOML)

    def _get_version_text(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf8') as f_version:
                text = f_version.read()
                for line in text.split('\n'):
                    if VERSION_TEXT in line and '=' in line:
                        version_text = line.split('=')[1]
                        version_text = version_text.strip()
                        version_text = version_text.replace("'", '')
                        return version_text
        except FileNotFoundError:
            return 'Version file missing'
        return 'Version text missing'

    def _get_history(self) -> str:

        try:
            with open(self.history_path, 'r', encoding='utf8') as f_history:
                return f_history.read()
        except FileNotFoundError:
            print(f'History file missing for {self.name}: {self.history_path}')
            return ''

    def _get_new_history(self) -> str:
        history = self.history.split('\n')
        date = datetime.now().strftime('%d %B %Y')
        version = f'Version {self.next_version()} - {date}'
        insertion = ['', version, '', '1. ', '-'*30, '']
        return '\n'.join([history[0]] + insertion + history[2:])

    def next_version(self) -> str:
        version = self.project_version.split('.')
        if 'missing' in version[0]:
            path = Path(self.project_dir, VERSION_FILE)
            print(f' version file missing {path}')
            return ''
        if len(version) != 3:
            print(f'Invalid version (structure) {self.project_version}')
            return ''
        if not version[2].isnumeric():
            print(f'Invalid version (non-numeric) {self.project_version}')
            return ''
        return f'{version[0]}.{version[1]}.{int(version[2]) + 1}'

    @staticmethod
    def _clean_string(text: str) -> str:
        text = text.strip()
        text = text.replace('"', '')
        return text.replace("'", '')

    def _get_pyproject_version(self) -> str:
        default = '-.-.-'
        self.py_project_missing = False
        try:
            with open(
                    self.pyproject_path, 'r', encoding='utf8') as f_pyproject:
                poetry_text = f_pyproject.read()
            self._pyproject_list = poetry_text.split('\n')
            for line in self._pyproject_list:
                if 'version =' in line:
                    line_list = line.split('=')
                    if len(line_list) != 2:
                        err_str = 'pyproject.toml format error in'
                        print(f'{err_str} {self.pyproject_path}')
                        return default
                    return self._clean_string(line_list[1])
            return default
        except FileNotFoundError:
            self.py_project_missing = True
            print(f'pyproject.toml missing {self.pyproject_path}')
        return default

    def get_project_data(self) -> None:
        self.dev_version = self._get_dev_version()
        self.project_version = self._get_project_version()
        self.history = self._get_history()
        self.new_history = self._get_new_history()
        self.pyproject_version = self._get_pyproject_version()

    def update_version(self, version: str) -> int:
        output = f'{VERSION_TEXT} = \'{version}\''
        try:
            with open(self.version_path, 'w', encoding='utf8') as f_version:
                f_version.write(output)
            return DIALOG_STATUS['ok']
        except FileNotFoundError:
            print(f'File missing {self.version_path}')
            return DIALOG_STATUS['error']

    def update_pyproject_version(self, version: str) -> int:
        for index, line in enumerate(self._pyproject_list):
            if 'version =' in line:
                line_list = line.split('=')
                if len(line_list) != 2:
                    print(f'Version format error in {self.version_path}')
                    return DIALOG_STATUS['error']
                version_text = f'{line_list[0].strip()} = "{version}"'

                output = self._pyproject_list[:index]
                output.append(version_text)
                output.extend(self._pyproject_list[index+1:])
                break

        try:
            with open(
                    self.pyproject_path, 'w', encoding='utf8') as f_pyproject:
                f_pyproject.write('\n'.join(output))
            return DIALOG_STATUS['ok']
        except FileNotFoundError:
            print(f'pyproject.toml missing {path}')
            return DIALOG_STATUS['error']

    def update_history(self, history: str) -> int:
        try:
            with open(self.history_path, 'w', encoding='utf8') as f_history:
                f_history.write(history)
            return DIALOG_STATUS['ok']
        except FileNotFoundError:
            print(f'File missing {self.version_path}')
            return DIALOG_STATUS['error']

    def get_versions(
            self, refresh: bool = False) -> list[dict[EnvironmentVersion]]:
        """Return a list of development versions of the project."""
        if not refresh and self.name in config.project_envs:
            return self._get_saved_versions()

        env_versions = {}  # dict of EnvironmentVersion
        versions = []  # paths to envs to ensure no duplication
        names = []  # names of envs to ensure no duplication

        pyenv_dir = Path(Path.home(), '.pyenv', 'versions')
        pyenv_versions = self._get_versions_from_dir(pyenv_dir)

        venv_dir = Path(Path.home(), 'projects')
        venv_versions = self._get_versions_from_dir(venv_dir)

        env_versions = {**pyenv_versions, **venv_versions}
        self._save_versions(env_versions)
        return env_versions

    def _get_saved_versions(self) -> dict:
        env_versions = {}  # dict of EnvironmentVersion
        versions = config.project_envs[self.name]
        for version in versions:
            env_version = EnvironmentVersion(version)
            env_versions[env_version.name] = env_version

        return env_versions

    def _get_versions_from_dir(self, path: str) -> dict:
        env_versions = {}  # dict of EnvironmentVersion
        environment_names = []  # names of envs to ensure no duplication

        for directory, subdirs, files in os.walk(path, followlinks=False):
            del subdirs, files
            project_name_index, environment_index = 0, 0

            if not Path(directory).is_dir():
                continue

            parts = Path(directory).parts
            if '.venv' in parts:
                start_index = parts.index('.venv')
                project_name_index = start_index + 4
                environment_index = start_index - 1
                python_version_index = start_index + 2
            elif '.pyenv' in parts:
                start_index = parts.index('.pyenv')
                project_name_index = start_index + 6
                environment_index = start_index + 2
                python_version_index = start_index + 4
            else:
                continue

            if len(parts) <= project_name_index:
                continue

            if self.name == parts[project_name_index]:
                environment_name = parts[environment_index]
                if environment_name not in environment_names:
                    environment_names.append(environment_name)
                    data = (
                        environment_name,
                        directory,
                        parts[python_version_index])
                    env_versions[environment_name] = EnvironmentVersion(data)
        return env_versions

    def _save_versions(self, env_versions: dict) -> None:
        versions = [version.serialize()
                    for version in env_versions.values()]
        project_envs = config.project_envs
        project_envs[self.name] = versions
        config.update('project_envs', project_envs)
        config.save()


class ProjectServer():
    """Handle projects."""
    def __init__(self) -> None:
        self.project_file =  Path(DATA_DIR, config.project_file)
        self.projects = self._get_projects()

    def _get_projects(self) -> dict[str, Project]:
        project_dict = {}
        project_list = self._read_projects()
        for key, item in project_list.items():
            project = Project()
            project.name = key
            project.project_dir = item[0]
            project_dict[key] = project
            project.get_project_data()
        return project_dict

    def _read_projects(self) -> list[str]:
        try:
            with open(self.project_file, 'r', encoding='utf8') as f_projects:
                try:
                    return json.load(f_projects)
                except json.decoder.JSONDecodeError:
                    return []
        except FileNotFoundError:
            return []

    def save_projects(self, items: dict[str, Project]) -> int:
        output = {project.name: project.serialize()
                  for project in items.values()}
        try:
            with open(self.project_file, 'w', encoding='utf8') as f_projects:
                json.dump(output, f_projects)
                self.projects = self._get_projects()
        except TypeError:
            return ps.ERROR
        return ps.OK
