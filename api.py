from fastapi import FastAPI
from queries import listar_juegos

app = FastAPI(title="DealSense API")

@app.get("/games")
def get_games():
    return listar_juegos()