# Trabalho Prático — GlobalSIM EDII

**Disciplina:** Estruturas de Dados II
**Curso:** Sistemas de Informação – DCET/1 – UNEB
**Professora:** Maria Inés Restovic

> Serviço Internacional de Internet por eSIM

---

## Contexto e objetivo

A GlobalSIM é uma empresa fictícia que oferece acesso à Internet móvel por eSIM para viajantes internacionais. O trabalho consiste no desenvolvimento incremental de uma aplicação Web em **Python/Flask** para administrar países atendidos, clientes e eSIMs, pacotes de serviço e uma rede internacional simulada.

O objetivo principal é aplicar, integrar e analisar estruturas de dados estudadas em Estruturas de Dados II. A interface Web deverá permitir que o funcionamento das estruturas seja observado por meio de operações reais do sistema.

## Organização do trabalho

| Etapa | Conteúdo principal | Aplicação no GlobalSIM |
|---|---|---|
| 1 | Tabela Hash + Web/Flask | Países atendidos e consulta de cobertura |
| 2 | Árvore B | Clientes, eSIMs e grande volume de registros |
| 3 | Grafos | Rede internacional e rotas de menor latência |

As etapas são incrementais: a Etapa 2 deverá preservar e integrar a Etapa 1; a Etapa 3 deverá preservar e integrar as duas etapas anteriores.

## Diferencial obrigatório da equipe

Além dos requisitos comuns, cada equipe deverá propor e implementar pelo menos um diferencial próprio para o GlobalSIM. O diferencial deverá acrescentar conteúdo funcional ou algorítmico relevante e deverá ser submetido à aprovação da professora.

Mudanças exclusivamente estéticas, alteração de cores, logotipo, tema visual ou reorganização de telas **não** serão consideradas diferencial.

Exemplos de diferenciais possíveis:

- Comparação de diferentes graus da Árvore B e seus efeitos sobre altura, divisões e buscas.
- Planejamento de viagem com múltiplos destinos.
- Simulação de falhas de conexões e recálculo automático das rotas.
- Roteamento por diferentes critérios, como latência, custo ou outro peso definido pela equipe.
- Identificação de países estratégicos da rede por métricas de conectividade.
- Recomendação de pacote de dados a partir do roteiro de viagem.
- Outro diferencial proposto pela equipe e aprovado pelo professor.

Na apresentação final, a equipe deverá explicar o problema resolvido pelo diferencial, o algoritmo ou estrutura utilizado, as decisões de implementação e sua integração ao restante do sistema.

## Regras gerais

- A aplicação deverá ser desenvolvida em Python com Flask.
- A interface deverá utilizar HTML e templates Jinja; Bootstrap poderá ser utilizado.
- Não será permitido substituir a Árvore B por lista, dict ou biblioteca pronta como mecanismo principal de busca.
- A equipe poderá utilizar listas e dicionários internamente quando fizerem parte da implementação de uma estrutura, desde que não substituam a estrutura exigida.
- Arquivos JSON poderão ser utilizados para persistência.
- Os dados persistidos deverão ser carregados nas estruturas correspondentes durante a execução.
- Rotas que alteram dados deverão utilizar POST; recomenda-se o padrão Post/Redirect/Get.
- A lógica das estruturas deverá ser separada das rotas Flask.

---

## ETAPA 1 — Tabela Hash e Aplicação Web

Construir a primeira versão funcional da aplicação Web e implementar o gerenciamento dos países atendidos pela GlobalSIM utilizando uma **Tabela Hash**.

### Dados dos países

Cada país deverá possuir um código utilizado como chave. Recomenda-se o código internacional de duas letras.

| Código | País |
|---|---|
| BR | Brasil |
| PT | Portugal |
| ES | Espanha |
| FR | França |
| IT | Itália |
| US | Estados Unidos |
| CA | Canadá |
| JP | Japão |

Exemplo de registro:

```json
{
  "codigo": "IT",
  "pais": "Itália",
  "regiao": "Europa",
  "operadora": "Operadora IT",
  "tecnologia": "5G"
}
```

### Funcionalidades Web obrigatórias

- Página inicial da GlobalSIM.
- Cadastro de país atendido.
- Consulta de cobertura por código do país.
- Listagem dos países cadastrados.
- Alteração dos dados de um país.
- Remoção de país.
- Persistência dos dados em arquivo JSON.

A aplicação deverá exercitar rotas, GET, POST, `request`, `render_template()`, `redirect()`, Jinja e formulários HTML.

### Exemplo de consulta de cobertura

```
Código do país: [ IT ]
[ Verificar cobertura ]

COBERTURA DISPONÍVEL
País:       Itália
Região:     Europa
Operadora:  Operadora IT
Tecnologia: 5G
```

### Entrega da Etapa 1 — 20/10/2026

- Código-fonte da aplicação Flask.
- Implementação da Tabela Hash.
- Arquivos JSON utilizados.
- Cadastro, consulta, alteração, remoção e listagem funcionando.
- Instrumentação básica da estrutura.
- Descrição inicial do diferencial escolhido pela equipe e como ele será integrado ao projeto.

---

## ETAPA 2 — Árvore B e Gerenciamento de Clientes

Ampliar o GlobalSIM para administrar um grande conjunto de clientes e eSIMs por meio de uma **Árvore B**, integrando essa nova estrutura à Tabela Hash desenvolvida na Etapa 1.

### Volume e estrutura dos clientes

O sistema deverá trabalhar com centenas de clientes. Recomenda-se um conjunto de aproximadamente **1.000 registros** (gerados automaticamente), permitindo observar o comportamento da Árvore B em buscas e inserções.

```json
{
  "id": 58372,
  "nome": "Maria Silva",
  "email": "maria@email.com",
  "esim": "ESIM-83921",
  "pacote": 102,
  "status": "ativo"
}
```

O ID do cliente deverá ser único e será utilizado como chave da Árvore B.

### Implementação da Árvore B

- Carga de clientes para a Árvore B.
- Cadastro de cliente.
- Consulta de cliente por ID.
- Listagem de clientes.
- Alteração dos dados de um cliente.
- Associação de eSIM e pacote ao cliente.
- Persistência dos registros.
- Manutenção integral das funcionalidades da Tabela Hash.

### Integração Árvore B × Tabela Hash

A aplicação deverá permitir operações integradas. Exemplo:

```
Entrada:
  Cliente: 58372
  Destino: IT

1. ÁRVORE B
   buscar(58372)
   → Maria Silva
   → eSIM: ESIM-83921
   → pacote: 102

2. TABELA HASH
   buscar("IT")
   → Itália
   → cobertura disponível
   → tecnologia: 5G
```

### Pacotes de serviço

Os pacotes poderão ser armazenados em JSON/lista, pois não constituem uma quarta estrutura principal.

| Código | Pacote | Dados | Validade |
|---|---|---|---|
| 101 | Europa Basic | 5 GB | 15 dias |
| 102 | Europa Plus | 10 GB | 30 dias |
| 201 | América Basic | 5 GB | 15 dias |
| 202 | América Plus | 15 GB | 30 dias |
| 301 | Global | 20 GB | 30 dias |

### Entrega da Etapa 2 — 24/11/2026

- Etapa 1 preservada e integrada.
- Implementação funcional da Árvore B.
- Carga do conjunto de clientes.
- Cadastro, busca, listagem e alteração de clientes.
- Integração cliente × país de destino.
- Primeira implementação funcional do diferencial, quando aplicável.

---

## ETAPA 3 — Grafos e Integração Final

Representar a rede internacional da GlobalSIM utilizando um **grafo ponderado** e integrar as três estruturas em uma consulta completa de serviço.

### Modelo do Grafo

Cada país atendido poderá ser representado por um vértice. As conexões entre pontos da infraestrutura serão arestas. O peso de cada aresta representará uma latência simulada em milissegundos.

Rede de exemplo (grafo não direcionado):

| Origem | Destino | Latência (ms) |
|---|---|---|
| BR | US | 80 |
| BR | PT | 120 |
| PT | ES | 30 |
| PT | FR | 40 |
| FR | IT | 25 |
| US | CA | 20 |
| CA | JP | 110 |

```
   BR ───80─── US
   │           │
  120          20
   │           │
   PT          CA
  /  \          \
 30   40        110
 /      \         \
ES      FR        JP
        │
        25
        │
        IT
```

### Implementação do Grafo

Deverão ser implementados **Breadth-First Search** (BFS, Busca em Largura), **Depth-First Search** (DFS, Busca em Profundidade) e o **algoritmo de Dijkstra**.

### Rota de menor latência

Para fins do trabalho, a melhor rota será aquela cuja soma das latências simuladas das arestas seja mínima.

### Consulta final integrada

1. Pesquisar o cliente na Árvore B.
2. Verificar na Tabela Hash se o destino é atendido.
3. Identificar o pacote associado ao cliente.
4. Localizar origem e destino no Grafo.
5. Calcular a rota de menor latência com Dijkstra.
6. Apresentar o resultado ao usuário.

Exemplo:

```
CONSULTA DE CONECTIVIDADE

Cliente: Maria Silva
eSIM:    ESIM-83921
Status:  Ativo

Pacote:   Europa Plus
Dados:    10 GB
Validade: 30 dias

Destino:    Itália
Cobertura:  Disponível
Tecnologia: 5G

Melhor rota:
Brasil → Portugal → França → Itália

Latência estimada: 185 ms
```

### Entrega da Etapa 3 — 01/12/2026

- Etapas 1 e 2 preservadas e integradas.
- Implementação do Grafo.
- BFS e DFS funcionando.
- Dijkstra e cálculo de menor caminho funcionando.
- Consulta integrada cliente × cobertura × rede.
- Visualização do Grafo.
- Diferencial da equipe totalmente implementado e integrado.
- Documentação final e apresentação do sistema.

---

## Estrutura sugerida do projeto

```
globalsim/
│
├── app.py
├── estruturas/
│   ├── tabela_hash.py
│   ├── arvore_b.py
│   └── grafo.py
│
├── arquivos/
│   ├── paises.json
│   ├── clientes.json
│   ├── pacotes.json
│   └── rede.json
│
├── templates/
│   ├── index.html
│   ├── paises.html
│   ├── clientes.html
│   ├── cobertura.html
│   ├── rede.html
│   └── consulta.html
│
└── static/
    └── css/
```

## Persistência

```
ARQUIVOS JSON
     │  carregar
     ▼
ESTRUTURAS EM MEMÓRIA
     │  operações
     ▼
ESTRUTURAS MODIFICADAS
     │  persistir
     ▼
ARQUIVOS JSON
```

A persistência não deverá substituir o uso das estruturas. Por exemplo, uma busca de cliente não deverá ser realizada diretamente em uma lista carregada do JSON quando o requisito exige a Árvore B.

---

## Apresentação das Etapas

Na apresentação, todos os integrantes deverão estar aptos a explicar o funcionamento das estruturas, a integração com Flask e o diferencial desenvolvido.

## Critérios gerais de avaliação

| Critério | Aspectos observados |
|---|---|
| Tabela Hash | Correção, uso efetivo e compreensão. |
| Árvore B | Correção, divisões, busca, uso efetivo e compreensão. |
| Grafos | Representação, BFS, DFS, Dijkstra e uso efetivo. |
| Aplicação Web | Rotas, formulários, templates, integração e organização. |
| Integração | Coerência entre países, clientes, pacotes e rede. |
| Instrumentação | Capacidade de observar e analisar as estruturas. |
| Diferencial | Relevância, complexidade, originalidade e integração. |
| Código e documentação | Modularização, clareza e qualidade técnica. |
| Apresentação | Demonstração funcional e domínio conceitual da equipe. |

## Importante

**Criar um repositório GitHub por equipe** para o desenvolvimento e entrega das etapas do projeto, mantendo um **README (relatório)** contendo identificação da equipe, instruções para execução, descrição das estruturas implementadas e o diferencial escolhido.

**O objetivo final não é apenas produzir um site, mas demonstrar como diferentes estruturas de dados resolvem problemas distintos dentro de uma mesma aplicação.**
