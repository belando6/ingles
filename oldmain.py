import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import random
from tkinter import filedialog
import webbrowser
import os


# ===================== BASE DE DATOS =====================
def crear_tabla():
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS vocabulario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palabra TEXT,
            traduccion TEXT,
            ejemplo TEXT,
            tipo TEXT,
            nivel TEXT,
            fecha TEXT,
            estado TEXT
        )
    """)
    conn.commit()
    conn.close()

def palabra_existe(palabra, nivel):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    c.execute("SELECT id FROM vocabulario WHERE palabra = ? AND nivel = ?", (palabra, nivel))
    existe = c.fetchone() is not None
    conn.close()
    return existe

def insertar_palabra(palabra, traduccion, ejemplo, tipo, nivel, estado="pendiente"):
    if palabra_existe(palabra, nivel):
        return False
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    fecha = datetime.date.today().isoformat()
    c.execute("""
        INSERT INTO vocabulario (palabra, traduccion, ejemplo, tipo, nivel, fecha, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (palabra, traduccion, ejemplo, tipo, nivel, fecha, estado))
    conn.commit()
    conn.close()
    return True

def obtener_palabras(estado=None, nivel=None, fecha=None):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    query = "SELECT id, palabra, traduccion, ejemplo, tipo FROM vocabulario WHERE 1=1"
    params = []
    if estado:
        query += " AND estado = ?"
        params.append(estado)
    if nivel:
        query += " AND nivel = ?"
        params.append(nivel)
    if fecha:
        query += " AND fecha = ?"
        params.append(fecha)
    c.execute(query, tuple(params))
    datos = c.fetchall()
    conn.close()
    return datos

def obtener_todas_palabras(nivel):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    c.execute("SELECT id, palabra, traduccion, ejemplo, tipo FROM vocabulario WHERE nivel = ?", (nivel,))
    datos = c.fetchall()
    conn.close()
    return datos

def actualizar_estado(id_palabra, nuevo_estado):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    c.execute("UPDATE vocabulario SET estado = ? WHERE id = ?", (nuevo_estado, id_palabra))
    conn.commit()
    conn.close()

# ===================== BASE DE DATOS - LISTENING =====================
def crear_tabla_listening():
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    
    # Crear tabla si no existe
    c.execute("""
        CREATE TABLE IF NOT EXISTS listening (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel TEXT,
            canal TEXT,
            titulo TEXT,
            url TEXT,
            fallos INTEGER DEFAULT 0
        )
    """)
    
    # Añadir columna 'pdf' si no existe
    c.execute("PRAGMA table_info(listening)")
    columnas = [info[1] for info in c.fetchall()]
    if "pdf" not in columnas:
        c.execute("ALTER TABLE listening ADD COLUMN pdf TEXT")
    
    conn.commit()
    conn.close()

def insertar_listening(nivel, canal, titulo, url, fallos=0, pdf=None):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO listening (nivel, canal, titulo, url, fallos, pdf)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nivel, canal, titulo, url, fallos, pdf))
    conn.commit()
    conn.close()


def obtener_listening(nivel=None):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    if nivel:
        c.execute("SELECT id, nivel, canal, titulo, url, fallos, pdf FROM listening WHERE nivel = ?", (nivel,))
    else:
        c.execute("SELECT id, nivel, canal, titulo, url, fallos, pdf FROM listening")
    audios = c.fetchall()
    conn.close()
    return audios

def eliminar_listening(id_audio):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    c.execute("DELETE FROM listening WHERE id = ?", (id_audio,))
    conn.commit()
    conn.close()

def aumentar_fallos(id_audio):
    conn = sqlite3.connect("vocabulario.db")
    c = conn.cursor()
    c.execute("UPDATE listening SET fallos = fallos + 1 WHERE id = ?", (id_audio,))
    conn.commit()
    conn.close()

# ===================== APLICACIÓN =====================
class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("English Learning App")
        self.root.geometry("700x550")
        
        self.nivel = tk.StringVar()
        self.apartados = ["Vocabulary", "Listening", "Reading", "Speaking", "Writing"]
        
        crear_tabla()
        crear_tabla_listening() 
        self.pantalla_nivel()
    
    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def pantalla_nivel(self):
        self.limpiar_ventana()
        
        label = tk.Label(self.root, text="Select your level:", font=("Arial", 14))
        label.pack(pady=20)
        
        niveles = ["B1", "B2", "C1", "C2"]
        combo = ttk.Combobox(self.root, values=niveles, textvariable=self.nivel, state="readonly", font=("Arial", 12))
        combo.pack(pady=10)
        
        boton = tk.Button(self.root, text="Continue", command=self.menu_principal, font=("Arial", 12))
        boton.pack(pady=20)
    
    def menu_principal(self):
        if not self.nivel.get():
            return
        
        self.limpiar_ventana()
        
        label = tk.Label(self.root, text=f"Main Menu - Level: {self.nivel.get()}", font=("Arial", 14))
        label.pack(pady=20)
        
        for i, nombre in enumerate(self.apartados, start=1):
            boton = tk.Button(self.root, text=nombre, command=lambda num=i: self.abrir_apartado(num),
                              font=("Arial", 12), width=20)
            boton.pack(pady=5)
        
        boton_volver = tk.Button(self.root, text="Change Level", command=self.pantalla_nivel, font=("Arial", 12))
        boton_volver.pack(pady=20)
    
    def abrir_apartado(self, num):
        if num == 1:
            self.vocabulario_menu()
        elif num == 2:
            self.listening_menu()
        else:
            self.limpiar_ventana()
            nombre_apartado = self.apartados[num - 1]
            label = tk.Label(self.root, text=f"{nombre_apartado} - Level: {self.nivel.get()}", font=("Arial", 14))
            label.pack(pady=20)
            tk.Button(self.root, text="Back to menu", command=self.menu_principal, font=("Arial", 12)).pack(pady=20)
    
    # ===================== VOCABULARY =====================
    def vocabulario_menu(self):
        self.limpiar_ventana()
        
        label = tk.Label(self.root, text=f"Vocabulary - Level {self.nivel.get()}", font=("Arial", 16))
        label.pack(pady=10)
        
        tk.Button(self.root, text="Daily Task", command=self.tarea_diaria, font=("Arial", 12), width=25).pack(pady=3)
        tk.Button(self.root, text="Daily Review", command=self.revision_diaria, font=("Arial", 12), width=25).pack(pady=3)
        tk.Button(self.root, text="General Review", command=self.revision_general, font=("Arial", 12), width=25).pack(pady=3)
        tk.Button(self.root, text="Random Question", command=self.pregunta_aleatoria, font=("Arial", 12), width=25).pack(pady=3)
        tk.Button(self.root, text="Back to menu", command=self.menu_principal, font=("Arial", 12)).pack(pady=15)
        tk.Button(self.root, text="Word List", command=self.listar_palabras, font=("Arial", 12), width=25).pack(pady=3)

    def tarea_diaria(self):
        self.verificar_tarea_completa()
    
    def verificar_tarea_completa(self):
        hoy = datetime.date.today().isoformat()
        nivel = self.nivel.get()
        palabras = obtener_palabras(nivel=nivel, fecha=hoy)
        conteo = {"palabra":0, "phrasal":0, "idioma":0}
        for _, _, _, _, tipo in palabras:
            if tipo in conteo:
                conteo[tipo] += 1
        
        if conteo["palabra"] < 5:
            self.formulario_palabra("Daily Task - Word", "palabra")
        elif conteo["phrasal"] < 3:
            self.formulario_palabra("Daily Task - Phrasal Verb", "phrasal")
        elif conteo["idioma"] < 1:
            self.formulario_palabra("Daily Task - Idiom", "idioma")
        else:
            messagebox.showinfo("Daily Task", "✅ Daily task completed!")
            self.vocabulario_menu()
    
    def formulario_palabra(self, titulo, tipo):
        self.limpiar_ventana()
        tk.Label(self.root, text=titulo, font=("Arial", 14)).pack(pady=10)
        
        palabra_entry = tk.Entry(self.root); palabra_entry.pack()
        traduccion_entry = tk.Entry(self.root); traduccion_entry.pack()
        ejemplo_entry = tk.Entry(self.root); ejemplo_entry.pack()
        
        def guardar():
            if insertar_palabra(palabra_entry.get().strip(), traduccion_entry.get().strip(),
                                 ejemplo_entry.get().strip(), tipo, self.nivel.get()):
                self.verificar_tarea_completa()
            else:
                messagebox.showwarning("Error", "This word already exists for this level.")
        
        tk.Button(self.root, text="Save", command=guardar).pack(pady=10)
        tk.Button(self.root, text="Cancel", command=self.vocabulario_menu).pack()
    
    def revision_diaria(self):
        ayer = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        palabras = obtener_palabras(nivel=self.nivel.get(), fecha=ayer)
        self.revision_lista(palabras, "Daily Review")
    
    def revision_general(self):
        palabras_pendientes = obtener_palabras(estado="pendiente", nivel=self.nivel.get())
        palabras_repetir = obtener_palabras(estado="repetir", nivel=self.nivel.get())
        lista = palabras_pendientes + palabras_repetir * 3  # Más frecuencia para repetir
        self.revision_lista(lista, "General Review")
    
    def revision_lista(self, lista, titulo):
        if not lista:
            messagebox.showinfo(titulo, "No words to review.")
            self.vocabulario_menu()
            return
        palabra_data = random.choice(lista)
        palabra_id, palabra, traduccion, ejemplo, tipo = palabra_data
        self.limpiar_ventana()
        tk.Label(self.root, text=f"Translate: {palabra}", font=("Arial", 14)).pack(pady=10)
        respuesta_entry = tk.Entry(self.root); respuesta_entry.pack()
        
        def comprobar():
            if respuesta_entry.get().strip().lower() == traduccion.lower():
                messagebox.showinfo("Correct", "✅ Well done!")
                actualizar_estado(palabra_id, "aprendido")
            else:
                messagebox.showerror("Incorrect", f"The correct translation is: {traduccion}")
                actualizar_estado(palabra_id, "repetir")
            self.revision_lista(lista, titulo)
        
        tk.Button(self.root, text="Check", command=comprobar).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.vocabulario_menu).pack()
    
    def pregunta_aleatoria(self):
        palabras = obtener_todas_palabras(self.nivel.get())
        self.revision_lista(palabras, "Random Question")

    def listar_palabras(self):
        self.limpiar_ventana()

        tk.Label(self.root, text=f"Word List - Level {self.nivel.get()}", font=("Arial", 16)).pack(pady=10)

        palabras = obtener_todas_palabras(self.nivel.get())
        if not palabras:
            tk.Label(self.root, text="No words in this level.", font=("Arial", 12)).pack(pady=10)
        else:
            frame = tk.Frame(self.root)
            frame.pack(pady=10)

            for palabra_id, palabra, traduccion, ejemplo, tipo in palabras:
                fila = tk.Frame(frame)
                fila.pack(fill="x", pady=2)

                tk.Label(fila, text=f"{palabra} - {traduccion}", width=30, anchor="w").pack(side="left")
                tk.Label(fila, text=f"({tipo})", width=12, anchor="w").pack(side="left")

                btn_eliminar = tk.Button(fila, text="Delete", command=lambda pid=palabra_id: self.eliminar_palabra(pid))
                btn_eliminar.pack(side="right")

        tk.Button(self.root, text="Back", command=self.vocabulario_menu).pack(pady=20)

    def eliminar_palabra(self, palabra_id):
        conn = sqlite3.connect("vocabulario.db")
        c = conn.cursor()
        c.execute("DELETE FROM vocabulario WHERE id = ?", (palabra_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Word deleted successfully.")
        self.listar_palabras()

    # ===================== LISTENING =====================
    def listening_menu(self):
        self.limpiar_ventana()
        
        tk.Label(self.root, text=f"Listening - Level {self.nivel.get()}", font=("Arial", 16)).pack(pady=10)
        
        tk.Button(self.root, text="Add Audio", command=self.formulario_listening, font=("Arial", 12), width=25).pack(pady=5)
        tk.Button(self.root, text="Random Audio with Mistake", command=self.random_audio_fallo, width=25).pack(pady=3)
        tk.Button(self.root, text="Select Audio to Modify", command=self.seleccionar_audio_modificar, width=25).pack(pady=3)

        tk.Button(self.root, text="View/Manage Audios", command=self.listar_listening, font=("Arial", 12), width=25).pack(pady=5)
        tk.Button(self.root, text="Back to menu", command=self.menu_principal, font=("Arial", 12)).pack(pady=20)

    def formulario_listening(self):
        self.limpiar_ventana()
        tk.Label(self.root, text="Add Listening Audio / PDF", font=("Arial", 14)).pack(pady=10)
        
        canal_entry = tk.Entry(self.root); canal_entry.pack(pady=2)
        canal_entry.insert(0, "Channel")
        
        titulo_entry = tk.Entry(self.root); titulo_entry.pack(pady=2)
        titulo_entry.insert(0, "Title")
        
        url_entry = tk.Entry(self.root); url_entry.pack(pady=2)
        url_entry.insert(0, "Audio URL (optional)")
        
        pdf_path_var = tk.StringVar()
        pdf_entry = tk.Entry(self.root, textvariable=pdf_path_var, width=50)
        pdf_entry.pack(pady=2)
        pdf_entry.insert(0, "PDF Path (optional)")
        
        def seleccionar_pdf():
            path = filedialog.askopenfilename(
                title="Select PDF",
                filetypes=[("PDF files", "*.pdf")]
            )
            if path:
                pdf_path_var.set(path)
        
        tk.Button(self.root, text="Select PDF", command=seleccionar_pdf).pack(pady=5)
        
        fallos_entry = tk.Entry(self.root); fallos_entry.pack(pady=2)
        fallos_entry.insert(0, "0")
        
        def guardar():
            canal = canal_entry.get().strip()
            titulo = titulo_entry.get().strip()
            url = url_entry.get().strip()
            pdf = pdf_path_var.get().strip()
            fallos = int(fallos_entry.get().strip() or 0)
            
            if not canal or not titulo:
                messagebox.showerror("Error", "Channel and Title are required")
                return
            if not url and not pdf:
                messagebox.showerror("Error", "Please provide either an Audio URL or a PDF")
                return
            
            # Guardar la info en la tabla listening
            insertar_listening(
                self.nivel.get(),
                canal,
                titulo,
                url,   # aquí puedes guardar URL o dejarlo vacío si se usó PDF
                fallos,
                pdf    # Si tu tabla listening tiene columna pdf, o añadir una columna nueva
            )
            messagebox.showinfo("Saved", "Audio/PDF saved successfully!")
            self.listening_menu()
        
        tk.Button(self.root, text="Save", command=guardar).pack(pady=10)
        tk.Button(self.root, text="Cancel", command=self.listening_menu).pack()


    def listar_listening(self):
        self.limpiar_ventana()
        tk.Label(self.root, text=f"Listening Audios - Level {self.nivel.get()}", font=("Arial", 16)).pack(pady=10)
        
        audios = obtener_listening(nivel=self.nivel.get())  # Ahora debe devolver id, nivel, canal, titulo, url, fallos, pdf
        if not audios:
            tk.Label(self.root, text="No listening audios found.", font=("Arial", 12)).pack(pady=10)
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
                url_entry.config(state="readonly")  # Solo lectura
                url_entry.pack(side="left", padx=5)

                # Botón para copiar la URL al portapapeles
                def copiar_url(u=url):
                    fila.clipboard_clear()
                    fila.clipboard_append(u)
                    messagebox.showinfo("Copied", "URL copied to clipboard!")

                tk.Button(fila, text="Copy URL", command=copiar_url).pack(side="left", padx=5)
                
                tk.Label(fila, text=f"Fallos: {fallos}", width=10, anchor="w").pack(side="left")
                
                # Botón para ver PDF si existe
                if pdf:  # Solo muestra el botón si hay PDF
                    def abrir_pdf(path=pdf):
                        if os.path.exists(path):
                            webbrowser.open_new(path)
                        else:
                            messagebox.showerror("Error", "PDF file not found!")
                    
                    tk.Button(fila, text="View PDF", command=abrir_pdf).pack(side="left", padx=5)
                
                tk.Button(fila, text="Delete", command=lambda aid=id_audio: self.eliminar_audio(aid)).pack(side="right")



        tk.Button(self.root, text="Back", command=self.listening_menu).pack(pady=15)
    def eliminar_audio(self, id_audio):
        eliminar_listening(id_audio)
        messagebox.showinfo("Deleted", "Audio deleted successfully.")
        self.listar_listening()
    def random_audio_fallo(self):
        conn = sqlite3.connect("vocabulario.db")
        c = conn.cursor()
        c.execute("SELECT id, titulo, fallos FROM listening WHERE nivel = ? AND fallos > 0", (self.nivel.get(),))
        audios = c.fetchall()
        conn.close()

        if not audios:
            messagebox.showinfo("Info", "No audios with mistakes.")
            return

        audio = random.choice(audios)
        self.modificar_fallos(audio[0], audio[1], audio[2])

    def seleccionar_audio_modificar(self):
        conn = sqlite3.connect("vocabulario.db")
        c = conn.cursor()
        c.execute("SELECT id, titulo, fallos FROM listening WHERE nivel = ?", (self.nivel.get(),))
        audios = c.fetchall()
        conn.close()

        if not audios:
            messagebox.showinfo("Info", "No audios saved.")
            return

        self.limpiar_ventana()
        tk.Label(self.root, text="Select an audio to modify fallos", font=("Arial", 14)).pack(pady=10)
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        for id_audio, titulo, fallos in audios:
            fila = tk.Frame(frame)
            fila.pack(fill="x", pady=2)
            tk.Label(fila, text=f"{titulo} - Fallos: {fallos}", width=50, anchor="w").pack(side="left")
            tk.Button(fila, text="Modify", command=lambda aid=id_audio, t=titulo, f=fallos: self.modificar_fallos(aid, t, f)).pack(side="left")

        tk.Button(self.root, text="Back", command=self.listar_listening).pack(pady=20)


    def modificar_fallos(self, id_audio, titulo, fallos_actual):
        self.limpiar_ventana()
        tk.Label(self.root, text=f"Modify Fallos - {titulo}", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(self.root)
        entry.insert(0, str(fallos_actual))
        entry.pack(pady=5)

        def guardar():
            try:
                nuevos_fallos = int(entry.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid integer")
                return

            conn = sqlite3.connect("vocabulario.db")
            c = conn.cursor()
            c.execute("UPDATE listening SET fallos = ? WHERE id = ?", (nuevos_fallos, id_audio))
            conn.commit()
            conn.close()
            messagebox.showinfo("Updated", "Fallos updated successfully")
            self.listar_listening()

        tk.Button(self.root, text="Save", command=guardar).pack(pady=5)
        tk.Button(self.root, text="Cancel", command=self.listar_listening).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
