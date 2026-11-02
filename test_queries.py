import sqlite3
import pandas as pd
from load import cargar
from queries import listar_juegos, obtener_historial, obtener_ofertas_vigentes


def _cargar_juego(ruta, game_id, nombre, precio, fecha):
    df = pd.DataFrame([{
        "gameID": game_id,
        "external": nombre,
        "internalName": nombre.upper(),
        "thumb": "http://thumb",
        "cheapest": precio,
        "precio_ar": None,
        "moneda_ar": None,
        "initial_ar": None,
        "descuento_ar": None,
        "fecha_extraccion": fecha,
    }])
    cargar(df, db_path=ruta)


def test_listar_juegos_ordenados_por_nombre(tmp_path):
    ruta = str(tmp_path / "test.db")
    _cargar_juego(ruta, "2", "Zelda", 10.0, "2026-11-01 10:00:00")
    _cargar_juego(ruta, "1", "Hollow Knight", 5.0, "2026-11-01 10:00:00")

    juegos = listar_juegos(ruta)

    assert [j["external"] for j in juegos] == ["Hollow Knight", "Zelda"]


def test_historial_de_juego_inexistente_devuelve_none(tmp_path):
    ruta = str(tmp_path / "test.db")
    _cargar_juego(ruta, "1", "Hollow Knight", 5.0, "2026-11-01 10:00:00")

    assert obtener_historial("999", ruta) is None


def test_historial_viene_en_orden_cronologico(tmp_path):
    ruta = str(tmp_path / "test.db")
    _cargar_juego(ruta, "1", "Hollow Knight", 5.0, "2026-11-01 10:00:00")
    _cargar_juego(ruta, "1", "Hollow Knight", 4.0, "2026-11-03 10:00:00")

    historial = obtener_historial("1", ruta)

    assert [h["cheapest"] for h in historial] == [5.0, 4.0]


def test_juego_existente_sin_observaciones_devuelve_lista_vacia(tmp_path):
    ruta = str(tmp_path / "test.db")
    _cargar_juego(ruta, "1", "Hollow Knight", 5.0, "2026-11-01 10:00:00")
    conn = sqlite3.connect(ruta)
    conn.execute("DELETE FROM price_observations")
    conn.commit()
    conn.close()

    assert obtener_historial("1", ruta) == []

def _df_oferta(game_id, precio_ar, initial_ar, descuento, fecha):
    return pd.DataFrame([{
        "gameID": game_id,
        "external": f"Juego {game_id}",
        "internalName": f"JUEGO{game_id}",
        "thumb": "http://thumb",
        "cheapest": 20.0,
        "precio_ar": precio_ar,
        "moneda_ar": "USD",
        "initial_ar": initial_ar,
        "descuento_ar": descuento,
        "fecha_extraccion": fecha,
    }])


def test_ofertas_vigentes_incluye_juegos_con_descuento(tmp_path):
    ruta = str(tmp_path / "test.db")
    cargar(_df_oferta("1", 5.0, 10.0, 50, "2026-11-01 10:00:00"), db_path=ruta)

    ofertas = obtener_ofertas_vigentes(ruta)

    assert [o["gameID"] for o in ofertas] == ["1"]
    assert ofertas[0]["descuento_ar"] == 50


def test_oferta_que_ya_termino_no_aparece_como_vigente(tmp_path):
    ruta = str(tmp_path / "test.db")
    cargar(_df_oferta("1", 5.0, 10.0, 50, "2026-11-01 10:00:00"), db_path=ruta)
    cargar(_df_oferta("1", 10.0, 10.0, 0, "2026-11-03 10:00:00"), db_path=ruta)

    assert obtener_ofertas_vigentes(ruta) == []