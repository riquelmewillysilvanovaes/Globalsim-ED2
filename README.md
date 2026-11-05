# GlobalSIM — Gestão Internacional de eSIM (EDII)

Aplicação Web desenvolvida em Python e Flask para a administração de cobertura internacional de Internet móvel por eSIM, clientes, pacotes de conectividade e roteamento de conexões. O projeto é desenvolvido de maneira incremental para a disciplina de **Estruturas de Dados II**, integrando Tabela Hash (Etapa 1), Árvore B (Etapa 2) e Grafos Ponderados (Etapa 3) com operações persistidas em arquivos JSON e interface Web interativa em Bootstrap 5.

---

## Identificação da Equipe

* **João Arthur Valente Lima**
* **João Gabriel Lima Meneses**
* **Riquelme Willy Silva Novaes**

* **Instituição:** Universidade do Estado da Bahia (UNEB)
* **Departamento:** Departamento de Ciências Exatas e da Terra (DCET / Campus I)
* **Curso:** Bacharelado em Sistemas de Informação
* **Disciplina:** Estruturas de Dados II
* **Docente:** Prof.ª Maria Inés Restovic
* **Semestre Letivo:** 2026.2

---

## 📁 Estrutura do Projeto

A organização dos diretórios do repositório reflete a modularização exigida pelo projeto prático:

```text
Globalsim-ED2/
├── .venv/                         # Ambiente virtual Python isolado
├── globalsim/
│   ├── app.py                     # Inicialização da aplicação Flask e rotas HTTP
│   ├── config.py                  # Caminhos dos JSON, grau da Árvore B, paginação
│   ├── requirements.txt           # Dependências do projeto (Flask, pytest)
│   ├── pytest.ini                 # Configuração dos testes
│   ├── INTERFACE_TABELA_HASH.md   # Especificação técnica da Tabela Hash
│   ├── arquivos/
│   │   ├── paises.json            # Países atendidos (Tabela Hash)
│   │   ├── clientes.json          # 1.000 clientes gerados (Árvore B)
│   │   └── pacotes.json           # Pacotes de serviço (lista)
│   ├── estruturas/
│   │   ├── tabela_hash.py         # Tabela Hash (Etapa 1)
│   │   └── arvore_b.py            # Árvore B: ArvoreB e NoB (Etapa 2)
│   ├── servicos/
│   │   ├── persistencia.py        # Leitura/gravação dos JSON (escrita atômica)
│   │   ├── paises_service.py      # Regras de negócio dos países
│   │   ├── clientes_service.py    # Regras de negócio dos clientes e eSIMs
│   │   ├── pacotes_service.py     # Pacotes e cobertura por região
│   │   └── consulta.py            # Consulta integrada cliente × destino
│   ├── scripts/
│   │   └── gerar_clientes.py      # Gera arquivos/clientes.json (seed fixa)
│   ├── static/css/style.css       # Estilos complementares da interface
│   ├── templates/
│   │   ├── base.html              # Template mestre com Bootstrap 5 e Navbar
│   │   ├── index.html             # Página inicial
│   │   ├── paises.html            # Listagem de países
│   │   ├── pais_form.html         # Cadastro e edição de país
│   │   ├── cobertura.html         # Consulta de cobertura
│   │   ├── clientes.html          # Listagem paginada + busca por ID
│   │   ├── cliente_form.html      # Cadastro e edição de cliente
│   │   ├── cliente_detalhe.html   # Cliente + caminho da busca na Árvore B
│   │   ├── cliente_esim.html      # Associação de eSIM e pacote
│   │   ├── consulta.html          # Consulta integrada cliente × destino
│   │   └── metricas.html          # Instrumentação da Hash e da Árvore B
│   └── tests/
│       ├── test_tabela_hash.py    # Testes da Tabela Hash
│       ├── test_arvore_b.py       # Testes da Árvore B e do serviço de clientes
│       └── test_app.py            # Testes das rotas e da consulta integrada
├── .gitignore
└── README.md
```

---

## 🚀 Instruções para Execução

### Pré-requisitos
* Python 3.10 ou superior
* Git

### 1. Clonar o Repositório
```bash
git clone https://github.com/riquelmewillysilvanovaes/Globalsim-ED2.git
cd Globalsim-ED2
```

### 2. Ativação do Ambiente Virtual (`.venv`)
* **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```
* **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
* **Windows (Prompt de Comando / CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

> *Caso o ambiente virtual ainda não tenha sido inicializado no diretório, execute `python3 -m venv .venv` antes da ativação.*

### 3. Instalar Dependências
```bash
pip install -r globalsim/requirements.txt
```

### 4. Executar o Servidor Flask
Navegue até a pasta da aplicação e inicie o servidor:
```bash
cd globalsim
python app.py
```
*(Alternativamente: `flask --app app run --debug`)*

### 5. Acessar a Aplicação no Navegador
Abra o navegador e acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 6. Executar os Testes
Dentro da pasta `globalsim/`:
```bash
pytest -q
```

### 7. (Re)gerar a base de clientes
O repositório já traz `arquivos/clientes.json` com 1.000 clientes. Para recriá-lo (mesma seed, mesmo resultado):
```bash
cd globalsim
python scripts/gerar_clientes.py          # ou: python scripts/gerar_clientes.py 5000
```

---

## 🔑 Etapa 1 — Tabela Hash (`globalsim/estruturas/tabela_hash.py`)

Os países atendidos ficam numa Tabela Hash implementada do zero (sem `dict`), indexada pelo código do país (`BR`, `IT`, ...).

* **Colisões:** encadeamento separado. Cada posição do vetor (bucket) é uma lista de pares `[chave, valor]`; chaves que caem no mesmo índice ficam na mesma cadeia.
* **Função de hash:** polinomial própria, `h = (h * 31 + ord(c)) % capacidade` para cada caractere. Não usamos `hash()` do Python porque ele muda a cada execução, o que tornaria a instrumentação não reproduzível.
* **Capacidade e rehash:** começa em 7 (primo pequeno, para colisões e redimensionamento aparecerem com os países cadastrados). Quando o fator de carga passa de 0,75, a capacidade dobra e é arredondada para o próximo primo (7 → 17 → 37 ...), e todas as chaves são reinseridas.
* **Operações:** `inserir` (rejeita código duplicado), `buscar`, `atualizar`, `remover`, `listar`/`itens`.
* **Instrumentação** (`metricas()` / `estatisticas()`): capacidade, nº de elementos, fator de carga, colisões atuais e acumuladas, maior bucket, buckets usados, nº de rehashes, comparações da última busca e o mapa dos buckets (índice → chaves).
* **Persistência:** `arquivos/paises.json` é carregado na tabela ao iniciar e regravado após cada cadastro, alteração ou remoção (`servicos/paises_service.py`).

---

## 🌳 Etapa 2 — Árvore B (`globalsim/estruturas/arvore_b.py`)

Os clientes ficam numa Árvore B implementada do zero, indexada pelo ID do cliente. Toda busca, listagem e alteração de cliente passa pela árvore; o JSON só é lido na carga e regravado depois de cada alteração.

* **Modelo:** implementação clássica (Cormen) com grau mínimo `t` configurável em `config.py` (padrão `t = 3`): cada nó guarda de `t−1 = 2` a `2t−1 = 5` chaves (a raiz pode ter menos), e um nó interno com `k` chaves tem `k+1` filhos. Cada chave anda junto com o registro do cliente (`no.chaves[i]` ↔ `no.valores[i]`).
* **Busca:** desce da raiz; em cada nó compara as chaves da esquerda para a direita até achar o ID ou a primeira chave maior, e desce pelo filho correspondente. Custo: no máximo `altura` nós visitados.
* **Inserção com split proativo:** na descida, todo filho cheio (5 chaves) é dividido **antes** de entrarmos nele — a chave do meio sobe para o pai, as 2 menores ficam no nó original e as 2 maiores vão para um nó novo. Assim a folha sempre tem espaço e nunca é preciso voltar subindo. Quando a raiz está cheia, cria-se uma raiz nova acima dela: é o único momento em que a árvore cresce, e ela cresce pelo topo, por isso todas as folhas ficam sempre no mesmo nível.
* **Operações:** `inserir` (rejeita ID duplicado), `buscar`, `atualizar`, `percorrer_em_ordem` (listagem ordenada por ID), `altura`. Remoção não é exigida pelo enunciado e não foi implementada.
* **Instrumentação** (`metricas()` / `estatisticas()`, página **Métricas**): nº de clientes, altura, total de nós, nº de splits, ocupação média dos nós, nós visitados e comparações da última busca, nós por nível, chaves dos 3 primeiros níveis e o caminho percorrido pela última busca (também mostrado na página de cada cliente).
* **Base de dados:** `scripts/gerar_clientes.py` gera 1.000 clientes com `random.seed(42)`, IDs únicos aleatórios de 5 dígitos, eSIM `ESIM-NNNNN`, pacote em {101, 102, 201, 202, 301} e status ativo/inativo/suspenso.
* **Ordem de carga (decisão de implementação):** o `clientes.json` é gravado em ordem de ID (percurso em ordem), mas inserir chaves já ordenadas é o pior caso da Árvore B com split proativo — cada split deixa o nó da esquerda com `t−1` chaves e ele nunca mais recebe nenhuma. Medimos com os 1.000 clientes:

  | Ordem de inserção | Altura | Nós | Splits | Ocupação média |
  |---|---|---|---|---|
  | Aleatória | 5 | 318 | 313 | 62,9% |
  | Ordenada por ID | 6 | 497 | 491 | 40,2% |

  Por isso `ClientesService.carregar()` embaralha a ordem de inserção com seed fixa: a árvore fica compacta e é igual em toda execução.

### Pacotes
`arquivos/pacotes.json` guarda os 5 pacotes do enunciado numa lista (o enunciado permite; não são uma estrutura avaliada). A equipe acrescentou o campo `cobertura` (`Europa`, `América` ou `Global`), usado para verificar se o pacote do cliente cobre a região do destino.

### Consulta integrada (`/consulta`)
Recebe o ID do cliente e o código do destino e executa, nesta ordem (`servicos/consulta.py`):
1. **Árvore B** — `buscar(id)`: nome, eSIM, pacote e status, com nós visitados e comparações.
2. **Tabela Hash** — `buscar("IT")`: país, cobertura e tecnologia, com comparações no bucket.
3. **Pacote** — dados, validade e se cobre a região do destino.

Trata cliente inexistente, destino não atendido, cliente inativo/suspenso, cliente sem eSIM/pacote e pacote que não cobre o destino. Na Etapa 3 a consulta ganha o Grafo e a rota de menor latência (Dijkstra).

### Rotas da Etapa 2
| Método | Rota | Função |
|---|---|---|
| GET | `/clientes?pagina=N` | Listagem paginada em ordem de ID + busca por ID |
| GET/POST | `/clientes/novo` | Cadastro (eSIM e pacote opcionais) |
| GET | `/clientes/<id>` | Consulta por ID, com o caminho da busca na árvore |
| GET/POST | `/clientes/<id>/editar` | Alteração de nome, e-mail e status |
| GET/POST | `/clientes/<id>/esim` | Associação de eSIM e pacote |
| GET | `/consulta?cliente=ID&destino=XX` | Consulta integrada cliente × destino |
| GET | `/metricas` | Instrumentação da Tabela Hash e da Árvore B |

Todas as alterações usam POST e seguem Post/Redirect/Get, com mensagens via `flash`.

---

## 💡 Diferencial da Equipe

### Tema: Simulação de Falhas de Conexões e Recálculo Automático das Rotas

* **Objetivo:** Simular quedas e indisponibilidades temporárias em enlaces da rede internacional e recalcular automaticamente a melhor rota alternativa de menor latência para o cliente.
* **Problema Resolvido:** Em operadoras globais de telecomunicações, rompimentos de cabos submarinos ou degradações de enlaces terrestres interrompem o fluxo de dados. O recálculo automatizado confere tolerância a falhas e alta disponibilidade ao serviço de eSIM.
* **Plano de Integração no Sistema:**
  * **Etapa 1 (Atual):** Modelagem estrutural dos países e operadoras na Tabela Hash, com persistência e padronização dos códigos-chave para identificação dos nós da malha.
  * **Etapa 2:** Mapeamento dos clientes indexados na Árvore B para identificar quais usuários e pacotes de viagem são impactados caso links específicos fiquem indisponíveis.
  * **Etapa 3:** Modelagem completa do grafo ponderado com BFS, DFS e Dijkstra. A interface fornecerá um painel administrativo para desativar conexões com um clique, disparando o recálculo imediato do caminho ótimo no subgrafo operacional ativo.
