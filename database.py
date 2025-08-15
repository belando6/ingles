import sqlite3
import datetime

class Database:
    def __init__(self, db_file="vocabulario.db"):
        self.db_file = db_file
        self.crear_tablas()

    def conectar(self):
        return sqlite3.connect(self.db_file)

    def crear_tablas(self):
        with self.conectar() as conn:
            c = conn.cursor()
            # Vocabulario
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
            # Listening
            c.execute("""
                CREATE TABLE IF NOT EXISTS listening (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nivel TEXT,
                    canal TEXT,
                    titulo TEXT,
                    url TEXT,
                    fallos INTEGER DEFAULT 0,
                    pdf TEXT
                )
            """)
            conn.commit()

    # ----- VOCABULARIO -----
    def palabra_existe(self, palabra, nivel):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM vocabulario WHERE palabra=? AND nivel=?", (palabra, nivel))
            return c.fetchone() is not None

    def insertar_palabra(self, palabra, traduccion, ejemplo, tipo, nivel, estado="pendiente"):
        if self.palabra_existe(palabra, nivel):
            return False
        with self.conectar() as conn:
            c = conn.cursor()
            fecha = datetime.date.today().isoformat()
            c.execute("""INSERT INTO vocabulario (palabra, traduccion, ejemplo, tipo, nivel, fecha, estado)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (palabra, traduccion, ejemplo, tipo, nivel, fecha, estado))
            conn.commit()
        return True

    def obtener_palabras(self, estado=None, nivel=None, fecha=None):
        query = "SELECT id, palabra, traduccion, ejemplo, tipo FROM vocabulario WHERE 1=1"
        params = []
        if estado:
            query += " AND estado=?"
            params.append(estado)
        if nivel:
            query += " AND nivel=?"
            params.append(nivel)
        if fecha:
            query += " AND fecha=?"
            params.append(fecha)
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute(query, tuple(params))
            return c.fetchall()

    def obtener_todas_palabras(self, nivel):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT id, palabra, traduccion, ejemplo, tipo FROM vocabulario WHERE nivel=?", (nivel,))
            return c.fetchall()

    def actualizar_estado(self, id_palabra, nuevo_estado):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("UPDATE vocabulario SET estado=? WHERE id=?", (nuevo_estado, id_palabra))
            conn.commit()

    def eliminar_palabra(self, palabra_id):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM vocabulario WHERE id=?", (palabra_id,))
            conn.commit()

    def obtener_estado_palabra(self, id_palabra):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT estado FROM vocabulario WHERE id=?", (id_palabra,))
            row = c.fetchone()
            return row[0] if row else None

    def obtener_todas_palabras_con_estado(self, nivel):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT id, palabra, traduccion, ejemplo, tipo, estado FROM vocabulario WHERE nivel=?", (nivel,))
            return c.fetchall()


    # ----- LISTENING -----
    def insertar_listening(self, nivel, canal, titulo, url, fallos=0, pdf=None):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO listening (nivel, canal, titulo, url, fallos, pdf)
                         VALUES (?, ?, ?, ?, ?, ?)""", (nivel, canal, titulo, url, fallos, pdf))
            conn.commit()


    def actualizar_fallos(self, id_audio, fallos):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("UPDATE listening SET fallos=? WHERE id=?", (fallos, id_audio))
            conn.commit()

    def aumentar_fallos(id_audio):
        conn = sqlite3.connect("vocabulario.db")
        c = conn.cursor()
        c.execute("UPDATE listening SET fallos = fallos + 1 WHERE id = ?", (id_audio,))
        conn.commit()
        conn.close()

    def obtener_listening(self, nivel=None):
        with self.conectar() as conn:
            c = conn.cursor()
            if nivel:
                c.execute("SELECT id, nivel, canal, titulo, url, fallos, pdf FROM listening WHERE nivel=?", (nivel,))
            else:
                c.execute("SELECT id, nivel, canal, titulo, url, fallos, pdf FROM listening")
            return c.fetchall()

    def eliminar_listening(self, id_audio):
        with self.conectar() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM listening WHERE id=?", (id_audio,))
        conn.commit()