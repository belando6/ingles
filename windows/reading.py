import tkinter as tk
from tkinter import messagebox

class ReadingWindow:
    def __init__(self, master, db, nivel):
        self.master = master
        self.db = db
        self.nivel = nivel

        self.frame = tk.Frame(master)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text=f"📖 Reading - Level {nivel}", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.frame, text="Section under development...", fg="gray").pack(pady=20)
        tk.Button(self.frame, text="Back", command=self.back).pack(pady=5)

    def back(self):
        self.frame.destroy()
