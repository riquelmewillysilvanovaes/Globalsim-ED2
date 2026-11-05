"""
Gera arquivos/clientes.json com ~1.000 clientes fictícios.

Uso (de dentro de globalsim/):
    python scripts/gerar_clientes.py            # 1000 clientes
    python scripts/gerar_clientes.py 5000       # outra quantidade

A seed é fixa (42): rodar de novo gera exatamente o mesmo arquivo, então a
instrumentação da Árvore B (splits, altura, nós) é reproduzível.

Os IDs são sorteados sem repetição (não sequenciais), como numa base real,
para que a Árvore B receba chaves espalhadas e faça splits em vários pontos.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CAMINHO_CLIENTES  # noqa: E402
from servicos.persistencia import salvar_json  # noqa: E402

SEED = 42
QUANTIDADE_PADRAO = 1000

PRIMEIROS_NOMES = [
    "Maria", "João", "Ana", "Pedro", "Juliana", "Lucas", "Fernanda", "Gabriel",
    "Beatriz", "Rafael", "Camila", "Mateus", "Larissa", "Gustavo", "Mariana",
    "Felipe", "Letícia", "Bruno", "Amanda", "Thiago", "Patrícia", "Diego",
    "Carolina", "Rodrigo", "Isabela", "Vinícius", "Aline", "Leonardo", "Bianca",
    "Eduardo", "Renata", "André", "Tatiana", "Ricardo", "Sofia", "Daniel",
]
SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa",
    "Rodrigues", "Almeida", "Nascimento", "Carvalho", "Araújo", "Ribeiro",
    "Gomes", "Martins", "Barbosa", "Rocha", "Dias", "Moreira", "Cardoso",
    "Teixeira", "Mendes", "Freitas", "Batista", "Meneses", "Novaes",
]
DOMINIOS = ["email.com", "gmail.com", "outlook.com", "uneb.br"]
PACOTES = [101, 102, 201, 202, 301]
STATUS = ["ativo", "inativo", "suspenso"]
PESOS_STATUS = [80, 12, 8]  # maioria ativa, como numa base real


def sem_acentos(texto):
    trocas = {"á": "a", "ã": "a", "â": "a", "é": "e", "ê": "e", "í": "i",
              "ó": "o", "ô": "o", "ú": "u", "ç": "c"}
    resultado = ""
    for caractere in texto.lower():
        resultado += trocas.get(caractere, caractere)
    return resultado


def gerar(quantidade):
    gerador = random.Random(SEED)
    # sample sorteia sem repetição: IDs e eSIMs únicos de 5 dígitos
    ids = gerador.sample(range(10000, 100000), quantidade)
    numeros_esim = gerador.sample(range(10000, 100000), quantidade)

    clientes = []
    for i in range(quantidade):
        nome = gerador.choice(PRIMEIROS_NOMES)
        sobrenome = gerador.choice(SOBRENOMES)
        usuario = f"{sem_acentos(nome)}.{sem_acentos(sobrenome)}{ids[i] % 1000}"
        clientes.append({
            "id": ids[i],
            "nome": f"{nome} {sobrenome}",
            "email": f"{usuario}@{gerador.choice(DOMINIOS)}",
            "esim": f"ESIM-{numeros_esim[i]:05d}",
            "pacote": gerador.choice(PACOTES),
            "status": gerador.choices(STATUS, weights=PESOS_STATUS)[0],
        })
    return clientes


def main():
    quantidade = QUANTIDADE_PADRAO
    if len(sys.argv) > 1:
        quantidade = int(sys.argv[1])
    clientes = gerar(quantidade)
    salvar_json(CAMINHO_CLIENTES, clientes)
    print(f"{len(clientes)} clientes gravados em {CAMINHO_CLIENTES}")


if __name__ == "__main__":
    main()
