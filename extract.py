import requests
import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extraer_juegos():
    with open("config.json", "r") as f:
        config = json.load(f)

    headers = {
        "User-Agent": "DataPP/1.0 (proyecto de aprendizaje - fede@example.com)"
    }

    resultados = []

    for titulo in config["juegos"]:
        try:
            url = f"https://www.cheapshark.com/api/1.0/games?title={titulo}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            resultados.extend(response.json())
            logging.info(f"Extraidos datos para '{titulo}'")
        except requests.RequestException as e:
            logging.error(f"Error al extraer datos para '{titulo}': {e}")

    return pd.DataFrame(resultados)