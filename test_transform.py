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
        "111": {"precio": 9.99, "moneda": "USD"}
    }

    resultado = agregar_precio_regional(df, precios_regionales)

    assert resultado.loc[resultado["gameID"] == "1", "precio_ar"].iloc[0] == 9.99
    assert resultado.loc[resultado["gameID"] == "1", "moneda_ar"].iloc[0] == "USD"
    assert resultado.loc[resultado["gameID"] == "2", "precio_ar"].isna().iloc[0]