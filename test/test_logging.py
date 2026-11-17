import logging

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_qr_invalido_regista_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="mnsr_digital"):
        client.post("/qr/validar", json={"sessao": "teste", "codigo": "QR-INVALIDO-123"})
    assert any(
        r.levelno == logging.WARNING and "QR rejeitado" in r.getMessage()
        for r in caplog.records
    )


def test_estrategia_desconhecida_regista_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="mnsr_digital"):
        client.get("/roteiros", params={"estrategia": "inexistente"})
    assert any("Estratégia desconhecida" in r.getMessage() for r in caplog.records)
