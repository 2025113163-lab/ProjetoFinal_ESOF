[![CI - MNSR Digital](https://github.com/2025113163-lab/ProjetoFinal_ESOF/actions/workflows/ci.yml/badge.svg)](https://github.com/2025113163-lab/ProjetoFinal_ESOF/actions/workflows/ci.yml)

# MNSR Digital

Aplicação móvel interativa para o **Museu Nacional Soares dos Reis (Porto)**, desenvolvida no âmbito da unidade curricular de Engenharia de Software (Licenciatura em Engenharia Informática, UFP).

**Membros da Equipa**
Robi Henriquez 2025101373 
Pedro Paiva 2025118433
Luis Santos 2025111261
Rodrigo Pereira 2025113163


**Marco atual:** M2: Modelação UML e Arquitetura

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

## Âmbito do Marco M1: EPICs e User Stories

| EPIC | User Story | Descrição |
|---|---|---|
| **EPIC-01** Roteiros Inteligentes (#1) | US-01 (#4) | Gerar roteiro por tempo disponível |
| | US-02 (#5) | Consultar conteúdo de uma obra |
| **EPIC-02** Gamificação & QR Codes (#2) | US-03 (#6) | Desbloquear pista por QR Code |
| | US-04 (#7) | Caça ao tesouro em modo anónimo |
| **EPIC-03** Assistente IA / RAG (#3) | US-05 (#8) | Perguntar ao assistente sobre uma obra |
| | US-06 (#9) | Recusar temas externos e evitar alucinações |

Cada User Story segue a estrutura *Como… quero… para que…*, os 3 Cs (Card, Conversation, Confirmation) e tem pelo menos 2 cenários de aceitação em formato BDD (Dado/Quando/Então).

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

## Organização do trabalho

- **Quadro Kanban:** Backlog → Ready for Sprint → In Progress → In Review → Done.
- **Labels:** `epic`, `user-story`, `bug`, `documentation`, `frontend`, `backend`, `ai-rag`.
- **Milestone:** M1.
- **Commits:** mensagens convencionais (por exemplo, `docs: adicionar visão do produto no README`).
