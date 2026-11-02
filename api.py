from fastapi import FastAPI, HTTPException
from queries import listar_juegos, obtener_historial

DB_PATH = "juegos.db"

app = FastAPI(title="DealSense API")

@app.get("/games")
def get_games():
    return listar_juegos(DB_PATH)

@app.get("/games/{game_id}/history")
def get_game_history(game_id: str):
    historial = obtener_historial(game_id, DB_PATH)
    if historial is None:
        raise HTTPException(status_code=404, detail=f"No se encontró el juego con gameID={game_id}")
    return historial