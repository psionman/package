
import os
from pathlib import Path
import re

from package import logger


TEST_DIR = '/home/jeff/projects/utilities/windows-converter/src/windows_converter'


def check_imports(base_dir: str) -> None:
    modules = _get_modules(base_dir)
    for path in modules.values():
        text = _get_text(path)
        _check_imports(list(modules), path.stem, text)


def _get_modules(module_dir: str) -> dict:
    modules = {}
    for directory_name, subdir_list, file_list in os.walk(module_dir):
        del subdir_list
        for file_name in file_list:
            file_path = Path(directory_name, file_name)
            if file_path.suffix == '.py':
                modules[file_path.stem] = file_path
    return modules


def _get_text(path: str) -> list:
    with open(path, 'r', encoding='utf-8') as f_module:
        return f_module.read().split('\n')


def _check_imports(modules: list, module_name: str, text: list) -> None:
    starts_with = ('from', 'import')
    for index, line in enumerate(text):
        import_line = any(line.startswith(start) for start in starts_with)
        if not import_line:
            continue
        for module in modules:
            module_re = rf'\b{module}\b'
            if re.search(module_re, line) and '.' not in line:
                print(module_name, module, line)
                logger.warning(f'Missing module in {module_name}: {index+1}')


if __name__ == "__main__":
    check_imports(TEST_DIR)
