from psiconfig import TomlConfig

from constants import CONFIG_PATH, DATA_DIR


DEFAULT_CONFIG = {
    'data_directory': DATA_DIR,
    'last_project': '',
    'project_file': 'projects.json',
    'project_envs': '[]',
    'ignore': [],
    'geometry': {
        'frm_main': '1400x600',
        'frm_config': '800x200',
        'frm_build': '700x900',
        'frm_compare': '1100x900',
        'frm_project': '800x400',
    },
}


def get_config() -> TomlConfig:
    """Return the config file."""
    return TomlConfig(path=CONFIG_PATH, defaults=DEFAULT_CONFIG)


def save_config(config: TomlConfig) -> TomlConfig | None:
    result = config.save()
    if result != config.STATUS_OK:
        return None
    config = TomlConfig(CONFIG_PATH)
    return config


config = get_config()
