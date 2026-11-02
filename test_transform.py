import pandas as pd
from transform import transformar, agregar_precio_regional

def test_dataframe_vacio_no_rompe():
    df_vacio = pd.DataFrame()
    resultado = transformar(df_vacio)
    assert resultado.empty


def test_transformacion_normal():
    df = pd.DataFrame({
        "gameID": ["1", "2"],
        "external": ["Juego Caro", "Juego Barato"],
        "internalName": ["JUEGOCARO", "JUEGOBARATO"],
        "thumb": ["http://a", "http://b"],
        "cheapest": ["19.99", "4.99"],
        "steamAppID": ["111", "222"],
    })
    resultado = transformar(df)

    assert resultado.iloc[0]["external"] == "Juego Barato"
    assert resultado["cheapest"].dtype == float


def test_precio_invalido_se_descarta():
    df = pd.DataFrame({
        "gameID": ["1", "2"],
        "external": ["Juego Valido", "Juego Sin Precio"],
        "internalName": ["A", "B"],
        "thumb": ["http://a", "http://b"],
        "cheapest": ["9.99", None],
        "steamAppID": ["111", "222"],
    })
    resultado = transformar(df)

    assert len(resultado) == 1
    assert resultado.iloc[0]["gameID"] == "1"


def test_duplicado_por_gameid_se_descarta():
    df = pd.DataFrame({
        "gameID": ["1", "1"],
        "external": ["Juego A", "Juego A (duplicado)"],
        "internalName": ["A", "A"],
        "thumb": ["http://a", "http://a"],
        "cheapest": ["9.99", "9.99"],
        "steamAppID": ["111", "222"],
    })
    resultado = transformar(df)

    assert len(resultado) == 1

def test_agregar_precio_regional_combina_datos():
    df = pd.DataFrame({
        "gameID": ["1", "2"],
        "external": ["Juego Con Precio AR", "Juego Sin Steam"],
        "internalName": ["A", "B"],
        "thumb": ["http://a", "http://b"],
        "steamAppID": ["111", None],
        "cheapest": [19.99, 9.99],
        "fecha_extraccion": ["2026-10-29 00:00:00", "2026-10-29 00:00:00"],
    })

    precios_regionales = {
        "111": {"precio": 9.99, "moneda": "USD", "precio_lista": 19.98, "descuento": 50}
    }

    resultado = agregar_precio_regional(df, precios_regionales)
    con_steam = resultado[resultado["gameID"] == "1"].iloc[0]
    sin_steam = resultado[resultado["gameID"] == "2"].iloc[0]

    assert con_steam["precio_ar"] == 9.99
    assert con_steam["moneda_ar"] == "USD"
    assert con_steam["initial_ar"] == 19.98
    assert con_steam["descuento_ar"] == 50
    assert pd.isna(sin_steam["precio_ar"])
    assert pd.isna(sin_steam["descuento_ar"])