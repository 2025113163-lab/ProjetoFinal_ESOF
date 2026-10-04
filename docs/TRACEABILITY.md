# Matriz de Rastreabilidade — Marco M1

## 1. Requisitos cobertos por User Stories

| Requisito | Tipo | Origem | EPIC | User Story | Issue | Cenários BDD |
|---|---|---|---|---|---|---|
| Gerar roteiro pelo tempo disponível (30/60/90 min) | RF | Visão do produto | EPIC-01 (#1) | US-01 | #4 | C1 |
| RNF-01: Desempenho (carregamento a partir da cache < 1,0 s) | RNF | Exercício 2.1 | EPIC-01 (#1) | US-01 | #4 | C2 (parcial) |
| Funcionamento offline na galeria | RNF (Fiabilidade) | Exercício 2.2 | EPIC-01 (#1) | US-01, US-02 | #4, #5 | US-01 C2; US-02 C2 |
| RF-03: Conteúdo da obra "O Desterro" | RF | Exercício 2.1 | EPIC-01 (#1) | US-02 | #5 | C1, C2 |
| Ler QR Codes para desbloquear pistas | RF | Exercício 2.2 | EPIC-02 (#2) | US-03 | #6 | C1, C2 |
| RNF-04: Privacidade/RGPD (sem PII, sem geolocalização contínua) | RNF | Exercício 2.1 | EPIC-02 (#2) | US-04 | #7 | C1, C2 |
| Guia conversacional de IA sobre as obras | RF | Visão do produto | EPIC-03 (#3) | US-05 | #8 | C1, C2 |
| RNF-02: Fiabilidade da IA (só acervo do MNSR, recusa temas externos) | RNF | Exercício 2.1 | EPIC-03 (#3) | US-06 | #9 | C1, C2 |

## 2. Requisitos identificados sem User Story no M1

| Requisito | Tipo | Motivo | Plano |
|---|---|---|---|
| RNF-01: ecrã principal < 1,5 s (4G/Wi-Fi) e < 2,5 s (offline) | RNF | Sem cenário BDD próprio | Candidato ao M2 |
| RNF-02: fidelidade factual >= 98% | RNF | Exige conjunto de teste validado pelo curador | Definir método de medição no M2 |
| Roteiros temáticos e por perfil | RF | Fora do âmbito mínimo do M1 | Backlog |
| Gestão do fluxo nas salas | RF | Referido na Visão; fora do âmbito do M1 | Backlog |
| Progresso e recompensas virtuais | RF | Parte da EPIC-02; adiado | Backlog |
| Botões de navegação >= 48x48 dp | RNF (Usabilidade) | Exercício 2.2 | Critério transversal no M2 |
| Comunicações com HTTPS/TLS 1.3 | RNF (Segurança) | Exercício 2.2 | Critério transversal no M2 |
| Sincronização de roteiros < 1,0 s após o arranque | RNF (Desempenho) | Exercício 2.2 | Backlog |
| Compatibilidade Android 10+ / iOS 15+ | RNF (Portabilidade) | Exercício 2.2 | Restrição técnica no M2 |

## 3. Visão geral por EPIC

| EPIC | User Stories | Estado |
|---|---|---|
| EPIC-01 Roteiros Inteligentes (#1) | US-01 (#4), US-02 (#5) | Backlog |
| EPIC-02 Gamificação & QR Codes (#2) | US-03 (#6), US-04 (#7) | Backlog |
| EPIC-03 Assistente IA / RAG (#3) | US-05 (#8), US-06 (#9) | Backlog |
