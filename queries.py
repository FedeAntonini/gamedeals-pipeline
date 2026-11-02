import sqlite3

def listar_juegos(db_path="juegos.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    filas = conn.execute("""
        SELECT gameID, external, thumb, ultima_verificacion
        FROM games
        ORDER BY external
    """).fetchall()
    conn.close()
    return [dict(fila) for fila in filas]