import tkinter as tk
from tkinter import ttk
from database import Database
from windows.vocabulario import VocabularioWindow
from windows.listening import ListeningWindow

class MainApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.nivel = tk.StringVar()
        self.pantalla_nivel()

    def pantalla_nivel(self):
        tk.Label(self.root, text="Select your level:").pack(pady=10)
        niveles = ["B1","B2","C1","C2"]
        ttk.Combobox(self.root, values=niveles, textvariable=self.nivel, state="readonly").pack(pady=5)
        tk.Button(self.root, text="Continue", command=self.menu_principal).pack(pady=10)

    def menu_principal(self):
        if not self.nivel.get():
            return
        tk.Button(self.root, text="Vocabulary", command=lambda: VocabularioWindow(self.root, self.db, self.nivel.get())).pack(pady=5)
        tk.Button(self.root,text="Listening",command=lambda: ListeningWindow(tk.Toplevel(self.root), self.db, self.nivel.get())).pack(pady=5)
        tk.Button(self.root, text="Reading", command=lambda: tk.messagebox.showinfo("Info","Reading section")).pack(pady=5)
        tk.Button(self.root, text="Speaking", command=lambda: tk.messagebox.showinfo("Info","Speaking section")).pack(pady=5)
        tk.Button(self.root, text="Writing", command=lambda: tk.messagebox.showinfo("Info","Writing section")).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("English Learning App")
    root.geometry("400x300")
    MainApp(root)
    root.mainloop()
