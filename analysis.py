from datetime import datetime
import sqlite3
from queries import obtener_ofertas_vigentes

def analizar_precio(observaciones, ultima_verificacion, umbral_dias=7, umbral_porcentaje=15):
    observaciones = [(f, p) for f, p in observaciones if p is not None]

    if not observaciones:
        return {
            "estado": "sin_datos",
            "explicacion": "Todavía no tenemos ningún precio registrado para este juego en esta región."
        }

    formato = "%Y-%m-%d %H:%M:%S"
    primera_fecha = datetime.strptime(observaciones[0][0], formato)
    fecha_verificacion = datetime.strptime(ultima_verificacion, formato)
    dias_trackeado = (fecha_verificacion - primera_fecha).days

    precio_minimo = min(p for _, p in observaciones)
    precio_actual = observaciones[-1][1]

    if dias_trackeado < umbral_dias:
        return {
            "estado": "datos_insuficientes",
            "precio_actual": precio_actual,
            "precio_minimo_registrado": precio_minimo,
            "dias_trackeado": dias_trackeado,
            "explicacion": (
                f"Venimos siguiendo este precio hace {dias_trackeado} día(s) — todavía no es "
                f"suficiente para evaluar si es una buena oportunidad. Necesitamos al menos "
                f"{umbral_dias} días de historial."
            )
        }

    diferencia_pct = ((precio_actual - precio_minimo) / precio_minimo) * 100 if precio_minimo > 0 else 0

    if precio_actual <= precio_minimo:
        return {
            "estado": "buena_oportunidad",
            "precio_actual": precio_actual,
            "precio_minimo_registrado": precio_minimo,
            "dias_trackeado": dias_trackeado,
            "explicacion": (
                f"El precio actual (${precio_actual}) está en el mínimo que registramos "
                f"en los últimos {dias_trackeado} días."
            )
        }

    if diferencia_pct > umbral_porcentaje:
        return {
            "estado": "esperar",
            "precio_actual": precio_actual,
            "precio_minimo_registrado": precio_minimo,
            "diferencia_pct": round(diferencia_pct, 1),
            "dias_trackeado": dias_trackeado,
            "explicacion": (
                f"El precio actual (${precio_actual}) está un {round(diferencia_pct, 1)}% por encima "
                f"del mínimo que registramos (${precio_minimo}) en los últimos {dias_trackeado} días. "
                f"Probablemente convenga esperar."
            )
        }

    return {
        "estado": "posible_oportunidad",
        "precio_actual": precio_actual,
        "precio_minimo_registrado": precio_minimo,
        "diferencia_pct": round(diferencia_pct, 1),
        "dias_trackeado": dias_trackeado,
        "explicacion": (
            f"El precio actual (${precio_actual}) está solo un {round(diferencia_pct, 1)}% por encima "
            f"del mínimo que registramos (${precio_minimo}) en los últimos {dias_trackeado} días. "
            f"Podría ser un buen momento, aunque no es el mínimo exacto."
        )
    }

def analizar_juego(gameID, db_path="juegos.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    fila_juego = cursor.execute(
        "SELECT external, ultima_verificacion FROM games WHERE gameID = ?", (gameID,)
    ).fetchone()

    if fila_juego is None:
        conn.close()
        return {"error": f"No se encontró el juego con gameID={gameID}"}

    external, ultima_verificacion = fila_juego

    filas = cursor.execute(
        "SELECT fecha_extraccion, cheapest, precio_ar FROM price_observations "
        "WHERE gameID = ? ORDER BY fecha_extraccion",
        (gameID,)
    ).fetchall()

    conn.close()

    observaciones_internacional = [(f, c) for f, c, _ in filas]
    observaciones_ar = [(f, a) for f, _, a in filas]

    return {
        "external": external,
        "internacional": analizar_precio(observaciones_internacional, ultima_verificacion),
        "argentina": analizar_precio(observaciones_ar, ultima_verificacion),
    }

def clasificar_oferta(precio_final, precio_lista, descuento):
    """Clasifica una oferta de Steam según la profundidad del descuento y el nivel de precio.

    Se apoya solo en el descuento que informa Steam en este momento;
    no usa historial, así que no dice si el precio es bajo respecto del pasado.
    """
    if precio_final is None or precio_lista is None or descuento is None:
        return {
            "profundidad": "sin_datos",
            "nivel_precio": "sin_datos",
            "explicacion": "No hay datos de precio de Steam para este juego, no se puede clasificar la oferta.",
        }

    if descuento <= 0:
        profundidad = "sin_oferta"
    elif descuento < 30:
        profundidad = "menor"
    elif descuento < 50:
        profundidad = "moderada"
    elif descuento < 65:
        profundidad = "buena"
    else:
        profundidad = "excepcional"

    if precio_final <= 10:
        nivel_precio = "economico"
    elif precio_final <= 30:
        nivel_precio = "medio"
    else:
        nivel_precio = "caro"

    if profundidad == "sin_oferta":
        explicacion = f"Steam no informa descuento: el precio actual es USD {precio_final:.2f}."
    else:
        explicacion = (
            f"Steam informa {descuento}% de descuento "
            f"(de USD {precio_lista:.2f} a USD {precio_final:.2f}): "
            f"descuento {profundidad}, juego de rango {nivel_precio}. "
            "Esta clasificación se basa solo en el descuento de Steam; "
            "no compara contra el historial de precios."
        )

    return {
        "profundidad": profundidad,
        "nivel_precio": nivel_precio,
        "explicacion": explicacion,
    }

def listar_ofertas(db_path="juegos.db"):
    ofertas = obtener_ofertas_vigentes(db_path)
    for oferta in ofertas:
        oferta["clasificacion"] = clasificar_oferta(
            oferta["precio_ar"], oferta["initial_ar"], oferta["descuento_ar"]
        )
    return ofertas