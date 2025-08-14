"""Process the upgrade of the module."""
from contextlib import chdir
import os
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

from psiutils.constants import DIALOG_STATUS

from package.psilogger import logger
from package.projects import Project


load_dotenv()
os.environ["UV_PUBLISH_TOKEN"] = os.getenv("UV_PUBLISH_TOKEN")


def update_module(context: dict) -> int:

    project = context['project']
    logger.info(
        "Starting build process",
        project=project.name,
    )

    if not context['test_build']:
        if _update_version(project, context['version']) != DIALOG_STATUS['ok']:
            return DIALOG_STATUS['error']

        if project.update_history(context['history']) != DIALOG_STATUS['ok']:
            return DIALOG_STATUS['error']
        logger.info(
            "Update history",
            project=project.name,
        )

        if (context['delete_build']
                and _delete_build_dirs(project) != DIALOG_STATUS['ok']):
            return DIALOG_STATUS['error']

    if _build(project) != DIALOG_STATUS['ok']:
        _restore_project(context)
        return DIALOG_STATUS['error']

    if _upload(project, context['test_build']) != DIALOG_STATUS['ok']:
        _restore_project(context)
        return DIALOG_STATUS['error']
    return DIALOG_STATUS['ok']


def _update_version(project: Project, version: str) -> int:
    if project.update_version(version) != DIALOG_STATUS['ok']:
        return DIALOG_STATUS['error']
    logger.info(
        "Update version",
        project=project.name,
        version=version
    )

    if project.update_pyproject_version(version) != DIALOG_STATUS['ok']:
        return DIALOG_STATUS['error']
    logger.info(
        "Update pyproject version",
        project=project.name,
        version=version
    )

    return DIALOG_STATUS['ok']


def _restore_project(context: dict) -> None:
    logger.info(
        "Restoring project",
        project=project.name,
    )
    project = context['project']
    _update_version(project, context['current_version'])
    project.update_history(context['current_history'])


def _build(project: Project) -> int:
    try:
        with chdir(str(project.base_dir)):
            subprocess.call(['uv', 'build'])
    except FileNotFoundError as error:
        logger.warning(
            "Build failed",
            error=error,
        )
        return DIALOG_STATUS['error']
    logger.info(
        "Build project",
        project=project.name,
    )
    return DIALOG_STATUS['ok']


def _upload(project: Project, test_build: bool = False) -> int:
    """
        The PyPi token is stored in the environmental variable UV_PUBLISH_TOKEN
        the value is kept in Documents/pypi folder
    """
    try:
        with chdir(str(project.base_dir)):
            if test_build:
                proc = subprocess.Popen(['uv', 'publish', '--dry-run'])
            else:
                proc = subprocess.Popen(['uv', 'publish'])
        proc.wait()
        (stdout, stderr) = proc.communicate()
        del stdout, stderr

        if proc.returncode == 0:
            logger.info(
                "Package uploaded",
                project=project.name,
            )
        else:
            print(f'Error! Return code: {proc.returncode}')
            logger.exception(
                f'Error! Return code: {proc.returncode}',
                project=project.name,
                )
            return DIALOG_STATUS['error']

    except FileNotFoundError as error:
        logger.exception(
            f'Error! {error}',
            project=project.name,
            )
        return DIALOG_STATUS['error']
    return DIALOG_STATUS['ok']


def _delete_build_dirs(project: Project) -> int:
    logger.info(
        "Removing build directories",
        project=project.name,
    )
    for build_dir in [
        'dist',
        'build',
        f'{project.name}.egg-info',
    ]:
        path = Path(project.base_dir, build_dir)
        if path.is_dir():
            try:
                shutil.rmtree(path)
                logger.info(
                    "Removing path",
                    project=project.name,
                    path=str(path),
                )
            except OSError:
                logger.exception(f'Failed to remove {path}')
                return DIALOG_STATUS['error']
    return DIALOG_STATUS['ok']
