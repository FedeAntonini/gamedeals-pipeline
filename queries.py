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

def obtener_ofertas_vigentes(db_path="juegos.db"):
    """Juegos cuya última observación tiene un descuento de Steam mayor a cero."""
    conn = _conectar(db_path)
    filas = conn.execute("""
        SELECT g.gameID, g.external, g.thumb,
               p.precio_ar, p.moneda_ar, p.initial_ar, p.descuento_ar,
               p.fecha_extraccion
        FROM games g
        JOIN price_observations p ON p.gameID = g.gameID
        WHERE p.id = (
            SELECT MAX(id) FROM price_observations WHERE gameID = g.gameID
        )
        AND p.descuento_ar > 0
        ORDER BY p.descuento_ar DESC, g.external
    """).fetchall()
    conn.close()
    return [dict(fila) for fila in filas]