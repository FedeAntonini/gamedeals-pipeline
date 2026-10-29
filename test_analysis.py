from analysis import analizar_precio, analizar_juego
import sqlite3


def test_sin_observaciones_devuelve_sin_datos():
    resultado = analizar_precio([], "2026-10-29 18:00:00")
    assert resultado["estado"] == "sin_datos"


def test_pocos_dias_devuelve_datos_insuficientes():
    observaciones = [("2026-10-29 10:00:00", 10.0)]
    resultado = analizar_precio(observaciones, "2026-10-29 18:00:00")
    assert resultado["estado"] == "datos_insuficientes"


def test_precio_en_el_minimo_es_buena_oportunidad():
    observaciones = [("2026-10-01 10:00:00", 10.0), ("2026-10-15 10:00:00", 8.0)]
    resultado = analizar_precio(observaciones, "2026-10-29 18:00:00")
    assert resultado["estado"] == "buena_oportunidad"


def test_precio_muy_por_encima_del_minimo_sugiere_esperar():
    observaciones = [("2026-10-01 10:00:00", 10.0), ("2026-10-15 10:00:00", 20.0)]
    resultado = analizar_precio(observaciones, "2026-10-29 18:00:00")
    assert resultado["estado"] == "esperar"


def test_precio_cerca_del_minimo_es_posible_oportunidad():
    observaciones = [("2026-10-01 10:00:00", 10.0), ("2026-10-15 10:00:00", 10.5)]
    resultado = analizar_precio(observaciones, "2026-10-29 18:00:00")
    assert resultado["estado"] == "posible_oportunidad"


def _crear_db_de_prueba(ruta):
    conn = sqlite3.connect(ruta)
    conn.execute("""
        CREATE TABLE games (
            gameID TEXT PRIMARY KEY,
            external TEXT,
            internal_name TEXT,
            thumb TEXT,
            ultima_verificacion TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE price_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gameID TEXT,
            cheapest REAL,
            precio_ar REAL,
            moneda_ar TEXT,
            fecha_extraccion TEXT
        )
    """)
    conn.execute(
        "INSERT INTO games (gameID, external, ultima_verificacion) VALUES (?, ?, ?)",
        ("1", "Juego de Prueba", "2026-10-29 18:00:00")
    )
    conn.executemany(
        "INSERT INTO price_observations (gameID, cheapest, precio_ar, fecha_extraccion) VALUES (?, ?, ?, ?)",
        [
            ("1", 20.0, 15.0, "2026-10-01 10:00:00"),
            ("1", 10.0, 7.0, "2026-10-15 10:00:00"),
        ]
    )
    conn.commit()
    conn.close()


def test_analizar_juego_devuelve_ambos_analisis(tmp_path):
    ruta_db = str(tmp_path / "test.db")
    _crear_db_de_prueba(ruta_db)

    resultado = analizar_juego("1", db_path=ruta_db)

    assert resultado["external"] == "Juego de Prueba"
    assert resultado["internacional"]["estado"] == "buena_oportunidad"
    assert resultado["argentina"]["estado"] == "buena_oportunidad"


def test_analizar_juego_no_encontrado(tmp_path):
    ruta_db = str(tmp_path / "test.db")
    _crear_db_de_prueba(ruta_db)

    resultado = analizar_juego("999", db_path=ruta_db)

    assert "error" in resultado