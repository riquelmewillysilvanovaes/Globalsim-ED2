"""
PLACEHOLDER da Tabela Hash.

Este arquivo existe só para o Flask funcionar enquanto a Tabela Hash real
não fica pronta. Ele usa um dict por dentro, o que NÃO é aceito na entrega
final. O colega responsável deve substituir este arquivo mantendo a MESMA
interface (nomes de métodos, parâmetros e retornos) descrita abaixo.

Interface combinada:
    inserir(chave, valor)    -> bool   True se inseriu, False se a chave já existia
    buscar(chave)            -> dict | None
    atualizar(chave, valor)  -> bool   True se atualizou, False se a chave não existe
    remover(chave)           -> bool   True se removeu, False se a chave não existe
    listar()                 -> list[dict]
    tamanho()                -> int
    metricas()               -> dict   (instrumentação da estrutura)
"""


class TabelaHash:
    def __init__(self, capacidade=11):
        self._capacidade = capacidade
        self._dados = {}  # provisório: trocar por buckets/encadeamento ou endereçamento aberto

    def inserir(self, chave, valor):
        if chave in self._dados:
            return False
        self._dados[chave] = valor
        return True

    def buscar(self, chave):
        return self._dados.get(chave)

    def atualizar(self, chave, valor):
        if chave not in self._dados:
            return False
        self._dados[chave] = valor
        return True

    def remover(self, chave):
        if chave not in self._dados:
            return False
        del self._dados[chave]
        return True

    def listar(self):
        return list(self._dados.values())

    def tamanho(self):
        return len(self._dados)

    def metricas(self):
        """Devolve um dict com dados para a tela de instrumentação.

        A versão real pode acrescentar outras chaves (o template exibe todas),
        por exemplo: comparações na última busca, tempo de operação etc.
        """
        return {
            "tamanho": self.tamanho(),
            "capacidade": self._capacidade,
            "fator_carga": round(self.tamanho() / self._capacidade, 2),
            "colisoes": 0,
            "maior_cadeia": 0,
            "buckets_usados": 0,
        }
