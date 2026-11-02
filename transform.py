import pandas as pd
import logging
from datetime import datetime

def transformar(df):
    if df.empty:
        return df

    df = df[["gameID", "external", "internalName", "thumb", "steamAppID", "cheapest"]].copy()

    df["cheapest"] = pd.to_numeric(df["cheapest"], errors="coerce")
    invalidos = df["cheapest"].isna().sum()
    if invalidos > 0:
        logging.warning(f"Se descartaron {invalidos} fila(s) con 'cheapest' inválido o ausente")
        df = df.dropna(subset=["cheapest"])

    duplicados = df.duplicated(subset=["gameID"]).sum()
    if duplicados > 0:
        logging.warning(f"Se descartaron {duplicados} fila(s) duplicada(s) por gameID repetido en esta corrida")
        df = df.drop_duplicates(subset=["gameID"], keep="first")

    df["fecha_extraccion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df.sort_values("cheapest")
    return df


def agregar_precio_regional(df, precios_regionales):
    df = df.copy()
    columnas = {
        "precio_ar": "precio",
        "moneda_ar": "moneda",
        "initial_ar": "precio_lista",
        "descuento_ar": "descuento",
    }
    for columna, clave in columnas.items():
        df[columna] = df["steamAppID"].map(
            lambda sid, c=clave: precios_regionales.get(str(sid), {}).get(c)
        )
    return df