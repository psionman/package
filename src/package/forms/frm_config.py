"""Tkinter frame for config maintenance."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from psiutils.buttons import Button, ButtonFrame, IconButton
from psiutils.constants import PAD
from psiutils.utilities import window_resize, geometry

from constants import APP_TITLE
from config import config, save_config, get_config
import text

LF = '\n'


class ConfigFrame():
    def __init__(self, parent):
        self.root = tk.Toplevel(parent.root)
        self.config = get_config()
        self.parent = parent
        self.ignore_text = None

        self.data_directory = tk.StringVar(value=config.data_directory)

        self.data_directory.trace_add('write', self._check_value_changed)

        self.show()

    def show(self):
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.title(text.CONFIG)

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-s>', self._save_config)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.wait_visibility()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)

        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(1, weight=1)

        row = 0
        label = ttk.Label(frame, text="Data directory:")
        label.grid(row=0, column=0, sticky=tk.E)

        directory = ttk.Entry(frame,
                              textvariable=self.data_directory)
        directory.grid(row=row, column=1, columnspan=1, sticky=tk.EW,
                       padx=PAD, pady=PAD)

        # select = ttk.Button(frame, text=f'{text.SELECT}{text.ELLIPSIS}',
        #                     command=self._set_data_directory)
        select = IconButton(frame, text=text.OPEN, icon='open',
                            command=self._set_data_directory)
        select.grid(row=row, column=2, sticky=tk.W, padx=PAD)

        row += 1
        label = ttk.Label(frame, text='Ignore')
        label.grid(row=row, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        row += 1
        self.ignore_text = tk.Text(frame, height=20)
        self.ignore_text.grid(row=row, column=0, columnspan=3,
                              sticky=tk.NSEW, padx=PAD)
        self.ignore_text.insert('0.0', '\n'.join(self.config.ignore))
        self.ignore_text.bind('<KeyRelease>', self._check_value_changed)

        row += 1
        self.button_frame = self._button_frame(frame)
        self.button_frame.grid(row=row, column=0, columnspan=3,
                          sticky=tk.EW, padx=PAD, pady=PAD)
        self.button_frame.disable()
        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('save', True, self._save_config),
            frame.icon_button('exit', False, self._dismiss),
        ]
        frame.grid(row=0, column=0, sticky=tk.EW)
        return frame

    def _value_changed(self, *args) -> bool:
        ignore_text = self.ignore_text.get('0.0', tk.END)
        return (
            self.data_directory.get() != self.config.data_directory or
            ignore_text != '\n'.join(self.config.ignore) or
            ...
        )

    def _check_value_changed(self, *args) -> None:
        enable = bool(self._value_changed())
        self.button_frame.enable(enable)

    def _set_data_directory(self) -> None:
        directory = filedialog.askdirectory(
            initialdir=self.data_directory.get(),
            parent=self.root,
        )
        if directory:
            self.data_directory.set(directory)

    def _save_config(self, *args) -> None:
        """Save defaults to config."""
        result = self.write_config()
        if result:
            messagebox.showinfo(title=APP_TITLE,
                                message=f'{text.CONFIG} saved',
                                parent=self.root)
        else:
            message = f'Defaults not saved{LF}{result}'
            messagebox.showerror(title=APP_TITLE, message=message,
                                 parent=self.root)
        self._dismiss()

    def write_config(self):
        # Files
        config.update('data_directory',  self.data_directory.get())

        ignore_text = self.ignore_text.get('0.0', tk.END)
        ignore_text = ignore_text.strip('\n')
        config.update('ignore', ignore_text.split('\n'))

        result = save_config(config)
        return result

    def _dismiss(self) -> None:
        self.root.destroy()
