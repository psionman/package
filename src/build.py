"""Process the upgrade of the module."""
from contextlib import chdir
import subprocess
import shutil
from pathlib import Path

from projects import Project
from psiutils.constants import DIALOG_STATUS


def update_module(context: dict) -> int:
    project = context['project']
    version = context['version']
    history = context['history']
    test_build = context['test_build']

    if not test_build:
        print('*** Update version ***')
        if project.update_version(version) != DIALOG_STATUS['ok']:
            return DIALOG_STATUS['error']

        print('*** Update pyproject ***')
        if project.update_poetry_version(version) != DIALOG_STATUS['ok']:
            return DIALOG_STATUS['error']

        print('*** Update history ***')
        if project.update_history(history) != DIALOG_STATUS['ok']:
            return DIALOG_STATUS['error']

        if context['delete_build']:
            if _delete_build_dirs(project) != DIALOG_STATUS['ok']:
                return DIALOG_STATUS['error']

    if _build(project) != DIALOG_STATUS['ok']:
        return DIALOG_STATUS['error']

    if _upload(project, test_build) != DIALOG_STATUS['ok']:
        return DIALOG_STATUS['error']

    print('')
    print('***Upload complete ***')
    print('')
    return DIALOG_STATUS['ok']


def _build(project: Project) -> int:
    print('*** Build ***')
    try:
        with chdir(str(project.base_dir)):
            subprocess.call(['uv', 'build'])
    except FileNotFoundError as error:
        print(error)
        print('Build failure')
        return DIALOG_STATUS['error']
    return DIALOG_STATUS['ok']


def _upload(project: Project, test_build: bool = False) -> int:
    """
        The PyPi token is stored in the environmental variable UV_PUBLISH_TOKEN
        the value is kept in Documents/pypi folder
    """
    print('*** Upload ***')
    error_msg = 'Upload failure'
    try:
        with chdir(str(project.base_dir)):
            if test_build:
                proc = subprocess.Popen(['uv', 'publish', '--dry-run'])
            else:
                proc = subprocess.Popen(['uv', 'publish'])
        proc.wait()
        (stdout, stderr) = proc.communicate()

        if proc.returncode != 0:
            print(f'Error! Return code: {proc.returncode}')
            if proc.returncode == 127:
                print('Is poetry installed in this environment?')
            return DIALOG_STATUS['error']
        else:
            print("success")

    except FileNotFoundError as error:
        print(error)
        print(error_msg)
        return DIALOG_STATUS['error']
    return DIALOG_STATUS['ok']


def _delete_build_dirs(project: Project) -> int:
    print('*** Removing build directories ***')
    for dir in [
        'dist',
        'build',
        f'{project.name}.egg-info',
    ]:
        path = Path(project.base_dir, dir)
        if path.is_dir():
            try:
                print(f'Removing {path}')
                shutil.rmtree(path)
            except OSError as error:
                print(f'Error: {path}: {error.strerror}')
                return DIALOG_STATUS['error']
    return DIALOG_STATUS['ok']
