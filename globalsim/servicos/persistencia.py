"""
Leitura e gravação dos arquivos JSON.

Os JSON são só a fonte de carga e de salvamento: o serviço lê o arquivo,
insere tudo na estrutura e, depois de cada alteração, regrava o arquivo a
partir da estrutura.
"""
import json
import os


def carregar_json(caminho, padrao=None):
    """Conteúdo do arquivo, ou `padrao` se ele não existe."""
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho, dados):
    """Grava em um arquivo temporário e depois troca pelo definitivo.

    os.replace é atômico: se o programa cair no meio da gravação, o JSON
    antigo continua inteiro em vez de ficar pela metade.
    """
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    os.replace(temporario, caminho)
