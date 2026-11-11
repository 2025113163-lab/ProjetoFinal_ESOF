# Registo de Utilização de IA (AI Log) — MNSR Digital

| Data | Membro | Ferramenta | Prompt / Contexto | Resultado Gerado | Validação / Ação Humana |
|---|---|---|---|---|---|
| 2026-11-11 | Robi | Gemini / Claude | Padronização do `data/museu.json`, implementação do Módulo A (`gerador_roteiro`), padrão `RoteiroStrategy` (`RotaMaisCurta`, `RotaMenosCrowded`, `RotaFamiliar`) e testes unitários em `test/test_roteiro.py`. | Código das classes de domínio, 3 estratégias concretas, endpoint `GET /roteiros` e suite de 5 testes unitários. | Revisto e testado localmente com `pytest --cov=src`. Corrigida a chave `Titulo`/`autor` no JSON e validada cobertura de 90% (6/6 testes a passar). |
