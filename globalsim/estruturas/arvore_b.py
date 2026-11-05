"""
Árvore B (Etapa 2) — clientes indexados pelo ID.

Implementação clássica (Cormen, cap. 18) com grau mínimo `t`:
  - todo nó guarda no máximo 2t-1 chaves;
  - todo nó, exceto a raiz, guarda no mínimo t-1 chaves;
  - um nó interno com k chaves tem k+1 filhos;
  - todas as folhas ficam no mesmo nível.

Cada chave (ID do cliente) anda junto com o seu valor (o dict do cliente):
`no.chaves[i]` e `no.valores[i]` são o mesmo registro. `no.filhos[i]` guarda as
chaves menores que `no.chaves[i]` e `no.filhos[i+1]` as maiores.

Usamos `list` apenas internamente (vetor de chaves, de valores e de filhos de
cada nó); o mecanismo de busca é a descida pela árvore, não um dict.

Interface usada pelo serviço (servicos/clientes_service.py):
    inserir(chave, valor)    -> bool   True se inseriu, False se o ID já existia
    buscar(chave)            -> dict | None
    atualizar(chave, valor)  -> bool   True se atualizou, False se o ID não existe
    percorrer_em_ordem()     -> list[dict]  clientes ordenados pelo ID
    altura()                 -> int
    tamanho()                -> int
    metricas()               -> dict   (instrumentação da estrutura)
    estatisticas()           -> dict   metricas() + níveis da árvore + caminho da última busca
"""

GRAU_MINIMO_PADRAO = 3


class NoB:
    """Nó da Árvore B. `folha` indica se o nó não tem filhos."""

    def __init__(self, folha: bool = True):
        self.chaves = []
        self.valores = []
        self.filhos = []
        self.folha = folha

    def cheio(self, t: int) -> bool:
        return len(self.chaves) == 2 * t - 1


class ArvoreB:
    def __init__(self, t: int = GRAU_MINIMO_PADRAO):
        if t < 2:
            raise ValueError("O grau mínimo t da Árvore B deve ser pelo menos 2.")
        self.t = t
        self.raiz = NoB(folha=True)
        self._tamanho = 0
        self._total_nos = 1

        # contadores de instrumentação
        self._splits = 0
        self._chave_ultima_busca = None
        self._nos_visitados_ultima_busca = 0
        self._comparacoes_ultima_busca = 0
        self._caminho_ultima_busca = []

    # ---------- busca ----------
    def _localizar(self, chave: int, registrar: bool = False):
        """Desce da raiz procurando a chave. Retorna (no, indice) ou (None, -1).

        Em cada nó as chaves são comparadas da esquerda para a direita: ou
        achamos a chave, ou paramos na primeira chave maior e descemos para o
        filho à esquerda dela. Uma varredura linear basta, porque com t=3 o
        nó tem no máximo 5 chaves (busca binária não mudaria nada visível).

        Com registrar=True, guarda nós visitados, comparações e o caminho
        percorrido para a instrumentação (só buscar() faz isso, para que as
        verificações internas de inserir/atualizar não apaguem a medição).
        """
        no = self.raiz
        nos_visitados = 0
        comparacoes = 0
        caminho = []
        encontrado = None
        indice_encontrado = -1

        while no is not None:
            nos_visitados += 1
            i = 0
            achou = False
            while i < len(no.chaves):
                comparacoes += 1
                if chave == no.chaves[i]:
                    achou = True
                    break
                if chave < no.chaves[i]:
                    break
                i += 1

            caminho.append({
                "chaves": list(no.chaves),
                "indice_encontrado": i if achou else None,
                "folha": no.folha,
            })

            if achou:
                encontrado = no
                indice_encontrado = i
                break
            if no.folha:
                break  # chegou numa folha sem achar: a chave não existe
            no = no.filhos[i]

        if registrar:
            self._chave_ultima_busca = chave
            self._nos_visitados_ultima_busca = nos_visitados
            self._comparacoes_ultima_busca = comparacoes
            self._caminho_ultima_busca = caminho
        return encontrado, indice_encontrado

    def buscar(self, chave: int):
        """Devolve o valor associado ao ID, ou None. Registra a instrumentação."""
        no, indice = self._localizar(chave, registrar=True)
        if no is None:
            return None
        return no.valores[indice]

    def __contains__(self, chave: int) -> bool:
        no, _ = self._localizar(chave)
        return no is not None

    def atualizar(self, chave: int, valor: dict) -> bool:
        """Troca o valor de um ID existente (a chave não muda, a árvore não muda de forma)."""
        no, indice = self._localizar(chave)
        if no is None:
            return False
        no.valores[indice] = valor
        return True

    # ---------- inserção ----------
    def inserir(self, chave: int, valor: dict) -> bool:
        """Insere o par. Retorna False se o ID já existe (não sobrescreve).

        Usa split proativo (Cormen): durante a descida, todo filho cheio é
        dividido ANTES de entrarmos nele. Assim, quando chegamos na folha ela
        com certeza tem espaço, e nunca é preciso voltar subindo pela árvore.
        """
        if chave in self:
            return False

        raiz = self.raiz
        if raiz.cheio(self.t):
            # Raiz cheia: criamos uma raiz nova, vazia, com a antiga como único
            # filho, e dividimos a antiga. É o ÚNICO ponto em que a árvore ganha
            # altura — e ela cresce pelo topo, por isso todas as folhas
            # continuam sempre no mesmo nível.
            nova_raiz = NoB(folha=False)
            nova_raiz.filhos.append(raiz)
            self.raiz = nova_raiz
            self._total_nos += 1
            self._dividir_filho(nova_raiz, 0)

        self._inserir_em_no_nao_cheio(self.raiz, chave, valor)
        self._tamanho += 1
        return True

    def _dividir_filho(self, pai: NoB, i: int) -> None:
        """Divide (split) o filho cheio pai.filhos[i], que tem 2t-1 chaves.

        Antes:  pai: [ ... | ... ]          filho: [c0 .. c(t-2) | c(t-1) | ct .. c(2t-2)]
        Depois: pai: [ ... | c(t-1) | ... ] esquerdo: [c0 .. c(t-2)]  direito: [ct .. c(2t-2)]

        A chave do meio (mediana, índice t-1) sobe para o pai; as t-1 menores
        ficam no nó original e as t-1 maiores vão para um nó novo, que vira o
        filho logo à direita da mediana. Se o filho não é folha, os seus 2t
        filhos são repartidos t para cada lado.
        """
        t = self.t
        cheio = pai.filhos[i]
        novo = NoB(folha=cheio.folha)

        chave_mediana = cheio.chaves[t - 1]
        valor_mediano = cheio.valores[t - 1]

        novo.chaves = cheio.chaves[t:]
        novo.valores = cheio.valores[t:]
        if not cheio.folha:
            novo.filhos = cheio.filhos[t:]
            cheio.filhos = cheio.filhos[:t]
        cheio.chaves = cheio.chaves[:t - 1]
        cheio.valores = cheio.valores[:t - 1]

        pai.chaves.insert(i, chave_mediana)
        pai.valores.insert(i, valor_mediano)
        pai.filhos.insert(i + 1, novo)

        self._splits += 1
        self._total_nos += 1

    @staticmethod
    def _posicao(no: NoB, chave: int) -> int:
        """Quantas chaves do nó são menores que `chave` (= onde ela entraria)."""
        i = 0
        while i < len(no.chaves) and no.chaves[i] < chave:
            i += 1
        return i

    def _inserir_em_no_nao_cheio(self, no: NoB, chave: int, valor: dict) -> None:
        """Desce até a folha certa dividindo os filhos cheios no caminho."""
        while not no.folha:
            i = self._posicao(no, chave)
            if no.filhos[i].cheio(self.t):
                self._dividir_filho(no, i)
                # a mediana que subiu agora está em no.chaves[i]; se a chave
                # nova é maior que ela, o lugar certo é o nó da direita
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]

        i = self._posicao(no, chave)
        no.chaves.insert(i, chave)
        no.valores.insert(i, valor)

    # ---------- percursos ----------
    def percorrer_em_ordem(self) -> list:
        """Todos os valores em ordem crescente de ID (filho, chave, filho, chave, ..., filho)."""
        resultado = []
        self._em_ordem(self.raiz, resultado)
        return resultado

    def _em_ordem(self, no: NoB, resultado: list) -> None:
        for i in range(len(no.chaves)):
            if not no.folha:
                self._em_ordem(no.filhos[i], resultado)
            resultado.append(no.valores[i])
        if not no.folha:
            self._em_ordem(no.filhos[len(no.chaves)], resultado)

    def _nos_por_nivel(self) -> list:
        """Percurso em largura: lista de níveis, cada nível uma lista de nós."""
        niveis = []
        nivel_atual = [self.raiz]
        while len(nivel_atual) > 0:
            niveis.append(nivel_atual)
            proximo = []
            for no in nivel_atual:
                for filho in no.filhos:
                    proximo.append(filho)
            nivel_atual = proximo
        return niveis

    # ---------- consultas auxiliares ----------
    def altura(self) -> int:
        """Número de níveis (só a raiz = 1). Basta descer pelo filho mais à esquerda,
        porque todas as folhas estão na mesma profundidade."""
        niveis = 1
        no = self.raiz
        while not no.folha:
            no = no.filhos[0]
            niveis += 1
        return niveis

    def tamanho(self) -> int:
        return self._tamanho

    def __len__(self) -> int:
        return self._tamanho

    # ---------- instrumentação ----------
    def metricas(self) -> dict:
        """Números da estrutura (só valores simples, para exibir em tabela).

        - ocupacao_media: chaves armazenadas / espaço total dos nós (2t-1 por nó).
          Com split proativo fica entre ~50% e 100%.
        """
        capacidade_total = self._total_nos * (2 * self.t - 1)
        ocupacao = 0.0
        if capacidade_total > 0:
            ocupacao = 100 * self._tamanho / capacidade_total

        return {
            "tamanho": self._tamanho,
            "grau_minimo": self.t,
            "min_chaves": self.t - 1,
            "max_chaves": 2 * self.t - 1,
            "altura": self.altura(),
            "total_nos": self._total_nos,
            "splits": self._splits,
            "ocupacao_media": round(ocupacao, 1),
            "chave_ultima_busca": self._chave_ultima_busca,
            "nos_visitados_ultima_busca": self._nos_visitados_ultima_busca,
            "comparacoes_ultima_busca": self._comparacoes_ultima_busca,
        }

    def estatisticas(self, niveis_exibidos: int = 3) -> dict:
        """metricas() + visualização dos primeiros níveis + caminho da última busca.

        - nos_por_nivel: quantos nós cada nível tem (todos os níveis).
        - niveis: as chaves de cada nó, só nos `niveis_exibidos` primeiros níveis
          (os últimos têm centenas de nós e não cabem na tela).
        """
        dados = self.metricas()
        todos_niveis = self._nos_por_nivel()

        nos_por_nivel = []
        for nivel in todos_niveis:
            nos_por_nivel.append(len(nivel))

        niveis = []
        for numero in range(min(niveis_exibidos, len(todos_niveis))):
            nos = []
            for no in todos_niveis[numero]:
                nos.append(list(no.chaves))
            niveis.append(nos)

        dados["nos_por_nivel"] = nos_por_nivel
        dados["niveis"] = niveis
        dados["caminho_ultima_busca"] = self._caminho_ultima_busca
        return dados
