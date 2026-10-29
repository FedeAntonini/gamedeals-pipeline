import requests
import logging

def extraer_precios_regionales(steam_app_ids, cc="ar"):
    ids_unicos = sorted({str(i) for i in steam_app_ids if i is not None and str(i) != "nan"})

    if not ids_unicos:
        return {}

    try:
        url = "https://store.steampowered.com/api/appdetails"
        params = {
            "appids": ",".join(ids_unicos),
            "cc": cc,
            "filters": "price_overview"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error al consultar precios regionales en Steam: {e}")
        return {}

    precios = {}
    for app_id in ids_unicos:
        resultado = data.get(app_id, {})
        overview = resultado.get("data", {}).get("price_overview") if resultado.get("success") else None

        if overview is None:
            precios[app_id] = {"precio": None, "moneda": None}
        else:
            precios[app_id] = {"precio": overview["final"] / 100, "moneda": overview["currency"]}

    return precios