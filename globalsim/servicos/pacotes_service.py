"""
Pacotes de serviço (101, 102, 201, 202, 301).

O enunciado permite guardar os pacotes em JSON/lista: são só 5 registros
fixos e não são uma estrutura avaliada. Por isso a busca aqui é linear.

Campo `cobertura` (definido pela equipe): "Europa", "América" ou "Global".
Um pacote cobre um país quando a região do país começa com a cobertura do
pacote ("América" cobre "América do Sul" e "América do Norte"); "Global"
cobre todos.
"""
import unicodedata

from servicos.persistencia import carregar_json

COBERTURA_GLOBAL = "global"


def _sem_acentos(texto):
    """'América do Sul' -> 'america do sul' (compara regiões digitadas com ou sem acento)."""
    decomposto = unicodedata.normalize("NFD", texto or "")
    letras = []
    for caractere in decomposto:
        if unicodedata.category(caractere) != "Mn":  # Mn = acento separado
            letras.append(caractere)
    return "".join(letras).strip().lower()


class PacotesService:
    def __init__(self, caminho_json):
        self.caminho_json = caminho_json
        self._pacotes = carregar_json(caminho_json, padrao=[])

    def listar(self):
        return self._pacotes

    def buscar(self, codigo):
        """Pacote com o código (int), ou None."""
        for pacote in self._pacotes:
            if pacote["codigo"] == codigo:
                return pacote
        return None

    def codigos(self):
        resultado = []
        for pacote in self._pacotes:
            resultado.append(pacote["codigo"])
        return resultado

    @staticmethod
    def cobre(pacote, pais):
        """True se o pacote dá direito a usar dados no país."""
        cobertura = _sem_acentos(pacote["cobertura"])
        if cobertura == COBERTURA_GLOBAL:
            return True
        return _sem_acentos(pais["regiao"]).startswith(cobertura)
