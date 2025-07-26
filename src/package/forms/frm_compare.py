"""Main frame for ..."""
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import shutil

from psiutils.constants import PAD, PADB
from psiutils.utilities import window_resize, geometry
from psiutils.buttons import ButtonFrame, Button, IconButton

from compare import compare
from config import get_config

import text
from projects import Project

FRAME_TITLE = 'Compare files across directories'


class CompareFrame():
    """Define the Main frame."""
    def __init__(
            self, parent: ttk.Frame, project: Project) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.project = project

        self.config = get_config()

        # Tk Variables
        self.project_name = tk.StringVar(value=project.name)
        self.dev_dir = tk.StringVar(value=project.dev_dir_short)
        self.project_dir = tk.StringVar(value=project.project_dir_short)
        self.dev_version = tk.StringVar(value=project.dev_version)
        self.project_version = tk.StringVar(value=project.project_version)
        self.mismatch = tk.StringVar(value='')
        self.show()

        self.destroy_widgets = []
        self.compare_project()

    def show(self):
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.transient(self.parent.root)
        root.bind('<Control-x>', self._dismiss)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.root.title(f'{FRAME_TITLE}')

        project_frame = self._project_frame(self.root)
        project_frame.grid(row=0, column=0, sticky=tk.EW, padx=PAD, pady=PAD)

        self.missing_frame = ttk.Frame(self.root)
        self.missing_frame.grid(row=2, column=0, sticky=tk.NW, pady=PAD)

        self.buttons = self._button_frame(self.root)
        self.buttons.grid(row=998, column=0, sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(self.root)
        sizegrip.grid(row=999, sticky=tk.SE)

    def _project_frame(self, container: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(container)
        frame.columnconfigure(2, weight=1)

        label = ttk.Label(frame, text='Project')
        label.grid(row=0, column=0, sticky=tk.E)

        entry = ttk.Entry(frame, textvariable=self.project_name,
                          state='readonly')
        entry.grid(row=0, column=1, sticky=tk.EW, padx=PAD)

        label = ttk.Label(frame, text='Dev version')
        label.grid(row=1, column=0, sticky=tk.E)

        entry = ttk.Entry(frame, textvariable=self.dev_version,
                          state='readonly')
        entry.grid(row=1, column=1, sticky=tk.EW, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.dev_dir, state='readonly')
        entry.grid(row=1, column=2, sticky=tk.EW, padx=PAD)

        label = ttk.Label(frame, text='Project version')
        label.grid(row=2, column=0, sticky=tk.E)

        entry = ttk.Entry(frame, textvariable=self.project_version,
                          state='readonly')
        entry.grid(row=2, column=1, sticky=tk.EW, padx=PAD)

        entry = ttk.Entry(frame, textvariable=self.project_dir,
                          state='readonly')
        entry.grid(row=2, column=2, sticky=tk.EW, padx=PAD)

        return frame

    def _main_frame(self) -> ttk.Frame:
        frame = ttk.Frame(self.root)
        frame.rowconfigure(0, weight=1)
        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('diff', True, self.show_diff),
            frame.icon_button('exit', False, self._dismiss),
        ]
        frame.enable(False)
        return frame

    def compare_project(self) -> None:
        """Destroy and recreate widgets based on comparison."""
        (missing, mismatches) = compare(
            self.project.project_dir, self.project.dev_dir)

        for item in self.destroy_widgets:
            item.destroy()

        frame = ttk.Frame(self.missing_frame)
        frame.grid(row=0, column=0, padx=PAD)
        self.destroy_widgets.append(frame)

        self.missing_file_frame = self._missing_frame(frame, missing)
        self.missing_file_frame.grid(row=0, column=0)
        self.destroy_widgets.append(self.missing_file_frame)

        mismatch_frame = self._mismatch_frame(frame, mismatches)
        mismatch_frame.grid(row=1, column=0, sticky=tk.W)
        self.destroy_widgets.append(mismatch_frame)

    def _missing_frame(self, container: ttk.Frame,
                       missing: list[tuple]) -> ttk.Frame:
        frame = ttk.Frame(container)
        frame.grid(row=9, column=0, padx=PAD)
        self.destroy_widgets.append(frame)

        label = ttk.Label(
            frame, text=' Missing files and dirs', style='blue-fg.TLabel')
        label.grid(row=0, column=0, sticky=tk.W)
        self.destroy_widgets.append(label)

        if not missing:
            label = ttk.Label(frame, text='None')
            label.grid(row=1, column=0)
            self.destroy_widgets.append(label)
            return frame

        label = ttk.Label(frame, text='Env dir')
        label.grid(row=1, column=0, sticky=tk.W)
        self.destroy_widgets.append(label)

        label = ttk.Label(frame, text='Project dir')
        label.grid(row=1, column=1, sticky=tk.W)
        self.destroy_widgets.append(label)

        row = 2
        for missing_files in missing:
            label = self._missing_file_label(frame, row, missing_files[0])
            label.grid(row=row, column=0, padx=PAD, sticky=tk.W)

            label = self._missing_file_label(frame, row, missing_files[1])
            label.grid(row=row, column=1, sticky=tk.W)

            if missing_files[0]:
                # button = ttk.Button(frame, text=text.COPY)
                button = IconButton(frame, text.COPY, 'copy_docs')
                button.grid(row=row, column=2, padx=PAD, pady=PADB)
                button.widget.bind(
                    '<Button-1>', lambda event, arg=None:
                    self._copy_file(missing_files[0]))

            row += 1
        return frame

    def _missing_file_label(self, frame: ttk.Frame, row: int,
                            file_name: str) -> ttk.Label:
        style = ''
        if not file_name:
            file_name = '-- missing --'
            style = 'red-fg.TLabel'
        label = ttk.Label(frame, text=file_name, style=style)
        self.destroy_widgets.append(label)
        return label

    def _mismatch_frame(self, container: ttk.Frame,
                        mismatches: list[str]) -> ttk.Frame:
        frame = ttk.Frame(container)
        frame.grid(row=9, column=0, padx=PAD)
        self.destroy_widgets.append(frame)

        label = ttk.Label(frame, text=' Mismatches', style='blue-fg.TLabel')
        label.grid(row=0, column=0, sticky=tk.W)
        self.destroy_widgets.append(label)

        if not mismatches:
            label = ttk.Label(frame, text='None')
            label.grid(row=1, column=0)
            self.destroy_widgets.append(label)
            return frame

        row = 2
        for item in mismatches:
            button = ttk.Radiobutton(
                frame,
                text=item,
                value=item,
                variable=self.mismatch,
                command=self.rb_selected
            )
            button.grid(row=row, column=0, sticky=tk.W)
            self.destroy_widgets.append(button)
            row += 1

        return frame

    def rb_selected(self, *args) -> None:
        self.buttons.enable(True)

    def show_diff(self, *args) -> None:
        file = self.mismatch.get()
        paths = [
            str(Path(self.project.dev_dir, file)),
            str(Path(self.project.project_dir, file)),
        ]

        self.root.withdraw()
        subprocess.run(['meld', *paths])
        self.root.deiconify()
        if self.dev_dir.get() and self.project_dir.get():
            self.compare_project()

    def _copy_file(self, file_name: str) -> None:
        source = Path(self.project.dev_dir, file_name)

        item = 'file'
        if source.is_dir():
            item = 'directory'
        dlg = messagebox.askokcancel(
            '', f'Copy this {item}?', parent=self.root)
        if not dlg:
            return

        destination = Path(self.project.project_dir, file_name)

        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copyfile(source, destination)

        for widget in self.missing_file_frame.winfo_children():
            widget.destroy()
        self.compare_project()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
