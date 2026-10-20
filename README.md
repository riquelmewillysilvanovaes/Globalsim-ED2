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
│   ├── requirements.txt           # Dependências do projeto (Flask, etc.)
│   ├── INTERFACE_TABELA_HASH.md   # Especificação técnica da Tabela Hash
│   ├── arquivos/
│   │   └── paises.json            # Persistência dos registros de países
│   ├── estruturas/
│   │   ├── __init__.py
│   │   └── tabela_hash.py         # Implementação própria da Tabela Hash
│   ├── servicos/
│   │   ├── __init__.py
│   │   └── paises_service.py      # Camada de serviços e regras de negócio
│   ├── static/
│   │   └── css/
│   │       └── style.css          # Estilos complementares da interface
│   └── templates/
│       ├── base.html              # Template mestre com Bootstrap 5 e Navbar
│       ├── index.html             # Página inicial / Apresentação do serviço
│       ├── paises.html            # Listagem de países e painel de métricas
│       ├── pais_form.html         # Formulário unificado (cadastro e edição)
│       └── cobertura.html         # Consulta de disponibilidade de rede
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

---

## 💡 Diferencial da Equipe

### Tema: Simulação de Falhas de Conexões e Recálculo Automático das Rotas

* **Objetivo:** Simular quedas e indisponibilidades temporárias em enlaces da rede internacional e recalcular automaticamente a melhor rota alternativa de menor latência para o cliente.
* **Problema Resolvido:** Em operadoras globais de telecomunicações, rompimentos de cabos submarinos ou degradações de enlaces terrestres interrompem o fluxo de dados. O recálculo automatizado confere tolerância a falhas e alta disponibilidade ao serviço de eSIM.
* **Plano de Integração no Sistema:**
  * **Etapa 1 (Atual):** Modelagem estrutural dos países e operadoras na Tabela Hash, com persistência e padronização dos códigos-chave para identificação dos nós da malha.
  * **Etapa 2:** Mapeamento dos clientes indexados na Árvore B para identificar quais usuários e pacotes de viagem são impactados caso links específicos fiquem indisponíveis.
  * **Etapa 3:** Modelagem completa do grafo ponderado com BFS, DFS e Dijkstra. A interface fornecerá um painel administrativo para desativar conexões com um clique, disparando o recálculo imediato do caminho ótimo no subgrafo operacional ativo.
