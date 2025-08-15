import tkinter as tk
from tkinter import messagebox
import datetime, random

class VocabularioWindow:
    instancia_abierta = None  # Evita duplicados

    def __init__(self, master, db, nivel):
        if VocabularioWindow.instancia_abierta:
            VocabularioWindow.instancia_abierta.lift()
            return
        VocabularioWindow.instancia_abierta = self

        self.db = db
        self.nivel = nivel
        self.win = tk.Toplevel(master)
        self.win.title(f"Vocabulary - Level {nivel}")
        self.win.geometry("500x500")
        self.win.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        tk.Label(self.win, text=f"Vocabulary - Level {nivel}", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.win, text="Daily Task", command=self.tarea_diaria).pack(pady=3)
        tk.Button(self.win, text="Add Word", command=self.anadir_palabra_suelta).pack(pady=3)
        tk.Button(self.win, text="Daily Review", command=self.revision_diaria).pack(pady=3)
        tk.Button(self.win, text="General Review", command=self.revision_general).pack(pady=3)
        tk.Button(self.win, text="Random Question", command=self.pregunta_aleatoria).pack(pady=3)
        tk.Button(self.win, text="Word List", command=self.listar_palabras).pack(pady=3)

    def cerrar_ventana(self):
        VocabularioWindow.instancia_abierta = None
        self.win.destroy()

    def tarea_diaria(self):
        hoy = datetime.date.today().isoformat()
        palabras = self.db.obtener_palabras(nivel=self.nivel, fecha=hoy)
        conteo = {"palabra": 0, "phrasal": 0, "idioma": 0}
        for _, _, _, _, tipo in palabras:
            if tipo in conteo:
                conteo[tipo] += 1

        objetivos = {"palabra": 5, "phrasal": 3, "idioma": 1}

        for tipo, meta in objetivos.items():
            if conteo[tipo] < meta:
                faltan = meta - conteo[tipo]
                mensaje = f"Debes añadir {faltan} {tipo}(s) hoy."
                self.formulario_palabra(f"Daily Task - {tipo}", tipo, mensaje)
                return

        messagebox.showinfo("Daily Task", "✅ ¡Tarea diaria completada!")

    def formulario_palabra(self, titulo, tipo, mensaje):
        top = tk.Toplevel(self.win)
        top.title(titulo)

        tk.Label(top, text=mensaje, fg="blue").pack(pady=5)
        tk.Label(top, text="Palabra en inglés").pack()
        palabra_entry = tk.Entry(top)
        palabra_entry.pack()

        tk.Label(top, text="Traducción en español").pack()
        traduccion_entry = tk.Entry(top)
        traduccion_entry.pack()

        tk.Label(top, text="Ejemplo de uso").pack()
        ejemplo_entry = tk.Entry(top)
        ejemplo_entry.pack()

        def guardar():
            palabra = palabra_entry.get().strip()
            traduccion = traduccion_entry.get().strip()
            ejemplo = ejemplo_entry.get().strip()
            if not palabra or not traduccion:
                messagebox.showerror("Error", "Debes rellenar palabra y traducción")
                return
            if self.db.insertar_palabra(palabra, traduccion, ejemplo, tipo, self.nivel):
                messagebox.showinfo("OK", "✅ Palabra añadida correctamente")
                top.destroy()
                self.tarea_diaria()
            else:
                messagebox.showerror("Error", "❌ La palabra ya existe")

        tk.Button(top, text="Guardar", command=guardar).pack(pady=5)

    def anadir_palabra_suelta(self):
        top = tk.Toplevel(self.win)
        top.title("Add Word")

        tk.Label(top, text="Add a new word", fg="blue").pack(pady=5)

        tk.Label(top, text="Type").pack()
        tipo_var = tk.StringVar()
        tipo_menu = tk.OptionMenu(top, tipo_var, "palabra", "phrasal", "idioma")
        tipo_menu.pack()

        tk.Label(top, text="Word in English").pack()
        palabra_entry = tk.Entry(top)
        palabra_entry.pack()

        tk.Label(top, text="Translation in Spanish").pack()
        traduccion_entry = tk.Entry(top)
        traduccion_entry.pack()

        tk.Label(top, text="Example sentence").pack()
        ejemplo_entry = tk.Entry(top)
        ejemplo_entry.pack()

        def guardar():
            palabra = palabra_entry.get().strip()
            traduccion = traduccion_entry.get().strip()
            ejemplo = ejemplo_entry.get().strip()
            tipo = tipo_var.get()
            if not palabra or not traduccion or not tipo:
                messagebox.showerror("Error", "Debes rellenar todos los campos y elegir un tipo.")
                return
            if self.db.insertar_palabra(palabra, traduccion, ejemplo, tipo, self.nivel):
                messagebox.showinfo("OK", "✅ Palabra añadida correctamente")
                top.destroy()
            else:
                messagebox.showerror("Error", "❌ La palabra ya existe")

        tk.Button(top, text="Guardar", command=guardar).pack(pady=5)


    def revision_diaria(self):
        ayer = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        lista = self.db.obtener_palabras(nivel=self.nivel, fecha=ayer)
        lista = [p for p in lista if self.db.obtener_estado_palabra(p[0]) != "aprendido"]
        self.revision_lista(lista, "Daily Review")

    def revision_general(self):
        lista = self.db.obtener_palabras(estado="pendiente", nivel=self.nivel) + \
                self.db.obtener_palabras(estado="repetir", nivel=self.nivel) * 3
        self.revision_lista(lista, "General Review")

    def revision_lista(self, lista, titulo):
        if not lista:
            messagebox.showinfo(titulo, "No words.")
            return
        palabra_id, palabra, traduccion, _, _ = random.choice(lista)
        top = tk.Toplevel(self.win)
        tk.Label(top, text=f"Translate: {palabra}").pack()
        entry = tk.Entry(top)
        entry.pack()

        def check():
            if entry.get().strip().lower() == traduccion.lower():
                self.db.actualizar_estado(palabra_id, "aprendido")
                messagebox.showinfo("OK", "✅ Correct!")
            else:
                self.db.actualizar_estado(palabra_id, "repetir")
                messagebox.showerror("Incorrect", f"Correct: {traduccion}")
            top.destroy()

        tk.Button(top, text="Check", command=check).pack()

    def pregunta_aleatoria(self):
        lista = self.db.obtener_todas_palabras(self.nivel)
        self.revision_lista(lista, "Random Question")

    def listar_palabras(self):
        lista = self.db.obtener_todas_palabras_con_estado(self.nivel)
        if not lista:
            messagebox.showinfo("Word List", "No words.")
            return

        top = tk.Toplevel(self.win)
        top.title("Word List")
        for palabra_id, palabra, traduccion, ejemplo, tipo, estado in lista:
            frame = tk.Frame(top)
            frame.pack(fill="x", pady=2)

            tk.Label(frame, text=f"{palabra} - {traduccion}", width=30, anchor="w").pack(side="left")
            tk.Label(frame, text=f"({tipo}) [{estado}]", width=20, anchor="w").pack(side="left")
            tk.Button(frame, text="Delete", command=lambda pid=palabra_id: self.eliminar_palabra(pid, top)).pack(side="right")

    def eliminar_palabra(self, palabra_id, win_list):
        self.db.eliminar_palabra(palabra_id)
        messagebox.showinfo("Deleted", "Word deleted successfully.")
        win_list.destroy()
        self.listar_palabras()
