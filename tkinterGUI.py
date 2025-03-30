import tkinter
from tkinter import ttk

import sv_ttk

"Creating a Tkinter GUI to interact with other stuff, kinda like an external, peripheral menu panel"
root = tkinter.Tk()

button = ttk.Button(root, text="Click me!")
button.pack()

# This is where the magic happens
sv_ttk.set_theme("dark")

root.mainloop()