"""
Consulta integrada cliente × destino (Etapa 2).

Junta as estruturas na ordem do enunciado:
  1. Árvore B   -> buscar(id) do cliente (nome, eSIM, status, pacote)
  2. Tabela Hash -> buscar(código) do destino (cobertura, tecnologia)
  3. Pacotes     -> dados, validade e se o pacote cobre a região do destino

Cada passo guarda também a instrumentação da estrutura que respondeu
(nós visitados/comparações na Árvore B, comparações na Tabela Hash), para a
tela mostrar o "custo" de cada busca. Na Etapa 3 entram o Grafo e o Dijkstra.
"""


class ConsultaIntegrada:
    def __init__(self, clientes, paises, pacotes):
        self.clientes = clientes
        self.paises = paises
        self.pacotes = pacotes

    def executar(self, cliente_id_texto, destino_texto):
        """Retorna um dict com o resultado de cada passo, avisos e o veredito final."""
        destino = (destino_texto or "").strip().upper()
        resultado = {
            "entrada": {"cliente": (cliente_id_texto or "").strip(), "destino": destino},
            "erros": [],
            "avisos": [],
            "cliente": None,
            "busca_arvore": None,
            "pais": None,
            "busca_hash": None,
            "pacote": None,
            "pacote_cobre_destino": None,
            "pode_conectar": False,
        }

        cliente_id = self.clientes.converter_id(cliente_id_texto)
        if cliente_id is None:
            resultado["erros"].append("O ID do cliente deve ser um número inteiro positivo.")
        if len(destino) != 2 or not destino.isalpha():
            resultado["erros"].append("O destino deve ser um código de 2 letras (ex.: IT).")
        if resultado["erros"]:
            return resultado

        # 1. Árvore B
        cliente = self.clientes.consultar(cliente_id)
        metricas_arvore = self.clientes.metricas()
        resultado["cliente"] = cliente
        resultado["busca_arvore"] = {
            "chave": cliente_id,
            "nos_visitados": metricas_arvore["nos_visitados_ultima_busca"],
            "comparacoes": metricas_arvore["comparacoes_ultima_busca"],
            "altura": metricas_arvore["altura"],
        }

        # 2. Tabela Hash
        pais = self.paises.consultar(destino)
        resultado["pais"] = pais
        resultado["busca_hash"] = {
            "chave": destino,
            "comparacoes": self.paises.metricas()["comparacoes_ultima_busca"],
        }

        if cliente is None:
            resultado["erros"].append(f"Cliente {cliente_id} não encontrado.")
        if pais is None:
            resultado["erros"].append(f"Destino {destino} não é atendido pela GlobalSIM.")

        # 3. Pacote
        if cliente is not None:
            if cliente.get("status") != "ativo":
                resultado["avisos"].append(
                    f"Cliente está {cliente.get('status')}: o serviço não pode ser usado."
                )
            if not cliente.get("esim"):
                resultado["avisos"].append("Cliente ainda não tem eSIM associado.")

            if cliente.get("pacote") is None:
                resultado["avisos"].append("Cliente não tem pacote associado.")
            else:
                pacote = self.pacotes.buscar(cliente["pacote"])
                resultado["pacote"] = pacote
                if pacote is not None and pais is not None:
                    cobre = self.pacotes.cobre(pacote, pais)
                    resultado["pacote_cobre_destino"] = cobre
                    if not cobre:
                        resultado["avisos"].append(
                            f"O pacote {pacote['nome']} não cobre a região {pais['regiao']}."
                        )

        resultado["pode_conectar"] = (
            not resultado["erros"] and not resultado["avisos"]
        )
        return resultado
