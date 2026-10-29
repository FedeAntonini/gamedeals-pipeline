import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

def migrar():
    conn = sqlite3.connect("juegos.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            gameID TEXT PRIMARY KEY,
            external TEXT,
            internal_name TEXT,
            thumb TEXT,
            ultima_verificacion TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gameID TEXT,
            cheapest REAL,
            fecha_extraccion TEXT,
            FOREIGN KEY (gameID) REFERENCES games(gameID)
        )
    """)

    filas = cursor.execute("""
        SELECT gameID, external, cheapest, fecha_extraccion
        FROM juegos
        WHERE gameID IS NOT NULL
        ORDER BY gameID, fecha_extraccion
    """).fetchall()

    salteadas = cursor.execute("SELECT COUNT(*) FROM juegos WHERE gameID IS NULL").fetchone()[0]
    logging.info(f"Filas sin gameID (salteadas, no migrables): {salteadas}")

    ultimo_precio_por_juego = {}

    for game_id, external, cheapest, fecha in filas:
        cursor.execute("""
            INSERT INTO games (gameID, external, ultima_verificacion)
            VALUES (?, ?, ?)
            ON CONFLICT(gameID) DO UPDATE SET
                external = excluded.external,
                ultima_verificacion = excluded.ultima_verificacion
        """, (game_id, external, fecha))

        if ultimo_precio_por_juego.get(game_id) != cheapest:
            cursor.execute("""
                INSERT INTO price_observations (gameID, cheapest, fecha_extraccion)
                VALUES (?, ?, ?)
            """, (game_id, cheapest, fecha))
            ultimo_precio_por_juego[game_id] = cheapest

    conn.commit()

    total_games = cursor.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    total_obs = cursor.execute("SELECT COUNT(*) FROM price_observations").fetchone()[0]
    logging.info(f"Migración completa: {total_games} juegos, {total_obs} observaciones de precio")

    conn.close()

if __name__ == "__main__":
    migrar()