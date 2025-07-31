import os
import re
from pathlib import Path
from typing import NamedTuple


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
