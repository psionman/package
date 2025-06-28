import tkinter as tk
from tkinter import ttk

TREE_COLUMNS = (
    ('code', 'Code', 20),
    ('name', 'Car', 50),
    ('price', 'Price', 100),
)

cars = {
    1: ('BMW', 30000),
    2: ('Mini', 20000),
}

class Main():
    def __init__(self) -> None:
        self.selected_car = None

        root = tk.Tk()
        root.geometry('400x400')

        self.tree = ttk.Treeview(
            root,
            selectmode='browse',
            height=15,
            show='headings',
            )
        self.tree.bind('<<TreeviewSelect>>', self._tree_clicked)

        col_list = tuple(col[0] for col in TREE_COLUMNS)
        self.tree['columns'] = col_list
        for col in TREE_COLUMNS:
            (col_key, col_text, col_width) = (col[0], col[1], col[2])
            self.tree.heading(col_key, text=col_text)
            self.tree.column(col_key, width=col_width, anchor=tk.W)
        self.tree.grid(row=0, column=0)
        self._populate_tree()

        button = tk.Button(text='Uplift', command=self._button_clicked)
        button.grid(row=1, column=1)

        root.mainloop()

    def _tree_clicked(self, *args) -> None:
        selected_item = self.tree.selection()
        if not selected_item:
            return
        values = self.tree.item(selected_item)['values']
        self.selected_car = values[0]

    def _button_clicked(self, *args) -> None:
        print(self.selected_car)
        print(self.tree.get_children())
        self.tree.delete(*self.tree.get_children())
        for key, car in cars.items():
            cars[key] = [car[0], int(car[1]*1.1)]
        self._populate_tree()

    def _populate_tree(self) -> None:
        for key, car in cars.items():
            values = [key] + [value for value in car]
            item = self.tree.insert('', 'end', values=values)
            if self.selected_car and key == self.selected_car:
                self.tree.selection_set(item)
if __name__ == '__main__':
    Main()
