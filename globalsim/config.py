"""Configurações do GlobalSIM: caminhos dos JSON e parâmetros das estruturas."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ARQUIVOS = os.path.join(BASE_DIR, "arquivos")

CAMINHO_PAISES = os.path.join(PASTA_ARQUIVOS, "paises.json")
CAMINHO_CLIENTES = os.path.join(PASTA_ARQUIVOS, "clientes.json")
CAMINHO_PACOTES = os.path.join(PASTA_ARQUIVOS, "pacotes.json")

# Árvore B: cada nó guarda de t-1 a 2t-1 chaves (t=3 -> 2 a 5 chaves por nó)
GRAU_MINIMO_ARVORE_B = 3

# listagem de clientes
CLIENTES_POR_PAGINA = 25
