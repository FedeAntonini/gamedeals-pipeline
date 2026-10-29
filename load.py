import sqlite3
import logging

def _crear_tablas(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            gameID TEXT PRIMARY KEY,
            external TEXT,
            internal_name TEXT,
            thumb TEXT,
            ultima_verificacion TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gameID TEXT,
            cheapest REAL,
            precio_ar REAL,
            moneda_ar TEXT,
            fecha_extraccion TEXT,
            FOREIGN KEY (gameID) REFERENCES games(gameID)
        )
    """)

def cargar(df, db_path="juegos.db"):
    try:
        conn = sqlite3.connect(db_path)
        _crear_tablas(conn)
        cursor = conn.cursor()
        nuevas_observaciones = 0

        for _, fila in df.iterrows():
            cursor.execute("""
                INSERT INTO games (gameID, external, internal_name, thumb, ultima_verificacion)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(gameID) DO UPDATE SET
                    external = excluded.external,
                    internal_name = excluded.internal_name,
                    thumb = excluded.thumb,
                    ultima_verificacion = excluded.ultima_verificacion
            """, (fila["gameID"], fila["external"], fila.get("internalName"), fila.get("thumb"), fila["fecha_extraccion"]))

            ultimo = cursor.execute("""
                SELECT cheapest, precio_ar FROM price_observations
                WHERE gameID = ?
                ORDER BY id DESC LIMIT 1
            """, (fila["gameID"],)).fetchone()

            precio_ar = fila.get("precio_ar")
            cambio = ultimo is None or ultimo[0] != fila["cheapest"] or ultimo[1] != precio_ar

            if cambio:
                cursor.execute("""
                    INSERT INTO price_observations (gameID, cheapest, precio_ar, moneda_ar, fecha_extraccion)
                    VALUES (?, ?, ?, ?, ?)
                """, (fila["gameID"], fila["cheapest"], precio_ar, fila.get("moneda_ar"), fila["fecha_extraccion"]))
                nuevas_observaciones += 1

        conn.commit()
        conn.close()
        logging.info(f"Carga completa: {len(df)} juegos procesados, {nuevas_observaciones} observación(es) de precio nueva(s)")
        return True
    except Exception as e:
        logging.error(f"Error al cargar datos en la base: {e}")
        return False