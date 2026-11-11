import json 
import os

from fastapi import FastAPI

app = FastAPI(title="MNSR Digital API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

class Obra:
    def init(self, id: int, titulo: str, autor: str, minutos_visita: int):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.minutos_visita = minvisita

    def repor(self):
        return f"Obra(id={self.id}, titulo='{self.titulo}', autor='{self.autor}', minutos_visita={self.minutos_visita})"

class Sala:
    def init(self, nome: str):
        self.nome = nome
        self.obras = []

    def adicionar_obra(self, obra: Obra):
        self.obras.append(obra)

    def repr(self):
        return f"Sala(nome='{self.nome}', obras={self.obras})"

class Roteiro:
    def init(self, nome: str):
        self.nome = nome
        self.salas = []

    def adicionar_obra(self, obra:obra)
        self.obras.append(obra)

    def calcular_tempo_total(self) -> int:
        return sum(obra.minutos_visita for obra in self.obras)

    def repr(self):
        return f"Roteiro(nome='{self.nome}', tempo_total={self.calcular_tempo_total()})"

def carregar_museu_json(caminho_ficheiro: str):
    if not os.path.exists(caminho_ficheiro): printf(f"Ficheiro {caminho_ficheiro} não encontrado.") return []
    with open (caminho_ficheiro, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    lista_obras = []
    for item in dados:
        obra = Obra(
            id=item['id'],
            titulo=item['titulo'],
            autor=item['autor'],
            minutos_visita=item['minutos_visita']
        )
        lista_obras.append(obra)

    return lista_obras