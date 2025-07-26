import tkinter as tk
from tkinter import messagebox

from psiutils.menus import Menu, MenuItem
from forms.frm_config import ConfigFrame

from constants import AUTHOR, APP_TITLE
from _version import __version__

import text
SPACES = ' '*20


class MainMenu():
    def __init__(self, parent) -> None:
        self.parent = parent
        self.root = parent.root

    def create(self) -> None:
        menubar = tk.Menu()
        self.root['menu'] = menubar

        # File menu
        file_menu = Menu(menubar, self._file_menu_items())
        menubar.add_cascade(menu=file_menu, label='File')

        # Help menu
        help_menu = Menu(menubar, self._help_menu_items())
        menubar.add_cascade(menu=help_menu, label='Help')

    def _file_menu_items(self) -> list:
        return [
            MenuItem(f'{text.CONFIG}{text.ELLIPSIS}', self._config_frame),
            MenuItem(text.QUIT, self._dismiss),
        ]

    def _help_menu_items(self) -> list:
        return [
            MenuItem(f'About{text.ELLIPSIS}', self._show_about),
        ]

    def _config_frame(self) -> None:
        """Display the config frame."""
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _show_about(self) -> None:
        about = (f'{APP_TITLE}\n'
                 f'Version: {__version__}\n'
                 f'Author: {AUTHOR} {SPACES}')
        messagebox.showinfo(title=f'About {APP_TITLE}', message=about)

    # def _new_project(self, *args) -> None:
    #     project = simpledialog.askstring('New project', 'Project name',
    #                                      parent=self.root)
    #     if not project:
    #         return

    #     self.project_list.append(project)
    #     self.project.set(project)
    #     if project not in self.cmb_project['values']:
    #         self.cmb_project['values'] += (project,)
    #     self.projects[project] = ['', '']

    def _dismiss(self) -> None:
        """Quit the application."""
        self.root.destroy()
