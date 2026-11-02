import sqlite3
import pandas as pd
from load import cargar


def _df_juego_sin_steam(precio=9.99):
    return pd.DataFrame({
        "gameID": ["1"],
        "external": ["Juego Sin Steam"],
        "internalName": ["SINSTEAM"],
        "thumb": ["http://a"],
        "cheapest": [precio],
        "precio_ar": [float("nan")],
        "moneda_ar": [None],
        "fecha_extraccion": ["2026-11-02 00:00:00"],
    })


def _contar_observaciones(ruta):
    conn = sqlite3.connect(ruta)
    total = conn.execute("SELECT COUNT(*) FROM price_observations").fetchone()[0]
    conn.close()
    return total


def test_juego_sin_precio_ar_no_duplica_observaciones(tmp_path):
    ruta = str(tmp_path / "test.db")
    assert cargar(_df_juego_sin_steam(), db_path=ruta)
    assert cargar(_df_juego_sin_steam(), db_path=ruta)
    assert _contar_observaciones(ruta) == 1


def test_cambio_de_precio_genera_nueva_observacion(tmp_path):
    ruta = str(tmp_path / "test.db")
    cargar(_df_juego_sin_steam(9.99), db_path=ruta)
    cargar(_df_juego_sin_steam(5.99), db_path=ruta)
    assert _contar_observaciones(ruta) == 2

def test_se_guardan_precio_de_lista_y_descuento(tmp_path):
    ruta = str(tmp_path / "test.db")
    df = _df_juego_sin_steam()
    df["precio_ar"] = [4.99]
    df["moneda_ar"] = ["USD"]
    df["initial_ar"] = [9.98]
    df["descuento_ar"] = [50]
    cargar(df, db_path=ruta)

    conn = sqlite3.connect(ruta)
    fila = conn.execute("SELECT initial_ar, descuento_ar FROM price_observations").fetchone()
    conn.close()

    assert fila == (9.98, 50)