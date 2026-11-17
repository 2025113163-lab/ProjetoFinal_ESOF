# Matriz de Rastreabilidade: Marcos M1 a M3

Esta matriz liga cada requisito às User Stories, à implementação, aos testes automáticos e às decisões de arquitetura (ADRs). Atualiza-se a cada marco.

**Legenda de estado:** ✅ Implementado e testado · 🟡 Parcial · ⬜ Pendente

**Resumo dos testes (CI):** 54 testes a passar, cobertura total de 96% (mínimo exigido pelo Quality Gate: 80%).

## 1. Requisitos funcionais

Os identificadores RF-xx seguem o enunciado do caso de estudo.

| Requisito | Módulo | EPIC | User Story | Issue | Implementação | Testes | Estado |
|---|---|---|---|---|---|---|---|
| RF-01 a RF-04: Gerador de roteiros por tempo disponível (30/60/90 min) e interesses, com rota e tempo por obra | A | EPIC-01 (#1) | US-01 | #4 | `GET /roteiros`, `gerador_roteiro`, `RoteiroStrategy` (`RotaMaisCurta`, `RotaMenosCrowded`, `RotaFamiliar`) em `src/main.py` | `test/test_roteiro.py` | 🟡 (falta o mapa visual das salas, previsto no frontend) |
| Consultar o conteúdo de uma obra (ex.: "O Desterrado") | A | EPIC-01 (#1) | US-02 | #5 | Dados da obra em `data/museu.json`; ainda sem endpoint próprio | | ⬜ |
| RF-05 a RF-08: Ler QR Codes e desbloquear pistas da caça ao tesouro | B | EPIC-02 (#2) | US-03 | #6 | `QRCode`, `POST /qr/validar`, `GET /pistas` em `src/main.py` | `test/test_qr.py`, `test/test_qr_integracao.py`, `test/test_qr_refactor.py` | ✅ |
| RF-05 a RF-08: Desafios de vários tipos (pergunta, QR, beacon simulado) | B | EPIC-02 (#2) | US-03 | #6 | `Desafio`, `DesafioPergunta`, `DesafioQR`, `DesafioBeacon`, `DesafioFactory` | `test/test_qr.py`, `test/test_qr_integracao.py` | ✅ |
| RF-05 a RF-08: Medalhas e descontos por desafios resolvidos | B | EPIC-02 (#2) | US-03 | #6 | `Recompensa`, `POST /desafios/responder` | `test/test_qr_integracao.py` | ✅ (limiares 3/6/10 e descontos 5/10/15% a validar com o Product Owner) |
| Caça ao tesouro em modo anónimo (sem dados pessoais) | B | EPIC-02 (#2) | US-04 | #7 | Progresso por sessão anónima em memória; sem dados pessoais nos logs | `test/test_qr_integracao.py` | ✅ |
| RF-09 a RF-12: Assistente conversacional de IA com RAG | C | EPIC-03 (#3) | US-05 | #8 | | | ⬜ |
| Recusar temas externos e evitar alucinações | C | EPIC-03 (#3) | US-06 | #9 | | | ⬜ |
| RF-13 a RF-15: Indicador de afluência por sala e notificações | D | EPIC-04 (#a criar) | US-07 | #a criar | Previsto: `AfluenciaSala` e padrão Observer | | ⬜ |

## 2. Requisitos não funcionais (ISO/IEC 25010)

| Requisito | Categoria | User Story | Implementação / evidência | Testes | ADR | Estado |
|---|---|---|---|---|---|---|
| RNF-01: Tempo de resposta (roteiro < 1,5 s; IA em streaming < 2,5 s) | Desempenho | US-01 | | Por medir | ADR-03 | ⬜ |
| RNF-02: Funcionamento offline nas salas | Fiabilidade | US-01, US-02 | Dados locais em `data/museu.json`; sem frontend offline ainda | | ADR-02 | ⬜ |
| RNF-03: RGPD e proteção de menores (sem dados pessoais identificáveis) | Segurança e privacidade | US-04 | Sessões anónimas; os logs não registam a sessão nem dados pessoais | `test/test_qr_integracao.py` | ADR-03 | 🟡 (falta auditoria OWASP e STRIDE no M5) |
| RNF-04: Acessibilidade WCAG 2.1 AA | Usabilidade | US-08 | | | | ⬜ |
| RNF-05: Cobertura de testes ≥ 80% e análise estática | Manutenibilidade | Transversal | Quality Gate no CI (`--cov-fail-under=80`) e Ruff em cada PR; cobertura atual de 96% | Todos os ficheiros de `test/` | ADR-01 | 🟡 (falta análise SonarQube) |
| Logging estruturado em JSON com `request_id` | Observabilidade (M4) | Transversal | `JSONFormatter` e middleware em `src/main.py` | `test/test_logging.py` | ADR-03 | ✅ |
| Verificação de estado do serviço | Fiabilidade | Transversal | `GET /health` | `test/test_health.py` | ADR-01 | ✅ |

## 3. User Stories, cenários BDD e testes

Os cenários BDD de cada User Story estão descritos na respetiva issue do GitHub. Os testes automáticos que as cobrem são:

| User Story | Cenários BDD | Ficheiros de teste | Estado |
|---|---|---|---|
| US-01 Gerar roteiro por tempo disponível | C1, C2 | `test/test_roteiro.py` | ✅ |
| US-02 Consultar conteúdo de uma obra | C1, C2 | | ⬜ |
| US-03 Desbloquear pista por QR Code | C1, C2 | `test/test_qr.py`, `test/test_qr_integracao.py`, `test/test_qr_refactor.py` | ✅ |
| US-04 Caça ao tesouro em modo anónimo | C1, C2 | `test/test_qr_integracao.py` | ✅ |
| US-05 Perguntar ao assistente sobre uma obra | C1, C2 | | ⬜ |
| US-06 Recusar temas externos e evitar alucinações | C1, C2 | | ⬜ |
| US-07 Ser avisado de salas com muita afluência | C1, C2 | | ⬜ |
| US-08 Usar a app com leitor de ecrã e alto contraste | C1, C2 | | ⬜ |

## 4. Rastreabilidade com a arquitetura (M2)

| Artefacto | Ficheiro | Requisitos que sustenta |
|---|---|---|
| Diagrama de classes UML | `docs/diagrama_classes.puml` | RF-01 a RF-08 (Módulos A e B), padrões Strategy e Factory |
| Diagrama de sequência: gerar roteiro | AJUSTAR com o caminho final | RF-01 a RF-04 |
| Diagrama de sequência: pergunta ao assistente de IA | AJUSTAR com o caminho final | RF-09 a RF-12 |
| ADR-01: arquitetura em camadas REST | AJUSTAR com o caminho final | RNF-05, `GET /health` |
| ADR-02: base de dados local para funcionamento offline | AJUSTAR com o caminho final | RNF-02 |
| ADR-03: stack Python/FastAPI | AJUSTAR com o caminho final | Todos os módulos, RNF-01, RNF-03 |

## 5. Requisitos sem User Story neste momento

| Requisito | Tipo | Motivo | Plano |
|---|---|---|---|
| RNF-01: ecrã principal < 1,5 s (4G/Wi-Fi) e < 2,5 s (offline) | RNF | Sem cenário BDD próprio; falta medir | Medir no M4 com logs de tempo de resposta |
| RNF-02: fidelidade factual do assistente ≥ 98% | RNF | Exige um conjunto de teste validado pelo curador | Definir o método de medição no M5 |
| Roteiros temáticos e por perfil | RF | Fora do âmbito mínimo | Backlog |
| Botões de navegação ≥ 48x48 dp | RNF (Usabilidade) | Depende do frontend | Critério transversal (US-08) |
| Comunicações com HTTPS/TLS 1.3 | RNF (Segurança) | Depende do ambiente de produção | M5 (auditoria) |
| Compatibilidade Android 10+ / iOS 15+ | RNF (Portabilidade) | Depende do frontend | Restrição técnica |

## 6. Visão geral por EPIC

| EPIC | User Stories | Estado |
|---|---|---|
| EPIC-01 Roteiros Inteligentes (#1) | US-01 (#4), US-02 (#5) | Em curso (US-01 implementada) |
| EPIC-02 Gamificação & QR Codes (#2) | US-03 (#6), US-04 (#7) | Implementada |
| EPIC-03 Assistente IA / RAG (#3) | US-05 (#8), US-06 (#9) | Backlog |
| EPIC-04 Fluxo e Acessibilidade (#a criar) | US-07, US-08 | Backlog |
