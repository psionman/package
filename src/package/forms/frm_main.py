
"""MainFrame for Package compare."""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import subprocess

import psiutils as ps
from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame, Button, IconButton
from psiutils.treeview import sort_treeview
from psiutils.menus import Menu, MenuItem
from psiutils.utilities import window_resize, geometry

from projects import ProjectServer
from config import get_config
import text

from main_menu import MainMenu
from forms.frm_project_edit import ProjectEditFrame
from forms.frm_project_versions import ProjectVersionsFrame

FRAME_TITLE = 'Package update and build'

TREE_COLUMNS = (
    ('name', 'Project', 50),
    ('main', 'project dir', 400),
)


class MainFrame():
    def __init__(self, parent):
        self.root = parent.root
        self.parent = parent
        self.config = get_config()

        self.project_server = ProjectServer()
        self.projects = self.project_server.projects
        self.project = None
        # tk variables

        self.show()

    def show(self):
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.title(FRAME_TITLE)
        root.bind('<Control-x>', self.dismiss)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=0, column=1, rowspan=9,
                               sticky=tk.NS, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(column=1, sticky=tk.SE)

        self.context_menu = self._context_menu()

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.tree = self._get_tree(frame)
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self._populate_tree()

        return frame

    def _get_tree(self, master: tk.Frame) -> ttk.Treeview:
        """Return  a tree widget for events."""
        tree = ttk.Treeview(
            master,
            selectmode='browse',
            height=15,
            show='headings',
            )
        tree.bind('<<TreeviewSelect>>', self._tree_clicked)
        tree.bind('<Button-3>', self._show_context_menu)

        col_list = tuple(col[0] for col in TREE_COLUMNS)
        tree['columns'] = col_list
        for col in TREE_COLUMNS:
            (col_key, col_text, col_width) = (col[0], col[1], col[2])
            tree.heading(col_key, text=col_text,
                         command=lambda c=col_key:
                         sort_treeview(tree, c, False))
            tree.column(col_key, width=col_width, anchor=tk.W)
        # tree.column(<'right-align-column-name'>, stretch=0, anchor=tk.E)
        return tree

    def _populate_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        projects = {key: self.projects[key]
                    for key in sorted(self.projects.keys())}
        for project in projects.values():
            values = (project.name,
                      project.project_dir_short,)
            item = self.tree.insert('', 'end', values=values)

            if self.project and project.name == self.project.name:
                self.tree.selection_set(item)
            elif self.config.last_project == project.name:
                self.tree.selection_set(item)

    def _tree_clicked(self, *args) -> None:
        if values := self.tree.item(self.tree.selection())['values']:
            self.project = self.projects[values[0]]
            self.button_frame.enable(True)
            self.context_menu.enable(True)

            self.config.update('last_project', values[0])
            self.config.save()

    def _show_context_menu(self, event) -> None:
        self.context_menu.tk_popup(event.x_root, event.y_root)
        selected_item = self.tree.identify_row(event.y)
        self.tree.selection_set(selected_item)

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.VERTICAL)
        frame.buttons = [
            frame.icon_button('new', False, self._new_project),
            frame.icon_button('edit', True, self._edit_project),
            frame.icon_button('code', True, self._open_code),
            frame.icon_button('compare', True, self._compare_project),
            frame.icon_button('refresh', True, self._refresh_project),
            frame.icon_button('delete', True, self._delete_project),
            frame.icon_button('close', False, self.dismiss),
        ]
        frame.enable(False)
        return frame

    def _context_menu(self) -> tk.Menu:
        menu_items = [
            MenuItem(text.NEW, self._new_project, dimmable=False),
            MenuItem(text.EDIT, self._edit_project, dimmable=True),
            MenuItem(text.CODE, self._open_code, dimmable=True),
            MenuItem(text.COMPARE, self._compare_project, dimmable=True),
            MenuItem(text.REFRESH, self._refresh_project, dimmable=True),
            MenuItem(text.DELETE, self._delete_project, dimmable=True),
        ]
        context_menu = Menu(self.root, menu_items)
        context_menu.enable(False)
        return context_menu

    def _new_project(self, *args) -> None:
        dlg = ProjectEditFrame(self, ps.NEW)
        self.root.wait_window(dlg.root)
        self._update_projects(dlg)

    def _edit_project(self, *args) -> None:
        dlg = ProjectEditFrame(self, ps.EDIT, self.project)
        # self._populate_tree()
        self.root.wait_window(dlg.root)
        self._update_projects(dlg)

    def _compare_project(self, refresh: bool = False) -> None:
        dlg = ProjectVersionsFrame(self, ps.EDIT, self.project, refresh)
        # self._populate_tree()
        self.root.wait_window(dlg.root)
        self._update_projects(dlg)

    def _refresh_project(self, *args) -> None:
        self._compare_project(True)

    def _delete_project(self, *args) -> None:
        dlg = messagebox.askyesno(
            'Delete project',
            f'Are you sure you want to delete {self.project.name}?',
            parent=self.root,
        )
        if dlg is False:
            return
        del self.projects[self.project.name]
        self._save_projects()

    def _update_projects(self, dlg: ttk.Frame) -> None:
        if dlg.status != ps.UPDATED:
            return
        self.projects[dlg.project.name] = dlg.project
        self._save_projects()

    def _save_projects(self) -> None:
        result = self.project_server.save_projects(self.projects)
        if result == ps.ERROR:
            messagebox.showerror(
                'Save',
                'Save failed',
                parent=self.root
            )
            return
        self._populate_tree()

    def _open_code(self, *args) -> None:
        subprocess.call(['codium', '-n', self.project.base_dir])

    def dismiss(self, *args) -> None:
        self.root.destroy()
