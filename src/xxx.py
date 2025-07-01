from PIL import Image, ImageTk
from pathlib import Path
import tkinter as tk
from tkinter import ttk


def main() -> None:
    root = tk.Tk()
    root.title('Hello world')
    root.geometry('400x400')

    icon = 'cancel'
    img = Image.open(f'{Path(__file__).parent}/icons/{icon}.png').resize((16, 16))
    photo = ImageTk.PhotoImage(img)

    btn = ttk.Button(root, image=photo, text="Edit", compound="left")
    btn.image = photo  # Prevent garbage collection
    btn.pack()

    root.mainloop()


if __name__ == '__main__':
    main()
