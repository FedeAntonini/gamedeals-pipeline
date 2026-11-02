import sqlite3

def _conectar(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def listar_juegos(db_path="juegos.db"):
    conn = _conectar(db_path)
    filas = conn.execute("""
        SELECT gameID, external, thumb, ultima_verificacion
        FROM games
        ORDER BY external
    """).fetchall()
    conn.close()
    return [dict(fila) for fila in filas]

def obtener_historial(gameID, db_path="juegos.db"):
    """Devuelve la lista de observaciones del juego, o None si el juego no existe."""
    conn = _conectar(db_path)
    existe = conn.execute(
        "SELECT 1 FROM games WHERE gameID = ?", (gameID,)
    ).fetchone()

    if existe is None:
        conn.close()
        return None

    filas = conn.execute("""
        SELECT fecha_extraccion, cheapest, precio_ar, moneda_ar, initial_ar, descuento_ar
        FROM price_observations
        WHERE gameID = ?
        ORDER BY fecha_extraccion, id
    """, (gameID,)).fetchall()
    conn.close()
    return [dict(fila) for fila in filas]