# Matriz de Rastreabilidade — Marco M2

Liga cada requisito (RF/RNF) à **User Story**, ao **desenho** (diagramas/ADRs) e aos **testes automáticos**.

- Os IDs **RF-xx / RNF-xx** seguem o enunciado (Módulo A = RF-01–04, B = RF-05–08, C = RF-09–12, D = RF-13–15; RNF-01 a RNF-05). Os rótulos usados no M1 (que numeravam os RNF de outra forma) ficam na coluna *Rótulo M1* para manter o histórico.
- Estado: ✅ coberto por teste automático · 🟡 coberto em parte · ❌ sem teste (planeado).
- Testes em `test/`; formato `ficheiro::Classe::teste`.

## 1. Requisitos funcionais → User Story → testes

| Requisito | Descrição | EPIC | User Story (issue) | BDD | Desenho | Testes automáticos | Estado |
|---|---|---|---|---|---|---|---|
| RF-01–04 (Mód. A) | Gerar roteiro pelo tempo disponível (30/60/90 min) e por interesse | EPIC-01 (#1) | US-01 (#4) | C1 | [Seq. roteiro](sequencia_roteiro.png) · ADR-01 | `test_roteiro.py::TestRoteiro::test_tempo_e_interesse_escultura` · `::test_tempo_curto_limite` · `::test_interesse_inexistente_devolve_vazio` · `::test_endpoint_roteiros` | ✅ |
| RF-01–04 (Mód. A) | Alternar algoritmo de rota (mais curta / menos crowded / familiar) — **Strategy** | EPIC-01 (#1) | US-01 (#4) | C1 | [Diagrama de classes](diagrama_classes.puml) | `test_roteiro.py::TestRoteiro::test_estrategias_roteiro` · `test_logging.py::test_estrategia_desconhecida_regista_warning` | 🟡 só verifica o limite de tempo e o limite de 8 min da familiar; falta testar a ordem de `RotaMenosCrowded` |
| RF-01–04 (Mód. A) | Consultar conteúdo de uma obra (ex.: "O Desterro") | EPIC-01 (#1) | US-02 (#5) | C1, C2 | — | — | ❌ sem endpoint nem teste |
| RF-05–08 (Mód. B) | Ler QR Code e desbloquear pista (válido, nulo, vazio, corrompido, repetido) | EPIC-02 (#2) | US-03 (#6) | C1, C2 | [Diagrama de classes](diagrama_classes.puml) (`QRCode`, `EstadoQR`) | `test_qr.py::TestQRCode::*` (6) · `test_qr.py::TestEndpointsQR::test_validar_qr_valido` · `::test_validar_qr_nulo` · `::test_validar_qr_vazio` · `::test_validar_qr_corrompido` · `::test_validar_qr_repetido` · `test_qr_refactor.py::TestEstadoQR::*` (3) · `test_qr_integracao.py::TestIntegracaoQRePistas::test_codigo_em_lista_e_corrompido` · `test_logging.py::test_qr_invalido_regista_warning` | ✅ |
| RF-05–08 (Mód. B) | Criar desafio a partir do QR validado, por tipo (pergunta, qr, beacon simulado) — **Factory** | EPIC-02 (#2) | US-03 (#6) | C1 | [Diagrama de classes](diagrama_classes.puml) (`DesafioFactory`, subtipos de `Desafio`) | `test_qr.py::TestDesafioFactory::*` (5) · `test_qr_integracao.py::TestTiposDesafio::*` (7) · `test_qr_integracao.py::TestIntegracaoQRePistas::test_validar_com_tipo_qr` · `::test_tipo_invalido_nao_consome_o_qr` | ✅ |
| RF-05–08 (Mód. B) | Responder a um desafio (`POST /desafios/responder`) | EPIC-02 (#2) | US-03 (#6) | C1 | [Diagrama de classes](diagrama_classes.puml) | `test_qr_integracao.py::TestIntegracaoQRePistas::test_responder_certo` · `::test_responder_errado_ou_nulo` · `::test_responder_sem_desbloquear_da_404` · `::test_resolver_duas_vezes_conta_uma_vez` | ✅ |
| RF-05–08 (Mód. B) | Listar pistas desbloqueadas e progresso | EPIC-02 (#2) | US-03 (#6), US-04 (#7) | C1 | — | `test_qr.py::TestEndpointsQR::test_pistas_vazias` · `::test_pistas_apos_validar` · `test_qr_integracao.py::TestIntegracaoQRePistas::test_pistas_mostra_tipo_e_resolvido` · `test_qr_refactor.py::TestPistasEficiencia::test_pistas_le_o_acervo_uma_unica_vez` | ✅ |
| RF-05–08 (Mód. B) | Medalhas digitais e descontos na loja/cafetaria (`Recompensa`) | EPIC-02 (#2) | sem US própria (ligar a US-03/US-04 ou criar) | — | [Diagrama de classes](diagrama_classes.puml) (`Recompensa`) | `test_qr_integracao.py::TestRecompensa::*` (3) · `::TestIntegracaoQRePistas::test_medalhas_e_descontos_em_pistas` · `::test_desbloquear_sem_resolver_nao_da_medalha` | 🟡 testado, mas limiares 3/6/10 e descontos 5/10/15% ainda a validar com o PO; sem US formal |
| RF-09–12 (Mód. C) | Perguntar ao assistente de IA sobre uma obra (RAG) | EPIC-03 (#3) | US-05 (#8) | C1, C2 | [Seq. assistente IA](sequencia_assistente_ia.png) | — | ❌ planeado para o M5 |
| RF-09–12 (Mód. C) | Recusar temas fora do acervo e evitar alucinações (*Rótulo M1: "RNF-02 Fiabilidade da IA"*) | EPIC-03 (#3) | US-06 (#9) | C1, C2 | [Seq. assistente IA](sequencia_assistente_ia.png) (ramo `alt`) | — | ❌ planeado para o M5 (testes anti-alucinação) |
| RF-13–15 (Mód. D) | Indicador de afluência por sala e notificação ao atravessar o limiar — **Observer** | — | **US-07 (a criar)** | a escrever | [Diagrama de classes](diagrama_classes.puml) | `test_afluencia.py::TestAfluenciaSala::*` (10) · `test_afluencia.py::TestNotificadorApp::*` (1) | 🟡 lógica coberta; sem endpoint nem ligação a Wi-Fi/Beacons; sem US formal |

## 2. Requisitos não funcionais → User Story → verificação

| Requisito | Métrica (enunciado) | Rótulo M1 | User Story (issue) | Desenho | Verificação | Estado |
|---|---|---|---|---|---|---|
| RNF-01 Desempenho | Roteiros < 1,5 s; IA com 1.º token em < 2,5 s a 200 utilizadores | "RNF-01: cache < 1,0 s" | US-01 (#4), C2 parcial | ADR-02 (respostas locais) · ADR-03 | — (sem teste de carga/tempo) | ❌ medir no M4 |
| RNF-02 Funcionamento offline | Roteiros, mapas e QR sem rede | "Funcionamento offline na galeria" | US-01 (#4) C2, US-02 (#5) C2 | ADR-02 · [Seq. roteiro](sequencia_roteiro.png) (bloco `opt`) | — (cliente ainda não existe) | ❌ |
| RNF-03 RGPD e menores | Sem dados pessoais de menores; segredos fora do cliente | "RNF-04: Privacidade/RGPD" | US-04 (#7) C1, C2 | ADR-02 (apenas sessão anónima) | `test_qr.py::TestEndpointsQR::test_sessoes_independentes` · `::test_pistas_isoladas_por_sessao` · `test_qr_integracao.py::TestIntegracaoQRePistas::test_recompensas_isoladas_por_sessao`; `.env` no `.gitignore` | 🟡 anonimato testado; gestão de segredos/vault por validar no M5 |
| RNF-04 Acessibilidade | WCAG 2.1 AA, toque >= 48x48 px | "Botões >= 48x48 dp" | critério transversal | — | — (cliente ainda não existe) | ❌ |
| RNF-05 Manutenibilidade | Cobertura >= 80%; sem vulnerabilidades High/Critical (SonarQube) | — | transversal | ADR-01 · ADR-03 | `.github/workflows/ci.yml`: `ruff check` + `pytest --cov-fail-under=80` a cada push/PR | 🟡 cobertura e linter no CI; SonarQube ainda não configurado |
| Observabilidade (transversal, M4) | Logging estruturado JSON com `X-Request-ID` | — | transversal | ADR-01 | `test_health.py::test_health_devuelve_ok` · `test_logging.py::*` (2) | 🟡 ID de pedido e avisos de QR/estratégia testados |

## 3. Requisitos do M1 ainda sem User Story

| Requisito | Tipo | Motivo | Plano |
|---|---|---|---|
| Ecrã principal < 1,5 s (4G/Wi-Fi) e < 2,5 s (offline) | RNF (Desempenho) | Sem cenário BDD próprio | Rever com RNF-01 |
| Fidelidade factual da IA >= 98% | RNF | Exige conjunto de teste validado pelo curador | Definir método de medição no M5 |
| Roteiros temáticos e por perfil | RF | Fora do âmbito mínimo | Backlog |
| Gestão do fluxo nas salas | RF | Tem implementação (Observer) mas não US | Criar US-07 |
| Progresso e recompensas virtuais | RF | Implementado (`Recompensa`), mas sem US própria | Ligar a US-03/US-04 ou criar US |
| Comunicações com HTTPS/TLS 1.3 | RNF (Segurança) | Critério transversal | M5 (segurança) |
| Sincronização de roteiros < 1,0 s após o arranque | RNF (Desempenho) | — | Backlog; ver ADR-02 |
| Compatibilidade Android 10+ / iOS 15+ | RNF (Portabilidade) | Restrição técnica | Depende da escolha PWA/nativo (ADR-02) |

## 4. Visão geral por EPIC

| EPIC | User Stories | Implementação |
|---|---|---|
| EPIC-01 Roteiros Inteligentes (#1) | US-01 (#4), US-02 (#5) | US-01 implementada; US-02 por implementar |
| EPIC-02 Gamificação & QR Codes (#2) | US-03 (#6), US-04 (#7) | US-03 implementada (QR, desafios por tipo, respostas, recompensas); US-04 em parte (sessão anónima) |
| EPIC-03 Assistente IA / RAG (#3) | US-05 (#8), US-06 (#9) | Por implementar (M5); desenho no diagrama de sequência |
| Afluência (Módulo D) | US-07 (a criar) | Observer implementado e testado; sem US |
