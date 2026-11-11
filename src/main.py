from fastapi import FastAPI

app = FastAPI(title="MNSR Digital API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}