
"""ProjectEditFrame  for <application>."""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import psiutils as ps
from psiutils.constants import PAD
from psiutils.buttons import ButtonFrame, Button, IconButton
from psiutils.utilities import window_resize, geometry

from projects import Project, EnvironmentVersion
from config import get_config
from compare import compare
import text

from forms.frm_compare import CompareFrame
from forms.frm_build import BuildFrame

FRAME_TITLE = 'Project compare versions'

DEFAULT_DEV_DIR = str(Path(Path.home(), '.pyenv', 'versions'))
DEFAULT_PROJECT_DIR = str(Path(Path.home(), 'projects'))

VERSION = 5
PYTHON_VERSION = 7
PROJECT = 9


class ProjectEditFrame():
    def __init__(self, parent, mode: int, project: Project = None) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = get_config()
        self.mode = mode
        self.project = project
        self.projects = parent.projects
        if project:
            project.dev_versions: list = project.get_versions()

        self.status = ps.NULL

        if not project:
            project = Project()
            project.dev_dir = DEFAULT_DEV_DIR
            project.project_dir = DEFAULT_PROJECT_DIR
        self.project = project

        # tk variables
        self.project_name = tk.StringVar(value=project.name)
        self.dev_dir = tk.StringVar(value=project.dev_dir)
        self.project_dir = tk.StringVar(value=project.project_dir)
        self.project_version = tk.StringVar(value=self.project.version_text)
        self.version = tk.StringVar()

        # Trace
        self.project_name.trace_add('write', self._values_changed)
        self.dev_dir.trace_add('write', self._values_changed)
        self.project_dir.trace_add('write', self._values_changed)
        self.version.trace_add('write', self._values_changed)

        self.show()

    def show(self) -> None:
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.title(FRAME_TITLE)
        root.transient(self.parent.root)
        root.bind('<Control-x>', self._dismiss)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(8, weight=1)
        frame.columnconfigure(2, weight=1)

        label = ttk.Label(frame, text='Project name')
        label.grid(row=0, column=0, sticky=tk.E, pady=PAD)

        state = 'readonly' if self.mode == ps.EDIT else 'normal'
        entry = ttk.Entry(frame, textvariable=self.project_name, state=state)
        entry.grid(row=0, column=1, sticky=tk.EW, padx=PAD)
        entry.focus_set()

        label = ttk.Label(frame, text='(Used to find dirs in virtual envs)')
        label.grid(row=1, column=1, sticky=tk.W, pady=0)

        label = ttk.Label(frame, text='Current_version')
        label.grid(row=2, column=0, sticky=tk.E, pady=PAD)

        entry = ttk.Entry(
            frame, textvariable=self.project_version, state='readonly')
        entry.grid(row=2, column=1, sticky=tk.EW, padx=PAD)

        label = ttk.Label(frame, text='Project dir')
        label.grid(row=3, column=0, sticky=tk.E, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.project_dir)
        entry.grid(row=3, column=1, columnspan=2, padx=PAD, sticky=tk.EW)

        # button = ttk.Button(frame, text=text.ELLIPSIS,
        #                     command=self._get_project_dir)
        button = IconButton(
            frame, text.OPEN, 'open', self._get_project_dir)
        button.grid(row=3, column=3)

        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=0, column=4, rowspan=9,
                               sticky=tk.NS, padx=PAD, pady=PAD)
        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.VERTICAL)
        frame.buttons = [
            frame.icon_button('save', True, self._save),
            frame.icon_button('exit', False, self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _get_project_dir(self, *args) -> None:
        if directory := filedialog.askdirectory(
                initialdir=self.project_dir.get(),
                parent=self.root,):
            self.project_dir.set(directory)

    def _values_changed(self, *args) -> None:
        enable = bool(self.project_name.get())
        self.button_frame.enable(enable)

    def _save(self, *args) -> None:
        if self.mode == ps.NEW:
            self.project = Project()
            self.project.name = self.project_name.get()
        self.project.project_dir = self.project_dir.get()
        self.parent.project_server.save_projects(self.projects)
        self.project_version.set(self.project.version_text)
        self.status = ps.UPDATED
        self._dismiss()

    def _compare_project(self) -> None:
        if not Path(self.project.dev_dir).is_dir():
            messagebox.showerror(
                'Path error',
                f'{self.project.dev_dir} \nis not a directory!',
                parent=self.root,
            )
            return
        self.project.dev_dir = self.version.get()
        dlg = CompareFrame(self, self.project)
        self.root.wait_window(dlg.root)
        for widget in self.versions_frame.winfo_children():
            widget.destroy()
        self._populate_versions_frame()

    def _build_project(self, *args) -> None:
        dlg = BuildFrame(self, self.project)
        self.root.wait_window(dlg.root)

    def _dismiss(self, *args) -> None:
        self.root.destroy()
