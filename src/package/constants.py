"""Constants for Project Compare"""
from pathlib import Path
from appdirs import user_config_dir, user_data_dir


PROJECT_DIR = Path(__file__).parent.parent

# Config
APP_NAME = 'package_build'
APP_TITLE = 'Package update and build'
AUTHOR = 'Jeff Watkins'
ICON_FILE = Path(PROJECT_DIR, 'dist', 'favicon.png')

CONFIG_PATH = Path(user_config_dir(APP_NAME, AUTHOR), 'config.toml')
DATA_DIR = str(Path(user_data_dir(APP_NAME, AUTHOR)))

HISTORY_FILE = 'HISTORY.md'
VERSION_FILE = '_version.py'
VERSION_TEXT = '__version__'

PYPROJECT_TOML = 'pyproject.toml'
