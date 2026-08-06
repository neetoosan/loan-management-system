import tkinter as tk
from tkinter import filedialog

try:
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title="Select a file", filetypes=[("All files","*.*")])
    root.destroy()
    if path:
        print("Selected:", path)
    else:
        print("No file selected (cancelled)")
except Exception as e:
    print("tkinter dialog failed:", repr(e))
    raise
