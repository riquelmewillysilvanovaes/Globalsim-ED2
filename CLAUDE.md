# CLAUDE.md — GlobalSIM EDII

Guia para o Claude Code trabalhar neste repositório. O enunciado completo está em `atividade.md` — **leia-o antes de qualquer tarefa nova**.

## Visão geral

Aplicação Web em **Python + Flask** (trabalho de Estruturas de Dados II, UNEB) que gerencia uma operadora fictícia de eSIM. O objetivo avaliado **não é o site**, e sim demonstrar três estruturas de dados implementadas à mão e integradas:

| Etapa | Estrutura | Domínio | Prazo |
|---|---|---|---|
| 1 | Tabela Hash | Países / cobertura | **20/10/2026** |
| 2 | Árvore B | Clientes / eSIMs (~1.000 registros) | 24/11/2026 |
| 3 | Grafo ponderado (BFS, DFS, Dijkstra) | Rede / rotas de menor latência | 01/12/2026 |

As etapas são incrementais: nunca quebre funcionalidades de uma etapa anterior.

## Regras inegociáveis (vêm do enunciado — violar = perder nota)

1. **Estruturas implementadas do zero.** Proibido usar `dict`, `list`, `set`, `bisect`, `sortedcontainers`, `networkx` ou qualquer biblioteca como *mecanismo principal* de busca/armazenamento da estrutura exigida.
   - `list` é permitida **internamente** (ex.: vetor de buckets da hash, vetor de chaves de um nó da Árvore B, lista de adjacência).
   - A busca de cliente **tem que** passar pela Árvore B; a busca de país **tem que** passar pela Tabela Hash. Nunca faça `for c in clientes_json` ou `paises_dict[codigo]` numa rota.
2. **Lógica das estruturas separada das rotas.** `estruturas/*.py` não importa Flask. Rotas só chamam métodos das estruturas/serviços.
3. **Rotas que alteram dados usam POST** e seguem **Post/Redirect/Get** (`redirect(url_for(...))` após o POST, com `flash` para feedback).
4. **Persistência em JSON** apenas como fonte de carga/salvamento: JSON → estrutura em memória → operações → estrutura → JSON. Salvar após cada operação que altera dados.
5. **Interface com HTML + Jinja** (`templates/`, herança de `base.html`). Bootstrap via CDN é permitido.
6. **Instrumentação obrigatória**: cada estrutura expõe métricas observáveis na interface (ver abaixo). É critério de avaliação.
7. Todo integrante precisa conseguir explicar o código: **prefira clareza a esperteza**. Nada de one-liners obscuros nas estruturas; comente as decisões não óbvias (função de hash, split da Árvore B, relaxamento no Dijkstra).

## Estrutura do projeto

```
globalsim/
├── app.py                  # cria o app, carrega estruturas, registra rotas
├── config.py               # caminhos dos JSON, grau da Árvore B, capacidade inicial da hash
├── estruturas/
│   ├── tabela_hash.py      # TabelaHash
│   ├── arvore_b.py         # ArvoreB, NoB
│   ├── grafo.py            # Grafo (BFS, DFS, Dijkstra)
│   └── heap_min.py         # HeapMin próprio, usado pelo Dijkstra (Etapa 3)
├── servicos/
│   ├── persistencia.py     # carregar/salvar JSON (escrita atômica: tmp + os.replace)
│   └── consulta.py         # consulta integrada (Etapas 2 e 3) + diferencial
├── scripts/
│   └── gerar_clientes.py   # gera ~1.000 clientes com seed fixa
├── arquivos/
│   ├── paises.json
│   ├── clientes.json
│   ├── pacotes.json
│   └── rede.json
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── paises.html  pais_form.html  cobertura.html
│   ├── clientes.html  cliente_form.html
│   ├── rede.html  consulta.html
│   └── instrumentacao.html
├── static/css/
├── tests/                  # pytest, um arquivo por estrutura
├── requirements.txt        # flask, pytest (Faker opcional para o gerador)
└── README.md               # relatório exigido pela professora
```

## Convenções

- Código, nomes e comentários em **português** (o enunciado e a banca são em português). Sem acentos em identificadores.
- Type hints e docstrings curtas nos métodos públicos das estruturas.
- Validação de formulário nas rotas (código de país com 2 letras maiúsculas, ID inteiro, pacote existente); erros via `flash`.
- Normalize códigos de país com `.strip().upper()` antes de qualquer operação.
- Sem banco de dados, sem ORM, sem SPA/JS framework.

## Comandos

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug        # servidor de desenvolvimento
pytest -q                           # testes das estruturas
python scripts/gerar_clientes.py    # (re)gera arquivos/clientes.json
```

Antes de declarar uma tarefa concluída: rode `pytest -q` e suba o servidor para conferir as páginas afetadas.

---

## Etapa 1 — Tabela Hash (prazo 20/10/2026)

### `TabelaHash`
- Resolução de colisões por **encadeamento separado** (cada bucket é uma lista de pares `[chave, valor]`) — mais fácil de explicar e de visualizar. Endereçamento aberto é alternativa aceitável; se trocar, documente no README.
- Função de hash **própria** (não usar `hash()` do Python, que é randomizado entre execuções). Sugestão: polinomial sobre `ord()` dos caracteres, `h = (h * 31 + ord(c)) % capacidade`.
- Capacidade inicial pequena e prima (ex.: 7) para que colisões e redimensionamento apareçam com os 8 países.
- **Rehash** quando fator de carga > 0,75, dobrando para o próximo primo.
- API: `inserir(chave, valor)`, `buscar(chave)`, `atualizar(chave, valor)`, `remover(chave)`, `itens()`, `__len__`, `__contains__`.
- `inserir` com chave existente deve falhar (cadastro duplicado) — `atualizar` é a operação de alteração.

### Instrumentação mínima
Exponha via `estatisticas()`: capacidade, nº de elementos, fator de carga, total de colisões, maior bucket, nº de rehashes, comparações da última busca, e um "mapa" dos buckets (índice → chaves) para a página `/instrumentacao`.

### Rotas
| Método | Rota | Função |
|---|---|---|
| GET | `/` | página inicial |
| GET | `/paises` | listagem |
| GET/POST | `/paises/novo` | cadastro |
| GET/POST | `/paises/<codigo>/editar` | alteração |
| POST | `/paises/<codigo>/remover` | remoção |
| GET | `/cobertura?codigo=IT` | consulta de cobertura (mostra "COBERTURA DISPONÍVEL" ou "não atendido") |
| GET | `/instrumentacao` | métricas da hash (depois, das outras estruturas também) |

### Dados
`arquivos/paises.json` com os 8 países do enunciado (BR, PT, ES, FR, IT, US, CA, JP), campos `codigo, pais, regiao, operadora, tecnologia`.

### Entregáveis extras
- README inicial com equipe, como executar, descrição da hash.
- **Descrição inicial do diferencial** no README (ver seção Diferencial).

---

## Etapa 2 — Árvore B (prazo 24/11/2026)

### `ArvoreB`
- Implementação clássica (Cormen) com **grau mínimo `t` configurável** (padrão `t = 3`). Cada nó guarda até `2t−1` chaves; os valores (dicionário do cliente) acompanham as chaves.
- Operações: `inserir(id, cliente)` com **split proativo** na descida, `buscar(id)`, `atualizar(id, dados)`, `percorrer_em_ordem()` (listagem ordenada), `altura()`. Remoção é opcional (não exigida); se implementar, testar os casos de merge/empréstimo.
- IDs duplicados são rejeitados.

### Instrumentação
Contadores: nº de splits, altura, nº de nós, nós visitados e comparações na última busca, ocupação média dos nós. Visualização da árvore por níveis em `/instrumentacao` (ao menos os 2–3 primeiros níveis).

### Dados e rotas
- `scripts/gerar_clientes.py`: ~1.000 clientes, `random.seed(42)`, IDs únicos aleatórios (não sequenciais — para exercitar splits variados), `esim` no formato `ESIM-NNNNN`, `pacote` em {101,102,201,202,301}, `status` em {ativo, inativo, suspenso}.
- `arquivos/pacotes.json` com a tabela de pacotes do enunciado (pacotes ficam em lista/JSON; não são uma 4ª estrutura).
- Rotas: `/clientes` (listagem paginada em ordem via percurso da árvore), `/clientes/novo`, `/clientes/<id>`, `/clientes/<id>/editar`, `/clientes/<id>/esim` (associar eSIM e pacote) — alterações via POST.
- **Consulta integrada** `/consulta` (cliente + destino): busca na Árvore B, depois na Tabela Hash, exibindo os passos como no enunciado.

---

## Etapa 3 — Grafo (prazo 01/12/2026)

### `Grafo`
- Ponderado, **não direcionado**, por **lista de adjacência** implementada na classe (vértices indexados pelo código do país).
- `bfs(origem)`, `dfs(origem)` (iterativo ou recursivo — retornar a ordem de visita), `dijkstra(origem, destino)` → `(caminho, custo)`.
- Dijkstra usa a `HeapMin` própria de `estruturas/heap_min.py` (evita questionamento sobre `heapq`).
- Vértices do grafo devem existir na Tabela Hash; ao remover um país, remover também suas arestas (coerência entre estruturas é critério).

### `arquivos/rede.json` (rede do enunciado)
BR–US 80, BR–PT 120, PT–ES 30, PT–FR 40, FR–IT 25, US–CA 20, CA–JP 110.
**Teste de aceitação:** `dijkstra("BR", "IT")` → `BR → PT → FR → IT`, **185 ms**.

### Consulta final integrada (`/consulta`)
1. Árvore B: cliente → nome, eSIM, status, pacote.
2. Tabela Hash: destino atendido? tecnologia.
3. Pacotes: dados e validade.
4. Grafo: origem (padrão BR) e destino.
5. Dijkstra: melhor rota e latência.
6. Exibir no formato do enunciado. Tratar: cliente inexistente, destino não atendido, destino inalcançável, cliente inativo.

### Visualização do grafo (`/rede`)
SVG gerado no template Jinja com posições fixas por país, ou vis-network via CDN. Destacar a rota do Dijkstra e a ordem de visita do BFS/DFS. Rotas para adicionar/remover conexões (POST).

---

## Diferencial (definido): Simulação de falhas de conexões e recálculo automático das rotas

**Problema resolvido:** numa rede real, enlaces caem. O GlobalSIM deve continuar indicando ao cliente a melhor rota disponível, ou avisar que o destino ficou inalcançável, sem intervenção manual.

### Modelo
- Cada aresta tem estado `ativa: true|false`, persistido em `arquivos/rede.json`:
  ```json
  {"origem": "PT", "destino": "FR", "latencia": 40, "ativa": true}
  ```
- Opcional: falha de **vértice** (queda de um país inteiro), que equivale a desativar todas as arestas dele sem removê-las.
- Falhar não é remover: a aresta continua no grafo e pode ser restaurada.

### API em `Grafo` (sem Flask)
- `falhar_conexao(a, b)`, `restaurar_conexao(a, b)`, `restaurar_todas()`.
- `falhar_aleatoria(n, seed=None)`: derruba `n` conexões ativas sorteadas (modo demonstração).
- BFS, DFS e Dijkstra **ignoram arestas inativas**. Use um único iterador `vizinhos_ativos(v)` para que todos os algoritmos compartilhem a regra.
- `esta_conectado(a, b)` via BFS: decide rapidamente se ainda existe caminho antes de rodar o Dijkstra.

### Recálculo automático (`servicos/consulta.py`)
- Toda falha ou restauração dispara o recálculo das rotas monitoradas. O conjunto mínimo é a rota da última consulta. O ideal são as rotas BR → cada destino atendido.
- Para cada rota, retornar um comparativo:
  `rota_anterior`, `latencia_anterior`, `rota_nova`, `latencia_nova`, `delta_ms`, `status ∈ {inalterada, desviada, inalcancavel}`.
- Se o destino ficar inalcançável, mostrar o **componente alcançável** a partir da origem (resultado da BFS).
- Manter um **histórico de eventos** em memória (lista interna do serviço): horário, conexão afetada, rotas impactadas. Salvar em JSON é opcional.

### Integração
- **Consulta final (`/consulta`)**: usa sempre o estado atual da rede. Se a rota ótima original estiver comprometida, exibe "Rota alternativa (falha em PT–FR)" com a latência extra, ou "Destino temporariamente inalcançável".
- **Tabela Hash**: não se pode falhar uma conexão de um país não atendido. Validar pela hash.
- **Árvore B**: opcional. Listar quantos clientes têm pacote que cobre um destino afetado. Isso exige percorrer a árvore e deve ser feito pelo percurso dela, nunca pelo JSON.

### Interface
- Em `/rede`: botões POST "Falhar" e "Restaurar" por conexão, "Falha aleatória" e "Restaurar tudo". Seguir o padrão PRG.
- Na visualização: arestas inativas tracejadas ou em vermelho, rota atual destacada.
- Painel "Impacto da última falha" com a tabela antes/depois e o histórico de eventos.

### Instrumentação
Mostrar o total de falhas e restaurações, o nº de recálculos, quantas rotas foram desviadas ou ficaram inalcançáveis, e os vértices relaxados e o tempo do último Dijkstra.

### Extensão opcional (enriquece a apresentação)
**Conexões críticas (pontes)** detectadas por DFS (algoritmo de Tarjan, `low[]`/`disc[]`). Indicam quais enlaces, se caírem, desconectam a rede. Na rede do enunciado (uma árvore), todas são pontes. Adicionar arestas redundantes ao `rede.json`, como ES–FR e US–PT, para que existam rotas alternativas e o recálculo fique visível na demonstração.

### Cenário de demonstração (usar nos testes)
1. Rede normal: `dijkstra("BR","IT")` → BR → PT → FR → IT, 185 ms.
2. Falhar PT–FR. Com a aresta redundante ES–FR, a rota passa a ser BR → PT → ES → FR → IT. Sem redundância, IT fica inalcançável.
3. Restaurar PT–FR: a rota volta a 185 ms.

### Entrega da Etapa 1
O README deve trazer a **descrição inicial** desse diferencial: problema, algoritmos (BFS para conectividade, Dijkstra sobre arestas ativas), e integração com a hash e a consulta final. A implementação começa na Etapa 3. Na Etapa 2 basta, se der tempo, preparar o campo `ativa` no `rede.json`.

Registrar no README final: problema resolvido, algoritmo, decisões de implementação e integração.

## Testes

Um arquivo por estrutura em `tests/`. Cobrir no mínimo:
- Hash: inserir/buscar/atualizar/remover, duplicata, colisão forçada, rehash preserva todos os itens.
- Árvore B: inserir 1.000 chaves aleatórias e buscar todas; percurso em ordem sai ordenado; todas as folhas na mesma altura; nenhum nó viola `t−1 ≤ chaves ≤ 2t−1` (exceto a raiz).
- Grafo: BFS/DFS a partir de BR; Dijkstra BR→IT = 185; destino inalcançável retorna `None`.

## O que NÃO fazer

- Não substituir estruturas por `dict`/biblioteca "só para facilitar".
- Não fazer busca linear no JSON carregado.
- Não usar GET para operações que alteram dados.
- Não colocar lógica de estrutura dentro de `app.py`.
- Não apagar ou reescrever funcionalidades de etapas anteriores ao avançar.
