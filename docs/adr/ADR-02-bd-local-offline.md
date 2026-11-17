# ADR-02: Armazenamento local para funcionamento offline

- **Estado:** Proposta
- **Data:** 2026-11-17
- **Marco:** M2

## Contexto

O RNF-02 exige que a app mantenha acesso a roteiros, mapas e leitura de QR Codes mesmo em zonas sem rede, devido às paredes espessas de pedra do Palácio dos Carrancas. Hoje o acervo existe em `data/museu.json` no servidor e o progresso da caça ao tesouro é guardado em memória no servidor (`_SESSOES`). Sem cópia local no cliente, a app deixa de funcionar quando a rede falha. O RNF-03 impede guardar dados pessoais identificáveis de menores.

## Decisão Considerada

Guardar no dispositivo uma **cópia local do acervo e dos últimos roteiros** em **IndexedDB**, gerida pela PWA, com **Service Worker** para a cache dos ficheiros estáticos.

- Na primeira ligação (ou quando há rede), a app descarrega o acervo (obras, salas, códigos QR) e guarda-o no IndexedDB.
- Roteiros gerados são guardados localmente; offline, a app mostra o último roteiro ou calcula-o a partir do acervo local.
- A validação de um QR Code offline é feita contra a tabela local `codigo_qr -> obra`. O progresso fica em fila local e é sincronizado com a API quando há rede.
- Apenas se guardam identificadores de sessão anónimos (sem nome, idade ou localização contínua), em linha com o RNF-03.

Alternativas consideradas:

1. **SQLite (React Native / Expo)**: tecnicamente adequada, mas só faz sentido se o cliente for nativo. Escolhida **apenas se** a equipa optar por React Native em vez de PWA.
2. **localStorage**: rejeitada. Limite de cerca de 5 MB, API síncrona e só strings.
3. **Sem armazenamento local (tudo online)**: rejeitada. Não cumpre o RNF-02.
4. **Base de dados no servidor com réplica no cliente (por exemplo CouchDB/PouchDB)**: rejeitada. Complexidade desproporcionada para um acervo de poucas dezenas de obras.

## Consequências

- (+) Cumpre o RNF-02 sem depender da rede dentro do museu.
- (+) Respostas locais rápidas, o que ajuda o RNF-01 (tempo de resposta).
- (+) API do servidor continua simples e sem estado do cliente.
- (-) Há duas fontes de verdade (servidor e cache local): é preciso versionar o acervo (por exemplo `versao` no JSON) e definir quando se invalida a cache.
- (-) A lógica de geração de roteiros pode ter de existir também no cliente (TypeScript) para funcionar offline; tem de se manter coerente com as estratégias do servidor.
- (-) A sincronização do progresso do Módulo B exige tratamento de conflitos (QR repetido lido offline em dois dispositivos da mesma sessão).
- Pressuposto: o cliente é uma **PWA**. Se a equipa escolher React Native, substituir IndexedDB por SQLite e atualizar este ADR.
