import pandas as pd
import pytest
from fastapi.testclient import TestClient

import api
from load import cargar


@pytest.fixture
def client(tmp_path, monkeypatch):
    ruta = str(tmp_path / "test.db")
    df = pd.DataFrame([{
        "gameID": "1",
        "external": "Hollow Knight",
        "internalName": "HOLLOWKNIGHT",
        "thumb": "http://thumb",
        "cheapest": 14.99,
        "precio_ar": None,
        "moneda_ar": None,
        "initial_ar": None,
        "descuento_ar": None,
        "fecha_extraccion": "2026-11-01 10:00:00",
    }])
    cargar(df, db_path=ruta)
    monkeypatch.setattr(api, "DB_PATH", ruta)
    return TestClient(api.app)


def test_get_games_devuelve_la_lista(client):
    respuesta = client.get("/games")
    assert respuesta.status_code == 200
    assert [j["external"] for j in respuesta.json()] == ["Hollow Knight"]


def test_history_de_juego_existente(client):
    respuesta = client.get("/games/1/history")
    assert respuesta.status_code == 200
    assert respuesta.json()[0]["cheapest"] == 14.99


def test_history_de_juego_inexistente_es_404(client):
    respuesta = client.get("/games/999/history")
    assert respuesta.status_code == 404
    assert "999" in respuesta.json()["detail"]


def test_analysis_de_juego_existente(client):
    respuesta = client.get("/games/1/analysis")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["external"] == "Hollow Knight"
    assert cuerpo["internacional"]["estado"] == "datos_insuficientes"
    assert cuerpo["argentina"]["estado"] == "sin_datos"


def test_analysis_de_juego_inexistente_es_404(client):
    respuesta = client.get("/games/999/analysis")
    assert respuesta.status_code == 404

@pytest.fixture
def client_con_oferta(tmp_path, monkeypatch):
    ruta = str(tmp_path / "test.db")
    df = pd.DataFrame([{
        "gameID": "2",
        "external": "Juego En Oferta",
        "internalName": "JUEGOENOFERTA",
        "thumb": "http://thumb",
        "cheapest": 19.99,
        "precio_ar": 9.99,
        "moneda_ar": "USD",
        "initial_ar": 19.98,
        "descuento_ar": 50,
        "fecha_extraccion": "2026-11-01 10:00:00",
    }])
    cargar(df, db_path=ruta)
    monkeypatch.setattr(api, "DB_PATH", ruta)
    return TestClient(api.app)


def test_deals_sin_ofertas_devuelve_lista_vacia(client):
    respuesta = client.get("/deals")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_deals_incluye_la_clasificacion(client_con_oferta):
    respuesta = client_con_oferta.get("/deals")
    assert respuesta.status_code == 200
    oferta = respuesta.json()[0]
    assert oferta["external"] == "Juego En Oferta"
    assert oferta["clasificacion"]["profundidad"] == "buena"
    assert oferta["clasificacion"]["nivel_precio"] == "economico"