"""
Camada de serviço dos clientes e eSIMs.

Aqui fica a validação, a regra de negócio e a persistência em JSON. As rotas
Flask (app.py) só chamam estes métodos, e a busca/inserção/listagem de fato é
feita pela ArvoreB (estruturas/arvore_b.py), indexada pelo ID do cliente.

Fluxo: JSON -> carrega na ArvoreB -> operações -> salva a ArvoreB no JSON.
"""
import random

from estruturas.arvore_b import ArvoreB, GRAU_MINIMO_PADRAO
from servicos.persistencia import carregar_json, salvar_json

STATUS_VALIDOS = ("ativo", "inativo", "suspenso")
PREFIXO_ESIM = "ESIM-"
SEED_CARGA = 42


class ClientesService:
    def __init__(self, caminho_json, pacotes, grau_minimo=GRAU_MINIMO_PADRAO):
        self.caminho_json = caminho_json
        self.pacotes = pacotes
        self.arvore = ArvoreB(grau_minimo)
        self.carregar()

    # ---------- persistência ----------
    def carregar(self):
        """Lê o JSON e insere cada cliente na Árvore B.

        O JSON é salvo em ordem de ID (fica legível), mas inserir chaves já
        ordenadas é o pior caso da Árvore B com split proativo: cada split
        deixa o nó da esquerda com t-1 chaves e ele nunca mais recebe nenhuma.
        Com os 1.000 clientes, a carga ordenada dá 6 níveis, 497 nós e 40% de
        ocupação; a carga embaralhada dá 5 níveis, ~320 nós e ~63%.
        Por isso embaralhamos a ordem de inserção com seed fixa: a árvore fica
        boa e sai igual em toda execução (instrumentação reproduzível).
        """
        registros = carregar_json(self.caminho_json, padrao=[])
        random.Random(SEED_CARGA).shuffle(registros)
        for registro in registros:
            self.arvore.inserir(registro["id"], registro)

    def salvar(self):
        """Grava no JSON os clientes da Árvore B, em ordem de ID (percurso em ordem)."""
        salvar_json(self.caminho_json, self.arvore.percorrer_em_ordem())

    # ---------- validação ----------
    @staticmethod
    def converter_id(valor):
        """'58372' -> 58372. None se não for um inteiro positivo."""
        texto = str(valor if valor is not None else "").strip()
        if not texto.isdigit():
            return None
        numero = int(texto)
        if numero <= 0:
            return None
        return numero

    @staticmethod
    def normalizar_esim(valor):
        """' esim-83921 ' -> 'ESIM-83921'. Também aceita só os números ('83921')."""
        texto = (valor or "").strip().upper()
        if texto.isdigit():
            texto = PREFIXO_ESIM + texto
        return texto

    @staticmethod
    def esim_valido(esim):
        """Formato ESIM-NNNNN (5 dígitos)."""
        numero = esim[len(PREFIXO_ESIM):]
        return esim.startswith(PREFIXO_ESIM) and len(numero) == 5 and numero.isdigit()

    @staticmethod
    def _validar_dados_pessoais(nome, email, status):
        if not nome:
            return "O campo 'nome' é obrigatório."
        if not email:
            return "O campo 'email' é obrigatório."
        partes = email.split("@")
        if len(partes) != 2 or not partes[0] or "." not in partes[1]:
            return "E-mail inválido (ex.: maria@email.com)."
        if status not in STATUS_VALIDOS:
            return "Status deve ser ativo, inativo ou suspenso."
        return None

    def _validar_associacao(self, esim_texto, pacote_texto, obrigatorio):
        """Valida eSIM e pacote. Retorna (erro, esim, pacote).

        No cadastro os dois são opcionais (cliente ainda sem eSIM); na
        associação são obrigatórios.
        """
        esim = self.normalizar_esim(esim_texto)
        pacote_texto = (pacote_texto or "").strip()

        if obrigatorio and (not esim or not pacote_texto):
            return "Informe o eSIM e o pacote.", None, None

        if esim and not self.esim_valido(esim):
            return "eSIM deve ter o formato ESIM-NNNNN (ex.: ESIM-83921).", None, None

        pacote = None
        if pacote_texto:
            pacote = self.converter_id(pacote_texto)
            if pacote is None or self.pacotes.buscar(pacote) is None:
                return f"Pacote {pacote_texto} não existe.", None, None

        return None, (esim or None), pacote

    # ---------- operações ----------
    def cadastrar(self, dados):
        """Retorna (ok, mensagem, id)."""
        cliente_id = self.converter_id(dados.get("id"))
        if cliente_id is None:
            return False, "O ID deve ser um número inteiro positivo.", None

        nome = (dados.get("nome") or "").strip()
        email = (dados.get("email") or "").strip().lower()
        status = (dados.get("status") or "ativo").strip().lower()
        erro = self._validar_dados_pessoais(nome, email, status)
        if erro:
            return False, erro, None

        erro, esim, pacote = self._validar_associacao(
            dados.get("esim"), dados.get("pacote"), obrigatorio=False
        )
        if erro:
            return False, erro, None

        cliente = {
            "id": cliente_id,
            "nome": nome,
            "email": email,
            "esim": esim,
            "pacote": pacote,
            "status": status,
        }
        if not self.arvore.inserir(cliente_id, cliente):
            return False, f"Já existe um cliente com o ID {cliente_id}.", None
        self.salvar()
        return True, f"Cliente {nome} (ID {cliente_id}) cadastrado com sucesso.", cliente_id

    def consultar(self, cliente_id):
        """Busca na Árvore B. Retorna o dict do cliente ou None."""
        numero = self.converter_id(cliente_id)
        if numero is None:
            return None
        return self.arvore.buscar(numero)

    def alterar(self, cliente_id, dados):
        """Altera nome, e-mail e status. O ID é a chave e não muda. Retorna (ok, mensagem)."""
        atual = self.consultar(cliente_id)
        if atual is None:
            return False, f"Cliente {cliente_id} não encontrado."

        nome = (dados.get("nome") or "").strip()
        email = (dados.get("email") or "").strip().lower()
        status = (dados.get("status") or "").strip().lower()
        erro = self._validar_dados_pessoais(nome, email, status)
        if erro:
            return False, erro

        novo = {**atual, "nome": nome, "email": email, "status": status}
        self.arvore.atualizar(atual["id"], novo)
        self.salvar()
        return True, f"Cliente {nome} atualizado com sucesso."

    def associar_esim(self, cliente_id, dados):
        """Associa (ou troca) o eSIM e o pacote do cliente. Retorna (ok, mensagem)."""
        atual = self.consultar(cliente_id)
        if atual is None:
            return False, f"Cliente {cliente_id} não encontrado."

        erro, esim, pacote = self._validar_associacao(
            dados.get("esim"), dados.get("pacote"), obrigatorio=True
        )
        if erro:
            return False, erro

        novo = {**atual, "esim": esim, "pacote": pacote}
        self.arvore.atualizar(atual["id"], novo)
        self.salvar()
        nome_pacote = self.pacotes.buscar(pacote)["nome"]
        return True, f"eSIM {esim} com pacote {nome_pacote} associado a {atual['nome']}."

    def listar_pagina(self, pagina, por_pagina):
        """Uma página da listagem, em ordem de ID (percurso em ordem da Árvore B)."""
        todos = self.arvore.percorrer_em_ordem()
        total = len(todos)
        total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
        pagina = min(max(1, pagina), total_paginas)
        inicio = (pagina - 1) * por_pagina
        return {
            "clientes": todos[inicio:inicio + por_pagina],
            "pagina": pagina,
            "total_paginas": total_paginas,
            "total": total,
        }

    def total(self):
        return self.arvore.tamanho()

    def metricas(self):
        return self.arvore.metricas()

    def estatisticas(self):
        return self.arvore.estatisticas()
