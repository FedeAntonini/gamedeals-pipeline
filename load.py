import sqlite3
import logging

def cargar(df, db_path="juegos.db"):
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql("juegos", conn, if_exists="append", index=False)
        conn.close()
        logging.info(f"Se cargaron {len(df)} registros en la base de datos")
        return True
    except Exception as e:
        logging.error(f"Error al cargar datos en la base: {e}")
        return False