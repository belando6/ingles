import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import random

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

# ===================== APLICACIÓN =====================
class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("English Learning App")
        self.root.geometry("700x550")
        
        self.nivel = tk.StringVar()
        self.apartados = ["Vocabulary", "Listening", "Reading", "Speaking", "Writing"]
        
        crear_tabla()
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

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
