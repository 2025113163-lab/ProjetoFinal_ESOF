[![CI - MNSR Digital](https://github.com/2025113163-lab/ProjetoFinal_ESOF/actions/workflows/ci.yml/badge.svg)](https://github.com/2025113163-lab/ProjetoFinal_ESOF/actions/workflows/ci.yml)

# MNSR Digital

Aplicação móvel interativa para o **Museu Nacional Soares dos Reis (Porto)**, desenvolvida no âmbito da unidade curricular de Engenharia de Software (Licenciatura em Engenharia Informática, UFP).

**Membros da Equipa**

- Robi Henriquez 2025101373
- Pedro Paiva 2025118433
- Luis Santos 2025111261
- Rodrigo Pereira 2025113163

**Marco atual:** M3 (core funcional) concluído, M2 (UML e ADRs) em fecho e M4 (CI/CD e logging) em curso. Ver [Estado do projeto](#estado-do-projeto).

---

## Visão do Produto

**PARA** os jovens, famílias e turistas culturais que visitam a cidade do Porto,
**QUE** procuram uma experiência museológica dinâmica, personalizada e interativa,
**A APP MNSR DIGITAL** é uma aplicação móvel inteligente e gamificada
**QUE** oferece roteiros personalizados pelo tempo disponível, caça ao tesouro por QR Code e um guia conversacional de IA para responder a dúvidas sobre as obras,
**AO CONTRÁRIO DOS** guias áudio estáticos e brochuras em papel tradicionais,
**O NOSSO PRODUTO** aumenta o envolvimento do visitante, promove o regresso do público local e permite gerir eficientemente o fluxo nas salas do museu.

---

## Contexto e problema

O MNSR, fundado em 1833 e sediado no Palácio dos Carrancas, tem um acervo muito rico de escultura e pintura, mas enfrenta um desafio de atratividade e retenção:

- cerca de **85 000 visitantes/ano**, contra 1 200 000 da Livraria Lello e 500 000 de Serralves;
- **62%** do público são seniores em excursões e apenas **15%** são jovens/estudantes;
- tempo médio de permanência de apenas **42 minutos**.

O objetivo da app é inverter este cenário através de tecnologia móvel interativa.

## Objetivos e indicadores de sucesso

Hipóteses de trabalho da equipa, a validar com o Product Owner:

| Indicador | Situação atual | Meta proposta |
|---|---|---|
| Visitantes jovens/estudantes | 15% | 25% |
| Tempo médio de permanência | 42 min | 55 min |
| Regresso de público local | não medido | a definir após o lançamento |

## Partes interessadas e personas

- **Visitante jovem:** quer uma visita rápida e interativa.
- **Família com crianças:** procura atividades seguras e divertidas (caça ao tesouro).
- **Turista cultural:** tem pouco tempo e quer ver o essencial.
- **Visitante sénior em excursão:** a app deve complementar, e não substituir, a visita guiada.
- **Curador / Product Owner:** valida o conteúdo e as regras de negócio.
- **Gestor do museu:** interessa-lhe gerir o fluxo nas salas.

---

## Âmbito: EPICs e User Stories

| EPIC | User Story | Descrição | Estado |
|---|---|---|---|
| **EPIC-01** Roteiros Inteligentes (#1) | US-01 (#4) | Gerar roteiro por tempo disponível | Implementada |
| | US-02 (#5) | Consultar conteúdo de uma obra | Pendente |
| **EPIC-02** Gamificação & QR Codes (#2) | US-03 (#6) | Desbloquear pista por QR Code | Implementada |
| | US-04 (#7) | Caça ao tesouro em modo anónimo | Implementada |
| **EPIC-03** Assistente IA / RAG (#3) | US-05 (#8) | Perguntar ao assistente sobre uma obra | Pendente |
| | US-06 (#9) | Recusar temas externos e evitar alucinações | Pendente |
| **EPIC-04** Fluxo e Acessibilidade (#45) | US-07 (#46) | Ser avisado de salas com muita afluência | Pendente |
| | US-08 (#47) | Usar a app com leitor de ecrã e alto contraste | Pendente |

Cada User Story segue a estrutura *Como… quero… para que…*, os 3 Cs (Card, Conversation, Confirmation) e tem pelo menos 2 cenários de aceitação em formato BDD (Dado/Quando/Então). A rastreabilidade entre requisitos, User Stories e testes está em [docs/TRACEABILITY.md](docs/TRACEABILITY.md).

---

## Estado do projeto

| Marco | Foco | Estado |
|---|---|---|
| M0 | Arranque e governação de IA | Concluído |
| M1 | Requisitos e agilidade | Concluído |
| M2 | Modelação UML e arquitetura | Concluído |
| M3 | Core funcional (Módulos A e B), testes | Concluído (54 testes, cobertura de 96%) |
| M4 | CI/CD e logging | CI e logging JSON feitos; falta o diagnóstico de bugs documentado |
| M5 | Segurança, padrões GoF e RAG | Pendente (Strategy e Factory feitos; Observer e RAG por fazer) |
| M6 | Release Candidate e defesa | Pendente |

---

## Arquitetura e tecnologias

- **Backend:** Python 3.12+ com FastAPI, em arquitetura em camadas (API REST, lógica de negócio e dados).
- **Dados:** acervo em `data/museu.json` (15 obras, com sala, tema, tempo de visita e código QR). O progresso da caça ao tesouro é guardado em memória por sessão anónima.
- **Testes:** pytest e pytest-cov.
- **Qualidade:** Ruff (linter) e Quality Gate de cobertura (80%) no CI.
- **Logging:** registos em JSON com `request_id` por pedido, propagado em todos os logs do pedido.

### Padrões de desenho aplicados

| Padrão | Onde | Para quê |
|---|---|---|
| **Strategy** | `RoteiroStrategy` com `RotaMaisCurta`, `RotaMenosCrowded` e `RotaFamiliar` | Alternar o algoritmo de cálculo do roteiro |
| **Factory Method** | `DesafioFactory` com `DesafioPergunta`, `DesafioQR` e `DesafioBeacon` | Criar o tipo de desafio da caça ao tesouro |
| **Observer** | Previsto para `AfluenciaSala` e `VisitanteApp` | Notificar a app sobre a afluência nas salas (por implementar) |

### API

| Método e caminho | Descrição |
|---|---|
| `GET /health` | Verificação de estado |
| `GET /roteiros?tempo=60&interesse=Escultura&estrategia=curta` | Gera o roteiro. `estrategia`: `curta`, `menos_crowded` ou `familiar` |
| `POST /qr/validar` | Valida um QR Code (`sessao`, `codigo`, `tipo`) e desbloqueia o desafio da obra |
| `POST /desafios/responder` | Verifica a resposta a um desafio (`sessao`, `codigo`, `resposta`) e devolve a recompensa |
| `GET /pistas?sessao=anonima` | Lista as pistas desbloqueadas e a recompensa atual |

A documentação interativa fica disponível em `/docs` com o servidor a correr.

---

## Como executar

Requisitos: Python 3.12 ou superior e Git.

```powershell
# 1. Clonar o repositório
git clone https://github.com/2025113163-lab/ProjetoFinal_ESOF.git
cd ProjetoFinal_ESOF

# 2. Criar e ativar o ambiente virtual (Windows)
python -m venv .venv
.venv\Scripts\Activate.ps1
# Mac/Linux: source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Arrancar o servidor
uvicorn src.main:app --reload
```

Abrir `http://127.0.0.1:8000/health` (deve devolver `{"status": "ok"}`) e `http://127.0.0.1:8000/docs` para experimentar a API.

### Testes e qualidade

```powershell
ruff check src/ test/
python -m pytest --cov=src --cov-report=term-missing
```

O CI executa exatamente estes dois comandos em cada Pull Request e falha se a cobertura descer de 80%.

---

## Estrutura do repositório

```
.
├── .github/workflows/ci.yml     # Pipeline de CI (Ruff + pytest + quality gate)
├── data/museu.json              # Acervo do museu (15 obras)
├── docs/
│   ├── AI_LOG.md                # Registo de utilização de IA (proveniência)
│   ├── TRACEABILITY.md          # Matriz de rastreabilidade
│   ├── diagrama_classes.puml    # Diagrama de classes UML (PlantUML)
│   ├── sequencia_asistente_ia.png
│   ├── sequencia_roteiro.png
│   └── adr/         
│      ├── ADR-01-arquitetura-em-camadas-rest.md     
│      ├── ADR-02-bd-local-offline.md
│      ├── ADR-03-stack-python-fastapi.md        
├── src/main.py                  # API, domínio, padrões e logging
├── test/                        # Testes automáticos
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Como instalar, executar e testar

Requisitos: Python 3.12. Todos os comandos correm na raiz do repositório.

```bash
# Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar a API (documentação interativa em http://127.0.0.1:8000/docs)
uvicorn src.main:app --reload

# Testes com cobertura (o CI exige >= 80%)
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Linter
ruff check src/ test/
```

---

## Documentação

- Product Backlog: [MNSR Digital — Product Backlog](<https://github.com/users/2025113163-lab/projects/1/views/1>)
- Matriz de rastreabilidade: [docs/TRACEABILITY.md](docs/TRACEABILITY.md)
- Decisões de arquitetura: [ADR-01](docs/adr/ADR-01-arquitetura-em-camadas-rest.md) · [ADR-02](docs/adr/ADR-02-bd-local-offline.md) · [ADR-03](docs/adr/ADR-03-stack-python-fastapi.md)
- Diagrama de classes: [docs/diagrama_classes.puml](docs/diagrama_classes.puml)
- Diagramas de sequência: [Gerar roteiro](docs/sequencia_roteiro.png) · [Pergunta ao assistente de IA](docs/sequencia_assistente_ia.png)
- Registo de IA: [docs/AI_LOG.md](docs/AI_LOG.md)

## Organização do trabalho

- **Quadro Kanban:** Backlog → Ready for Sprint → In Progress → In Review → Done.
- **Labels:** `epic`, `user-story`, `bug`, `documentation`, `frontend`, `backend`, `ai-rag`.
- **Milestones:** M1 a M6.
- **Ramos:** um ramo por tarefa (`feature/...`, `fix/...`, `docs/...`, `chore/...`), sempre a partir de uma `main` atualizada. Não se faz push direto para a `main`.
- **Pull Requests:** revistas por pelo menos uma pessoa diferente do autor, com o CI a verde antes do merge.
- **Commits:** mensagens convencionais (`feat:`, `fix:`, `docs:`, `test:`, `chore:`), por exemplo `docs: adicionar visão do produto no README`.
- **Definition of Done:** código revisto em PR, testes a passar, cobertura ≥ 80%, documentação atualizada e entrada no `docs/AI_LOG.md` se foi usada IA.

## Governação de IA generativa

Usamos IA generativa de forma transparente e responsável. Todas as interações relevantes ficam registadas em [docs/AI_LOG.md](docs/AI_LOG.md), com o prompt, o resultado e a validação humana feita. A equipa é responsável por todo o código, teste e documento submetido.
