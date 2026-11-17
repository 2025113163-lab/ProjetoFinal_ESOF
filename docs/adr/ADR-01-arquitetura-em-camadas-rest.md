# ADR-01: Arquitetura em camadas com API REST

- **Estado:** Proposta
- **Data:** 2026-11-17
- **Marco:** M2

## Contexto

A App MNSR Digital tem uma interface móvel (PWA), lógica de negócio (roteiros, caça ao tesouro, afluência, assistente de IA) e dados do acervo. O enunciado exige desacoplamento entre interface, lógica e dados (arquitetura em camadas / REST), e o requisito RNF-05 pede baixo acoplamento e testabilidade (cobertura >= 80%). A equipa é pequena (4 pessoas) e o projeto decorre em poucas semanas.

## Decisão Considerada

Adotar uma **arquitetura em 3 camadas** exposta por uma **API REST**, num único serviço (monólito modular):

| Camada | Responsabilidade | Onde está / ficará |
|---|---|---|
| Apresentação | PWA: mapas, leitura de QR Codes, chat, cache offline | Cliente (a desenvolver) |
| Aplicação / API | Endpoints REST (`/roteiros`, `/qr/validar`, `/desafios/responder`, `/pistas`, `/health`), validação de pedidos, logging com `X-Request-ID` | `src/main.py` |
| Domínio e dados | `Obra`, `Roteiro`, estratégias de rota, `QRCode`, `Desafio` (e subtipos), `DesafioFactory`, `Recompensa`, `AfluenciaSala`; leitura do acervo | `src/main.py`, `src/afluencia.py`, `data/museu.json` |

A comunicação entre cliente e servidor é feita apenas por HTTP/JSON. A lógica de negócio não depende da framework web (por exemplo, `src/afluencia.py` não importa FastAPI), o que permite testá-la sem arrancar o servidor.

Alternativas consideradas:

1. **Microserviços** (roteiros, gamificação, IA separados): rejeitada. Aumenta a complexidade de deploy e de CI sem benefício para o tamanho da equipa e do projeto.
2. **MVC com páginas geradas no servidor**: rejeitada. Não serve o requisito de funcionamento offline (RNF-02) nem a experiência de app móvel.
3. **Monólito sem separação interna**: rejeitada. Dificulta testes e a aplicação dos padrões Strategy, Observer e Factory.

## Consequências

- (+) Fronteiras claras: o cliente pode evoluir independentemente da API; o domínio é testável com `pytest` sem rede.
- (+) Um só processo e um só pipeline de CI (`.github/workflows/ci.yml`).
- (+) A estratégia de rota, o Observer e a Factory vivem na camada de domínio, sem acoplamento a HTTP.
- (-) Estado atual: API e domínio partilham o ficheiro `src/main.py`. Tem de ser repartido em módulos/pacotes (por exemplo `api/`, `dominio/`, `dados/`) para cumprir a separação rigorosa em 3 camadas até ao M3/M5.
- (-) O progresso da caça ao tesouro (`_SESSOES`) está em memória; ao escalar para várias instâncias terá de passar para armazenamento partilhado.
- (-) O módulo RAG/IA (M5) será um componente interno chamado pela camada de API, a documentar em ADR próprio quando for implementado.
