import tkinter as tk
from tkinter import messagebox, filedialog
import os, random

EXAM_STRUCTURE = {
    "B1": {1: 7, 2: 6, 3: 6, 4: 6},
    "B2": {1: 7, 2: 7, 3: 7, 4: 7},
    "C1": {1: 8, 2: 8, 3: 8, 4: 8},
    "C2": {1: 9, 2: 9, 3: 9, 4: 9}
}

class ListeningWindow:
    def __init__(self, master, db, nivel):
        self.root = master
        self.db = db
        self.nivel = nivel
        self.root.title(f"Listening - Nivel {self.nivel}")
        self.root.geometry("900x600")
        self.mostrar_menu()

    # -------------------- UTIL --------------------
    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _pick_pdf(self, path_var):
        p = filedialog.askopenfilename(filetypes=[("PDF files","*.pdf")])
        if p: path_var.set(p)

    def copiar_url(self, url):
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        messagebox.showinfo("Copiado", "URL copiada al portapapeles.")

    def abrir_pdf(self, path):
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("Error", "PDF no encontrado.")

    # -------------------- MENU --------------------
    def mostrar_menu(self):
        self.limpiar_pantalla()
        tk.Label(self.root, text=f"🎧 Listening - Nivel {self.nivel}", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="➕ Añadir Audio/PDF", command=self.formulario_listening).pack(pady=5)
        tk.Button(self.root, text="📂 Ver/Modificar Audios", command=self.listar_listening).pack(pady=5)
        tk.Button(self.root, text="🎯 Practicar Listening", command=self.practicar_listening).pack(pady=5)
        tk.Button(self.root, text="⬅ Cerrar", command=self.root.destroy).pack(pady=20)

    # -------------------- AÑADIR AUDIO --------------------
    def formulario_listening(self):
        top = tk.Toplevel(self.root)
        top.title("Añadir Audio/PDF")
        top.geometry("600x600")

        def row(lbl):
            f = tk.Frame(top); f.pack(fill="x", pady=4)
            tk.Label(f, text=lbl, width=18, anchor="w").pack(side="left")
            return f

        f1 = row("Canal de YouTube:")
        canal_entry = tk.Entry(f1); canal_entry.pack(side="left", fill="x", expand=True)
        f2 = row("Título del Audio:")
        titulo_entry = tk.Entry(f2); titulo_entry.pack(side="left", fill="x", expand=True)
        f3 = row("URL de YouTube:")
        url_entry = tk.Entry(f3); url_entry.pack(side="left", fill="x", expand=True)
        f4 = row("Ruta del PDF:")
        path_var = tk.StringVar()
        tk.Entry(f4, textvariable=path_var).pack(side="left", fill="x", expand=True)
        tk.Button(f4, text="📄 Seleccionar PDF", command=lambda: self._pick_pdf(path_var)).pack(side="left", padx=6)

        def save():
            canal = canal_entry.get().strip()
            titulo = titulo_entry.get().strip()
            url = url_entry.get().strip()
            pdf = path_var.get().strip()
            if not canal or not titulo or not url:
                messagebox.showerror("Error", "⚠ Rellena canal, título y URL.")
                return

            audio_id = self.db.insertar_listening(self.nivel, canal, titulo, url, fallos=0, pdf=pdf)
            messagebox.showinfo("OK", "✅ Audio añadido. Ahora añade las preguntas por partes.")
            top.destroy()
            self.gestor_preguntas_todas_partes(audio_id, titulo)

        tk.Button(top, text="💾 Guardar y Añadir Preguntas", command=save).pack(pady=12)

    # -------------------- GESTOR DE PREGUNTAS --------------------
    def gestor_preguntas_todas_partes(self, listening_id, titulo_audio):
        win = tk.Toplevel(self.root)
        win.title(f"Preguntas - {titulo_audio}")
        win.geometry("900x600")

        partes = EXAM_STRUCTURE.get(self.nivel, {1:6,2:6,3:6,4:6})
        container = tk.Frame(win); container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas)
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        entradas_por_parte = {}

        for parte, num_preg in partes.items():
            tk.Label(form, text=f"Parte {parte} (preguntas: {num_preg})", font=("Arial", 12, "bold")).pack(pady=5)
            entradas = []
            for n in range(1, num_preg+1):
                fila = tk.Frame(form); fila.pack(fill="x", pady=2, padx=8)
                tk.Label(fila, text=f"{n:02d}.", width=4).pack(side="left")
                tk.Label(fila, text=f"Pregunta {n}", width=50, anchor="w").pack(side="left", padx=4)
                respuesta_entry = tk.Entry(fila, width=40)
                respuesta_entry.pack(side="left", padx=4)
                entradas.append((n, respuesta_entry))
            entradas_por_parte[parte] = entradas

        def guardar_todas():
            self.db.eliminar_preguntas_de_listening(listening_id)
            total = 0
            for parte, filas in entradas_por_parte.items():
                for num, respuesta_entry in filas:
                    respuesta = respuesta_entry.get().strip()
                    if respuesta:
                        self.db.insertar_pregunta_listening(listening_id, parte, num, None, respuesta)
                        total += 1
            messagebox.showinfo("Guardado", f"✅ Guardadas {total} preguntas.")
            win.destroy()

        tk.Button(win, text="💾 Guardar todas las preguntas", command=guardar_todas).pack(pady=10)

    # -------------------- LISTAR AUDIOS --------------------
    def listar_listening(self):
        self.limpiar_pantalla()
        tk.Label(self.root, text=f"Listening Audios - Nivel {self.nivel}", font=("Arial", 16)).pack(pady=10)
        audios = self.db.obtener_listening(nivel=self.nivel)
        if not audios:
            tk.Label(self.root, text="No hay audios guardados.", font=("Arial", 12)).pack(pady=10)
        else:
            frame = tk.Frame(self.root); frame.pack(pady=10, fill="both", expand=True)
            for id_audio, nivel, canal, titulo, url, fallos, pdf in audios:
                fila = tk.Frame(frame); fila.pack(fill="x", pady=2)
                tk.Label(fila, text=f"{titulo}", width=20, anchor="w").pack(side="left")
                tk.Label(fila, text=f"{canal}", width=15, anchor="w").pack(side="left")
                url_entry = tk.Entry(fila, width=30); url_entry.insert(0, url); url_entry.config(state="readonly"); url_entry.pack(side="left", padx=5)
                tk.Button(fila, text="Copiar URL", command=lambda u=url: self.copiar_url(u)).pack(side="left", padx=5)
                tk.Label(fila, text=f"Fallos: {fallos}", width=10, anchor="w").pack(side="left")
                if pdf: tk.Button(fila, text="Ver PDF", command=lambda p=pdf: self.abrir_pdf(p)).pack(side="left", padx=5)
                tk.Button(fila, text="Eliminar", command=lambda aid=id_audio: self.eliminar_audio(aid)).pack(side="right")
        tk.Button(self.root, text="⬅ Volver", command=self.mostrar_menu).pack(pady=15)

    def eliminar_audio(self, id_audio):
        self.db.eliminar_listening(id_audio)
        messagebox.showinfo("Eliminado", "Audio eliminado correctamente.")
        self.listar_listening()

    # -------------------- PRACTICAR LISTENING --------------------
    def practicar_listening(self):
        self.limpiar_pantalla()
        tk.Label(self.root, text=f"Practicar Listening - Nivel {self.nivel}", font=("Arial", 16)).pack(pady=10)

        audios = self.db.obtener_listening(nivel=self.nivel)
        if not audios:
            tk.Label(self.root, text="No hay audios para practicar.", font=("Arial", 12)).pack(pady=10)
            tk.Button(self.root, text="⬅ Volver", command=self.mostrar_menu).pack(pady=5)
            return

        for id_audio, nivel, canal, titulo, url, fallos, pdf in audios:
            texto_boton = f"{titulo} ({canal}) - Últimos fallos: {fallos}"  # <- agregamos fallos aquí
            tk.Button(self.root, text=texto_boton, command=lambda aid=id_audio: self._ejercicio_listening(aid)).pack(pady=2)

        tk.Button(self.root, text="⬅ Volver", command=self.mostrar_menu).pack(pady=15)


    def _ejercicio_listening(self, listening_id):
        self.limpiar_pantalla()
        partes = EXAM_STRUCTURE.get(self.nivel)
        preguntas_todas = []
        for parte in partes:
            preguntas_todas.extend(self.db.obtener_preguntas_listening(listening_id, parte))
        
        if not preguntas_todas:
            tk.Label(self.root, text="No hay preguntas para este audio. Añádelas primero.", font=("Arial", 12)).pack(pady=10)
            tk.Button(self.root, text="⬅ Volver", command=self.practicar_listening).pack(pady=10)
            return

        respuestas_vars = []
        for _id, parte, num, pregunta, correcta in preguntas_todas:
            row = tk.Frame(self.root); row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=f"{parte}.{num}", width=6, anchor="e").pack(side="left")
            tk.Label(row, text=f"Pregunta {num}", width=60, anchor="w").pack(side="left", padx=6)
            var = tk.StringVar()
            tk.Entry(row, textvariable=var, width=30).pack(side="left", padx=4)
            respuestas_vars.append((parte, num, correcta, var))

        def corregir():
            fallos = 0
            errores_detalle = []
            for parte, num, correcta, var in respuestas_vars:
                if var.get().strip().lower() != (correcta or "").strip().lower():
                    fallos += 1
                    errores_detalle.append(f"Parte {parte}, Pregunta {num}")
            self.db.actualizar_fallos(listening_id, fallos)
            mensaje = f"Fallos: {fallos} de {len(respuestas_vars)}"
            if errores_detalle:
                mensaje += "\nErrores en:\n" + "\n".join(errores_detalle)
            messagebox.showinfo("Resultado", mensaje)
            self.practicar_listening()

        tk.Button(self.root, text="💾 Corregir", command=corregir).pack(pady=12)
        tk.Button(self.root, text="⬅ Volver", command=self.practicar_listening).pack(pady=5)

