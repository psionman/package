import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from psiutils.buttons import ButtonFrame
from psiutils.widgets import clickable_widget
from psiutils.constants import PAD, DIALOG_STATUS
from psiutils.utilities import window_resize, geometry

from package.config import config, read_config
from package import logger

from package.build import update_module
from package.text import Text

txt = Text()

FRAME_TITLE = 'Build package'


class BuildFrame():
    def __init__(self, parent, project):
        # pylint: disable=no-member)
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = read_config()

        self.project = project

        # tk variables
        self.project_name = tk.StringVar(value=project.name)
        self.current_version = tk.StringVar(value=project.project_version)
        self.pyproject_version = tk.StringVar(value=project.pyproject_version)
        self.new_version = tk.StringVar(value=project.next_version())
        self.history = tk.StringVar(value=project.new_history)
        self.delete_build = tk.IntVar(value=1)
        self.status = tk.StringVar()
        self.test_build = tk.BooleanVar(value=False)

        if os.getcwd() != self.project.project_dir:
            self.status.set(txt.NOT_IN_PROJECT_DIR)

        self.button_frame = None
        self.history_text = None

        self._show()

    def _show(self) -> None:
        # pylint: disable=no-member)
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.transient(self.parent.root)
        root.title(FRAME_TITLE)

        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=1, column=0, sticky=tk.NSEW)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=9, column=0, sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(row=99, column=2, sticky=tk.SE)

        if config.last_project:
            self.button_frame.enable()

    def _main_frame(self, container: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(container)
        frame.rowconfigure(4, weight=1)
        frame.columnconfigure(3, weight=1)

        label = ttk.Label(frame, text='Project')
        label.grid(row=0, column=0, sticky=tk.E, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.project_name,
                          state='readonly')
        entry.grid(row=0, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        clickable_widget(entry)

        label = ttk.Label(frame, text='Current version')
        label.grid(row=1, column=0, sticky=tk.E, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.current_version,
            state='readonly'
            )
        entry.grid(row=1, column=1, sticky=tk.W, padx=PAD, pady=PAD)

        label = ttk.Label(frame, text='pyproject version')
        label.grid(row=2, column=0, sticky=tk.E, padx=PAD)
        entry = ttk.Entry(
            frame,
            textvariable=self.pyproject_version,
            state='readonly',
            )
        if self.current_version.get() != self.pyproject_version.get():
            entry['foreground'] = 'red'
        entry.grid(row=2, column=1, sticky=tk.W, padx=PAD, pady=PAD)

        label = ttk.Label(frame, text='New version')
        label.grid(row=1, column=2, sticky=tk.W, padx=PAD)
        entry = ttk.Entry(frame, textvariable=self.new_version)
        entry.grid(row=1, column=3, sticky=tk.W, padx=PAD, pady=PAD)

        check_button = tk.Checkbutton(frame, text='Test build',
                                      variable=self.test_build)
        check_button.grid(row=3, column=1, sticky=tk.W)

        self.history_text = tk.Text(frame)
        self.history_text.insert('1.0', self.history.get())
        self.history_text.grid(row=4, column=0, columnspan=4, sticky=tk.NSEW,
                               padx=PAD, pady=PAD)

        checkbutton = tk.Checkbutton(
            frame,
            text='Delete all "build" files',
            variable=self.delete_build
            )
        checkbutton.grid(row=5, column=0, sticky=tk.W)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        """Create button row."""
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('build', self._build, True),
            frame.icon_button('exit', self._dismiss),
        ]
        frame.disable()
        return frame

    def _build(self, *args) -> None:
        context = {
            'project': self.project,
            'delete_build': self.delete_build.get(),
            'version': self.new_version.get(),
            'current_version': self.current_version.get(),
            'history': self.history_text.get('1.0', 'end'),
            'current_history': self.project.history,
            'test_build': self.test_build.get(),
        }
        if update_module(context) == DIALOG_STATUS['ok']:
            messagebox.showinfo(
                'Module update',
                'Module updated',
                parent=self.root
            )
        else:
            logger.warning(
                "Build process error",
                project=self.project.name,
            )
            messagebox.showerror(
                'Module update',
                'Module not updated',
                parent=self.root
            )
        self._dismiss()

    def _dismiss(self):
        self.root.destroy()
