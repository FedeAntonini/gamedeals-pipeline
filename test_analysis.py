from analysis import analizar_precio, analizar_juego, clasificar_oferta
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

import pytest

@pytest.mark.parametrize("descuento, esperado", [
    (0, "sin_oferta"),
    (29, "menor"),
    (30, "moderada"),
    (49, "moderada"),
    (50, "buena"),
    (64, "buena"),
    (65, "excepcional"),
    (90, "excepcional"),
])
def test_profundidad_del_descuento(descuento, esperado):
    resultado = clasificar_oferta(precio_final=20.0, precio_lista=40.0, descuento=descuento)
    assert resultado["profundidad"] == esperado


@pytest.mark.parametrize("precio_final, esperado", [
    (4.99, "economico"),
    (10.0, "economico"),
    (10.01, "medio"),
    (30.0, "medio"),
    (30.01, "caro"),
])
def test_nivel_de_precio(precio_final, esperado):
    resultado = clasificar_oferta(precio_final=precio_final, precio_lista=precio_final * 2, descuento=50)
    assert resultado["nivel_precio"] == esperado


def test_oferta_sin_datos_no_inventa_clasificacion():
    resultado = clasificar_oferta(precio_final=None, precio_lista=None, descuento=None)
    assert resultado["profundidad"] == "sin_datos"
    assert resultado["nivel_precio"] == "sin_datos"


def test_explicacion_aclara_que_no_usa_historial():
    resultado = clasificar_oferta(precio_final=35.0, precio_lista=70.0, descuento=50)
    assert "no compara contra el historial" in resultado["explicacion"]
    assert "35.00" in resultado["explicacion"]