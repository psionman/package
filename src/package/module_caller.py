import sys

from psiutils.constants import Mode

from package.projects import ProjectServer
from package.forms.frm_config import ConfigFrame
# from package.forms.frm_project_versions import ProjectVersionsFrame
from package.forms.frm_search import SearchFrame


class ModuleCaller():
    def __init__(self, root, module) -> None:
        modules = {
            'config': self._config,
            'project': self._project,
            'search': self._search
            }
        self.projects = ProjectServer().projects

        self.invalid = False
        if module == '-h':
            for key in sorted(list(modules.keys())+['main']):
                print(key)
            self.invalid = True
            return

        if module not in modules:
            if module != 'main':
                print(f'*** Invalid function name: {module} ***')
            self.invalid = True
            return

        self.root = root
        modules[module]()
        self.root.destroy()
        return

    def _config(self) -> None:
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _project(self) -> None:
        dlg = ProjectEditFrame(self, Mode.EDIT, projects['psiutils'])
        self.root.wait_window(dlg.root)

    def _search(self) -> None:
        search_term = ''
        if len(sys.argv) > 2:
            search_term = sys.argv[2]
        dlg = SearchFrame(self, search_term)
        self.root.wait_window(dlg.root)
