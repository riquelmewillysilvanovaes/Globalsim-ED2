"""
Tabela Hash com encadeamento separado (Etapa 1).

Cada posição do vetor (bucket) é uma lista de pares [chave, valor]. Quando
duas chaves caem no mesmo índice (colisão), o par novo é colocado no fim da
lista daquele bucket. A busca calcula o índice e percorre só aquele bucket.

Usamos `list` apenas internamente (vetor de buckets e cada cadeia); o
mecanismo de busca é a função de hash + o encadeamento, não um dict.

Interface usada pelo serviço (servicos/paises_service.py):
    inserir(chave, valor)    -> bool   True se inseriu, False se a chave já existia
    buscar(chave)            -> dict | None
    atualizar(chave, valor)  -> bool   True se atualizou, False se a chave não existe
    remover(chave)           -> bool   True se removeu, False se a chave não existe
    listar()                 -> list[dict]
    tamanho()                -> int
    metricas()               -> dict   (instrumentação da estrutura)
"""

CAPACIDADE_INICIAL = 7  # prima e pequena: colisões e rehash aparecem com poucos países
FATOR_CARGA_MAXIMO = 0.75
BASE_HASH = 31


def _eh_primo(n: int) -> bool:
    """Testa divisores ímpares até a raiz de n."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def _proximo_primo(n: int) -> int:
    """Menor primo maior ou igual a n."""
    while not _eh_primo(n):
        n += 1
    return n


class TabelaHash:
    def __init__(self, capacidade: int = CAPACIDADE_INICIAL):
        self._capacidade = _proximo_primo(max(capacidade, 2))
        self._buckets = self._criar_buckets(self._capacidade)
        self._tamanho = 0

        # contadores de instrumentação
        self._colisoes_acumuladas = 0
        self._rehashes = 0
        self._comparacoes_ultima_busca = 0

    # ---------- função de hash ----------
    def _hash(self, chave: str) -> int:
        """Hash polinomial sobre os caracteres da chave.

        Não usamos hash() do Python porque ele é randomizado a cada execução
        (PYTHONHASHSEED), o que mudaria a posição dos países entre execuções
        e tornaria a instrumentação impossível de reproduzir.

        h = (h * 31 + código do caractere) mod capacidade. Aplicar o módulo a
        cada passo mantém o número pequeno; multiplicar pela base faz a ordem
        dos caracteres importar ("BR" e "RB" caem em índices diferentes).
        """
        h = 0
        for caractere in chave:
            h = (h * BASE_HASH + ord(caractere)) % self._capacidade
        return h

    @staticmethod
    def _criar_buckets(capacidade: int) -> list:
        buckets = []
        for _ in range(capacidade):
            buckets.append([])
        return buckets

    def _bucket_da_chave(self, chave: str) -> list:
        return self._buckets[self._hash(chave)]

    # ---------- operações ----------
    def inserir(self, chave: str, valor: dict) -> bool:
        """Insere o par. Retorna False se a chave já existe (não sobrescreve)."""
        bucket = self._bucket_da_chave(chave)
        for par in bucket:
            if par[0] == chave:
                return False

        if len(bucket) > 0:
            self._colisoes_acumuladas += 1
        bucket.append([chave, valor])
        self._tamanho += 1

        if self.fator_carga() > FATOR_CARGA_MAXIMO:
            self._rehash()
        return True

    def buscar(self, chave: str):
        """Devolve o valor da chave, ou None. Conta as comparações feitas."""
        bucket = self._bucket_da_chave(chave)
        comparacoes = 0
        for par in bucket:
            comparacoes += 1
            if par[0] == chave:
                self._comparacoes_ultima_busca = comparacoes
                return par[1]
        self._comparacoes_ultima_busca = comparacoes
        return None

    def atualizar(self, chave: str, valor: dict) -> bool:
        """Troca o valor de uma chave existente. False se a chave não existe."""
        bucket = self._bucket_da_chave(chave)
        for par in bucket:
            if par[0] == chave:
                par[1] = valor
                return True
        return False

    def remover(self, chave: str) -> bool:
        """Remove a chave da sua cadeia. False se a chave não existe."""
        bucket = self._bucket_da_chave(chave)
        for posicao in range(len(bucket)):
            if bucket[posicao][0] == chave:
                bucket.pop(posicao)
                self._tamanho -= 1
                return True
        return False

    def _rehash(self) -> None:
        """Dobra a capacidade (arredondando para o próximo primo) e reinsere tudo.

        Como o índice depende da capacidade (mod capacidade), toda chave
        precisa ser recalculada; não dá para só copiar os buckets.
        Capacidade prima espalha melhor as chaves no módulo.
        """
        buckets_antigos = self._buckets
        self._capacidade = _proximo_primo(2 * self._capacidade)
        self._buckets = self._criar_buckets(self._capacidade)
        for bucket in buckets_antigos:
            for chave, valor in bucket:
                self._bucket_da_chave(chave).append([chave, valor])
        self._rehashes += 1

    # ---------- consultas auxiliares ----------
    def itens(self) -> list:
        """Lista de pares (chave, valor), na ordem dos buckets."""
        resultado = []
        for bucket in self._buckets:
            for chave, valor in bucket:
                resultado.append((chave, valor))
        return resultado

    def listar(self) -> list:
        """Todos os valores armazenados (a ordem não importa)."""
        valores = []
        for _, valor in self.itens():
            valores.append(valor)
        return valores

    def tamanho(self) -> int:
        return self._tamanho

    def fator_carga(self) -> float:
        return self._tamanho / self._capacidade

    def __len__(self) -> int:
        return self._tamanho

    def __contains__(self, chave: str) -> bool:
        bucket = self._bucket_da_chave(chave)
        for par in bucket:
            if par[0] == chave:
                return True
        return False

    # ---------- instrumentação ----------
    def metricas(self) -> dict:
        """Números da estrutura (só valores simples, para exibir em tabela).

        - colisoes: chaves que hoje dividem bucket com outra (soma de len-1).
        - colisoes_acumuladas: inserções que caíram em bucket já ocupado,
          desde a criação da tabela (inclui as que o rehash depois desfez).
        """
        colisoes = 0
        maior_bucket = 0
        buckets_usados = 0
        for bucket in self._buckets:
            if len(bucket) > 0:
                buckets_usados += 1
                colisoes += len(bucket) - 1
            if len(bucket) > maior_bucket:
                maior_bucket = len(bucket)

        return {
            "tamanho": self._tamanho,
            "capacidade": self._capacidade,
            "fator_carga": round(self.fator_carga(), 2),
            "colisoes": colisoes,
            "colisoes_acumuladas": self._colisoes_acumuladas,
            "maior_bucket": maior_bucket,
            "buckets_usados": buckets_usados,
            "rehashes": self._rehashes,
            "comparacoes_ultima_busca": self._comparacoes_ultima_busca,
        }

    def estatisticas(self) -> dict:
        """metricas() + o mapa dos buckets (índice -> chaves), para /instrumentacao."""
        dados = self.metricas()
        mapa = []
        for indice in range(self._capacidade):
            chaves = []
            for par in self._buckets[indice]:
                chaves.append(par[0])
            mapa.append({"indice": indice, "chaves": chaves})
        dados["mapa_buckets"] = mapa
        return dados
