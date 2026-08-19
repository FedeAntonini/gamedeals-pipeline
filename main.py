import logging
from extract import extraer_juegos
from transform import transformar
from load import cargar

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    logging.info("Iniciando pipeline de GameDeals")
    df_crudo = extraer_juegos()
    df_transformado = transformar(df_crudo)
    cargar(df_transformado)
    logging.info("Pipeline finalizado")

if __name__ == "__main__":
    main()