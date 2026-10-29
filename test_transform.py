import pandas as pd
from transform import transformar


def test_dataframe_vacio_no_rompe():
    # Cubre el caso que arreglamos antes: si no hay datos, no debe explotar
    df_vacio = pd.DataFrame()
    resultado = transformar(df_vacio)
    assert resultado.empty


def test_transformacion_normal():
    # Caso feliz: columnas correctas, tipo de dato correcto, ordenado por precio
    df = pd.DataFrame({
        "gameID": ["1", "2"],
        "external": ["Juego Caro", "Juego Barato"],
        "cheapest": ["19.99", "4.99"],
    })
    resultado = transformar(df)

    assert list(resultado.columns) == ["gameID", "external", "cheapest", "fecha_extraccion"]
    assert resultado.iloc[0]["external"] == "Juego Barato"  # el más barato queda primero
    assert resultado["cheapest"].dtype == float


def test_precio_invalido_se_descarta():
    # Cubre el arreglo A: un precio inválido no debe tirar abajo la fila ni el resto
    df = pd.DataFrame({
        "gameID": ["1", "2"],
        "external": ["Juego Valido", "Juego Sin Precio"],
        "cheapest": ["9.99", None],
    })
    resultado = transformar(df)

    assert len(resultado) == 1
    assert resultado.iloc[0]["gameID"] == "1"


def test_duplicado_por_gameid_se_descarta():
    # Cubre el arreglo C: mismo gameID repetido en la corrida, debe quedar solo una vez
    df = pd.DataFrame({
        "gameID": ["1", "1"],
        "external": ["Juego A", "Juego A (duplicado)"],
        "cheapest": ["9.99", "9.99"],
    })
    resultado = transformar(df)

    assert len(resultado) == 1