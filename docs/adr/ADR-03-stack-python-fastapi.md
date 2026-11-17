# ADR-03: Stack do backend em Python e FastAPI

- **Estado:** Proposta
- **Data:** 2026-11-17
- **Marco:** M2

## Contexto

O enunciado permite Java (Spring Boot) ou Python (FastAPI) para o backend REST. A equipa precisa de iterar depressa, ter testes unitários e de integração simples (RNF-05), validação rigorosa de entradas (QR Codes nulos, vazios ou corrompidos) e, mais tarde, integrar um módulo RAG/IA com respostas em streaming (RNF-01).

## Decisão Considerada

Usar **Python 3.12 com FastAPI** (servido com Uvicorn), **Pydantic** para validação de pedidos, **pytest** + **pytest-cov** para testes e cobertura, **httpx/TestClient** para testes de endpoints e **Ruff** como linter. O CI corre em GitHub Actions (`.github/workflows/ci.yml`) com quality gate de cobertura >= 80%.

Alternativas consideradas:

1. **Java + Spring Boot (JUnit/JaCoCo)**: robusto e alinhado com o enunciado, mas com mais código de arranque e configuração para o ritmo do projeto.
2. **Flask**: mais simples, mas sem validação e documentação OpenAPI integradas e com pior suporte a streaming assíncrono.
3. **Node.js/TypeScript no backend**: permitiria uma só linguagem com o cliente, mas as bibliotecas de IA/RAG estão mais maduras em Python.

## Consequências

- (+) Validação automática (Pydantic) e documentação interativa da API em `/docs` sem esforço extra.
- (+) Suporte nativo a `async` e streaming, útil para o assistente de IA (RNF-01: primeiro token em < 2,5 s).
- (+) Ecossistema Python para o RAG (clientes de LLM, bases de dados vetoriais).
- (+) Testes rápidos: lógica de domínio testável com `unittest`/`pytest` sem arrancar servidor.
- (-) Tipagem estática opcional: convém usar anotações de tipo e Ruff de forma consistente para evitar erros em runtime.
- (-) Desempenho bruto inferior ao da JVM; para a carga prevista (200 utilizadores simultâneos) é considerado suficiente e será medido no M4.
- (-) As dependências em `requirements.txt` não têm versões fixadas; deve passar a usar-se versões fixas (ou ficheiro de lock) e auditoria de dependências no M5.
