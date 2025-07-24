
from projects import ProjectServer
import psiutils as ps

from forms.frm_config import ConfigFrame
from forms.frm_project_versions import ProjectVersionsFrame


class ModuleCaller():
    def __init__(self, root, module) -> None:
        modules = {
            'config': self._config,
            'project': self._project
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
        dlg = ProjectEditFrame(self, ps.EDIT, projects['psiutils'])
        self.root.wait_window(dlg.root)
