import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3, os, random, webbrowser



# ---------- CLASE DE LISTENING ----------
class ListeningWindow:
    def __init__(self, master, db, nivel):
        self.root = master
        self.db = db
        self.nivel = nivel

        self.root.title(f"Listening - Nivel {self.nivel}")
        self.root.geometry("800x600")

        self.mostrar_menu()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_menu(self):
        self.limpiar_pantalla()

        tk.Label(self.root, text=f"🎧 Listening - Nivel {self.nivel}", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="➕ Añadir Audio/PDF", command=self.formulario_listening).pack(pady=5)
        tk.Button(self.root, text="📂 Ver/Modificar Audios", command=self.listar_listening).pack(pady=5)
        tk.Button(self.root, text="🎯 Audio Aleatorio con Fallos", command=self.random_audio_fallo).pack(pady=5)
        tk.Button(self.root, text="✏ Modificar Fallos", command=self.seleccionar_audio_modificar).pack(pady=5)
        tk.Button(self.root, text="⬅ Cerrar", command=self.root.destroy).pack(pady=20)

    

    # ---------- FORMULARIO PARA AÑADIR ----------
    def formulario_listening(self):
        top = tk.Toplevel(self.root)
        top.title("Añadir Audio/PDF")
        top.geometry("400x400")

        tk.Label(top, text="Canal de YouTube:").pack()
        canal_entry = tk.Entry(top)
        canal_entry.pack()

        tk.Label(top, text="Título del Audio:").pack()
        titulo_entry = tk.Entry(top)
        titulo_entry.pack()

        tk.Label(top, text="URL de YouTube:").pack()
        url_entry = tk.Entry(top)
        url_entry.pack()

        tk.Label(top, text="Ruta del PDF:").pack()
        path_var = tk.StringVar()
        tk.Entry(top, textvariable=path_var).pack()

        def select_pdf():
            p = filedialog.askopenfilename(filetypes=[("PDF files","*.pdf")])
            if p:
                path_var.set(p)

        tk.Button(top, text="📄 Seleccionar PDF", command=select_pdf).pack(pady=5)

        tk.Label(top, text="Número de Fallos:").pack()
        fallos_entry = tk.Entry(top)
        fallos_entry.pack()

        def save():
            canal = canal_entry.get().strip()
            titulo = titulo_entry.get().strip()
            url = url_entry.get().strip()
            pdf = path_var.get().strip()
            try:
                fallos = int(fallos_entry.get() or 0)
            except ValueError:
                fallos = 0

            if not canal or not titulo or not url:
                messagebox.showerror("Error", "⚠ Rellena todos los campos obligatorios.")
                return

            conn = sqlite3.connect("vocabulario.db")
            c = conn.cursor()
            c.execute("INSERT INTO listening (nivel, canal, titulo, url, fallos, pdf) VALUES (?, ?, ?, ?, ?, ?)",
                      (self.nivel, canal, titulo, url, fallos, pdf))
            conn.commit()
            conn.close()

            messagebox.showinfo("OK", "✅ Audio añadido correctamente.")
            top.destroy()

        tk.Button(top, text="💾 Guardar", command=save).pack(pady=5)


    # ---------- LISTAR AUDIOS ----------

    def listar_listening(self):
        self.limpiar_pantalla()

        tk.Label(self.root, text=f"Listening Audios - Nivel {self.nivel}", font=("Arial", 16)).pack(pady=10)

        audios = self.db.obtener_listening(nivel=self.nivel)
        if not audios:
            tk.Label(self.root, text="No hay audios guardados.", font=("Arial", 12)).pack(pady=10)
        else:
            frame = tk.Frame(self.root)
            frame.pack(pady=10, fill="both", expand=True)

            for id_audio, nivel, canal, titulo, url, fallos, pdf in audios:
                fila = tk.Frame(frame)
                fila.pack(fill="x", pady=2)

                tk.Label(fila, text=f"{titulo}", width=20, anchor="w").pack(side="left")
                tk.Label(fila, text=f"{canal}", width=15, anchor="w").pack(side="left")

                url_entry = tk.Entry(fila, width=30)
                url_entry.insert(0, url)
                url_entry.config(state="readonly")
                url_entry.pack(side="left", padx=5)

                tk.Button(fila, text="Copiar URL", command=lambda u=url: self.copiar_url(u)).pack(side="left", padx=5)
                tk.Label(fila, text=f"Fallos: {fallos}", width=10, anchor="w").pack(side="left")

                if pdf:
                    tk.Button(fila, text="Ver PDF", command=lambda p=pdf: self.abrir_pdf(p)).pack(side="left", padx=5)

                tk.Button(fila, text="Eliminar", command=lambda aid=id_audio: self.eliminar_audio(aid)).pack(side="right")

        tk.Button(self.root, text="⬅ Volver", command=self.mostrar_menu).pack(pady=15)



    def eliminar_audio(self, id_audio):
        self.db.eliminar_listening(id_audio)
        messagebox.showinfo("Eliminado", "Audio eliminado correctamente.")
        self.listar_listening()


    # ---------- AUDIO ALEATORIO CON FALLOS ----------
    def random_audio_fallo(self):
        conn = sqlite3.connect("vocabulario.db")
        c = conn.cursor()
        c.execute("SELECT id, titulo, fallos FROM listening WHERE nivel = ? AND fallos > 0", (self.nivel,))
        audios = c.fetchall()
        conn.close()

        if not audios:
            messagebox.showinfo("Info", "No hay audios con fallos.")
            return

        audio = random.choice(audios)
        self.modificar_fallos(audio[0], audio[1], audio[2])


    # ---------- SELECCIONAR AUDIO PARA MODIFICAR ----------
    def seleccionar_audio_modificar(self):
        conn = sqlite3.connect("vocabulario.db")
        c = conn.cursor()
        c.execute("SELECT id, titulo, fallos FROM listening WHERE nivel = ?", (self.nivel,))
        audios = c.fetchall()
        conn.close()

        if not audios:
            messagebox.showinfo("Info", "No hay audios guardados.")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Selecciona un audio para modificar fallos", font=("Arial", 14)).pack(pady=10)
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        for id_audio, titulo, fallos in audios:
            fila = tk.Frame(frame)
            fila.pack(fill="x", pady=2)
            tk.Label(fila, text=f"{titulo} - Fallos: {fallos}", width=50, anchor="w").pack(side="left")
            tk.Button(fila, text="Modificar", command=lambda aid=id_audio, t=titulo, f=fallos: self.modificar_fallos(aid, t, f)).pack(side="left")

        tk.Button(self.root, text="⬅ Volver", command=self.listar_listening).pack(pady=20)


    # ---------- MODIFICAR FALLOS ----------
    def modificar_fallos(self, id_audio, titulo, fallos_actual):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Modificar Fallos - {titulo}", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(self.root)
        entry.insert(0, str(fallos_actual))
        entry.pack(pady=5)

        def guardar():
            try:
                nuevos_fallos = int(entry.get())
            except ValueError:
                messagebox.showerror("Error", "Introduce un número válido.")
                return

            conn = sqlite3.connect("vocabulario.db")
            c = conn.cursor()
            c.execute("UPDATE listening SET fallos = ? WHERE id = ?", (nuevos_fallos, id_audio))
            conn.commit()
            conn.close()
            messagebox.showinfo("Actualizado", "Fallos actualizados correctamente.")
            self.listar_listening()

        tk.Button(self.root, text="💾 Guardar", command=guardar).pack(pady=5)
        tk.Button(self.root, text="⬅ Cancelar", command=self.listar_listening).pack(pady=5)