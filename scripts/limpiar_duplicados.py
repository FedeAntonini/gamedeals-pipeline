import sqlite3

SQL_REPETIDAS = """
SELECT p.id FROM price_observations p
WHERE EXISTS (
    SELECT 1 FROM price_observations q
    WHERE q.gameID = p.gameID
      AND q.id = (SELECT MAX(r.id) FROM price_observations r
                  WHERE r.gameID = p.gameID AND r.id < p.id)
      AND q.cheapest IS p.cheapest
      AND q.precio_ar IS p.precio_ar
)
"""

conn = sqlite3.connect("juegos.db")
ids = [fila[0] for fila in conn.execute(SQL_REPETIDAS).fetchall()]
print(f"Filas repetidas (igual a la observación anterior del mismo juego): {len(ids)}")

if ids and input("¿Borrarlas? (s/n): ").strip().lower() == "s":
    conn.executemany("DELETE FROM price_observations WHERE id = ?", [(i,) for i in ids])
    conn.commit()
    print("Listo.")
conn.close()