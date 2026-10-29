import logging
import os
from extract import extraer_juegos
from extract_steam import extraer_precios_regionales
from transform import transformar, agregar_precio_regional
from load import cargar

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode="a"),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Iniciando pipeline de GameDeals")
    df_crudo = extraer_juegos()
    df_transformado = transformar(df_crudo)

    if not df_transformado.empty:
        precios_ar = extraer_precios_regionales(df_transformado["steamAppID"])
        df_transformado = agregar_precio_regional(df_transformado, precios_ar)

    exito = cargar(df_transformado)
    if exito:
        logging.info("Pipeline finalizado correctamente")
    else:
        logging.error("Pipeline finalizado CON ERRORES en la carga")

if __name__ == "__main__":
    main()