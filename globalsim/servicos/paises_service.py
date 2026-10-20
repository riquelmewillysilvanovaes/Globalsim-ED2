"""
Camada de serviço dos países atendidos.

Aqui fica a lógica de negócio e a persistência em JSON. As rotas Flask
(app.py) só chamam estes métodos, e a busca/inserção/remoção de fato é
feita pela TabelaHash (estruturas/tabela_hash.py).

Fluxo: JSON -> carrega na TabelaHash -> operações -> salva a TabelaHash no JSON.
"""
import json
import os

from estruturas.tabela_hash import TabelaHash

CAMPOS = ("codigo", "pais", "regiao", "operadora", "tecnologia")


class PaisesService:
    def __init__(self, caminho_json, tabela=None):
        self.caminho_json = caminho_json
        self.tabela = tabela if tabela is not None else TabelaHash()
        self.carregar()

    # ---------- persistência ----------
    def carregar(self):
        """Lê o JSON e insere cada país na Tabela Hash."""
        if not os.path.exists(self.caminho_json):
            return
        with open(self.caminho_json, "r", encoding="utf-8") as f:
            registros = json.load(f)
        for registro in registros:
            self.tabela.inserir(registro["codigo"], registro)

    def salvar(self):
        """Grava no JSON o conteúdo atual da Tabela Hash."""
        with open(self.caminho_json, "w", encoding="utf-8") as f:
            json.dump(self.listar(), f, ensure_ascii=False, indent=2)

    # ---------- validação ----------
    @staticmethod
    def normalizar(dados):
        """Limpa espaços e padroniza o código em maiúsculas."""
        limpo = {c: (dados.get(c) or "").strip() for c in CAMPOS}
        limpo["codigo"] = limpo["codigo"].upper()
        return limpo

    @staticmethod
    def validar(dados):
        """Devolve uma mensagem de erro, ou None se estiver tudo certo."""
        for campo in CAMPOS:
            if not dados[campo]:
                return f"O campo '{campo}' é obrigatório."
        codigo = dados["codigo"]
        if len(codigo) != 2 or not codigo.isalpha():
            return "O código deve ter exatamente 2 letras (ex.: BR, IT)."
        return None

    # ---------- operações ----------
    def cadastrar(self, dados):
        """Retorna (ok, mensagem)."""
        dados = self.normalizar(dados)
        erro = self.validar(dados)
        if erro:
            return False, erro
        if not self.tabela.inserir(dados["codigo"], dados):
            return False, f"Já existe um país com o código {dados['codigo']}."
        self.salvar()
        return True, f"País {dados['pais']} cadastrado com sucesso."

    def consultar(self, codigo):
        """Consulta de cobertura. Retorna o dict do país ou None."""
        return self.tabela.buscar((codigo or "").strip().upper())

    def alterar(self, codigo, dados):
        """O código é a chave e não muda. Retorna (ok, mensagem)."""
        codigo = codigo.strip().upper()
        dados = self.normalizar({**dados, "codigo": codigo})
        erro = self.validar(dados)
        if erro:
            return False, erro
        if not self.tabela.atualizar(codigo, dados):
            return False, f"País {codigo} não encontrado."
        self.salvar()
        return True, f"País {dados['pais']} atualizado com sucesso."

    def remover(self, codigo):
        """Retorna (ok, mensagem)."""
        codigo = codigo.strip().upper()
        if not self.tabela.remover(codigo):
            return False, f"País {codigo} não encontrado."
        self.salvar()
        return True, f"País {codigo} removido."

    def listar(self):
        return sorted(self.tabela.listar(), key=lambda p: p["codigo"])

    def metricas(self):
        return self.tabela.metricas()
