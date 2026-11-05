"""
GlobalSIM - Etapa 1 (Tabela Hash) + Etapa 2 (Árvore B)

Este arquivo só contém as rotas. A lógica fica em servicos/ e as
estruturas de dados em estruturas/.
"""
from flask import Flask, flash, redirect, render_template, request, url_for

import config
from servicos.clientes_service import STATUS_VALIDOS, ClientesService
from servicos.consulta import ConsultaIntegrada
from servicos.pacotes_service import PacotesService
from servicos.paises_service import PaisesService


def criar_app(caminho_paises=None, caminho_clientes=None, caminho_pacotes=None):
    app = Flask(__name__)
    app.secret_key = "globalsim-ed2-chave-de-desenvolvimento"

    paises = PaisesService(caminho_paises or config.CAMINHO_PAISES)
    pacotes = PacotesService(caminho_pacotes or config.CAMINHO_PACOTES)
    clientes = ClientesService(
        caminho_clientes or config.CAMINHO_CLIENTES,
        pacotes,
        grau_minimo=config.GRAU_MINIMO_ARVORE_B,
    )
    consulta = ConsultaIntegrada(clientes, paises, pacotes)

    # ---------- página inicial ----------
    @app.route("/")
    def index():
        return render_template(
            "index.html",
            total=paises.tabela.tamanho(),
            total_clientes=clientes.total(),
        )

    # ---------- listagem ----------
    @app.route("/paises")
    def listar_paises():
        return render_template(
            "paises.html", paises=paises.listar(), metricas=paises.metricas()
        )

    # ---------- cadastro ----------
    @app.route("/paises/novo", methods=["GET", "POST"])
    def cadastrar_pais():
        if request.method == "POST":
            ok, mensagem = paises.cadastrar(request.form)
            if ok:
                flash(mensagem, "sucesso")
                return redirect(url_for("listar_paises"))
            flash(mensagem, "erro")
            # reexibe o formulário com o que foi digitado
            return render_template(
                "pais_form.html", pais=request.form, editando=False
            )
        return render_template("pais_form.html", pais={}, editando=False)

    # ---------- alteração ----------
    @app.route("/paises/<codigo>/editar", methods=["GET", "POST"])
    def editar_pais(codigo):
        pais = paises.consultar(codigo)
        if pais is None:
            flash(f"País {codigo.upper()} não encontrado.", "erro")
            return redirect(url_for("listar_paises"))

        if request.method == "POST":
            ok, mensagem = paises.alterar(codigo, request.form)
            if ok:
                flash(mensagem, "sucesso")
                return redirect(url_for("listar_paises"))
            flash(mensagem, "erro")
            return render_template(
                "pais_form.html",
                pais={**request.form, "codigo": pais["codigo"]},
                editando=True,
            )
        return render_template("pais_form.html", pais=pais, editando=True)

    # ---------- remoção (só POST) ----------
    @app.route("/paises/<codigo>/remover", methods=["POST"])
    def remover_pais(codigo):
        ok, mensagem = paises.remover(codigo)
        flash(mensagem, "sucesso" if ok else "erro")
        return redirect(url_for("listar_paises"))

    # ---------- consulta de cobertura ----------
    @app.route("/cobertura")
    def cobertura():
        codigo = request.args.get("codigo", "").strip()
        pais = None
        consultou = bool(codigo)
        if consultou:
            pais = paises.consultar(codigo)
        return render_template(
            "cobertura.html", codigo=codigo, pais=pais, consultou=consultou
        )

    # ---------- clientes: listagem paginada (percurso em ordem da Árvore B) ----------
    @app.route("/clientes")
    def listar_clientes():
        pagina = request.args.get("pagina", "1")
        pagina = int(pagina) if pagina.isdigit() else 1
        resultado = clientes.listar_pagina(pagina, config.CLIENTES_POR_PAGINA)
        return render_template(
            "clientes.html",
            **resultado,
            pacotes=pacotes,
            metricas=clientes.metricas(),
        )

    # ---------- clientes: busca por ID (formulário da listagem) ----------
    @app.route("/clientes/buscar")
    def buscar_cliente():
        cliente_id = request.args.get("id", "").strip()
        if clientes.converter_id(cliente_id) is None:
            flash("Informe um ID numérico para buscar.", "erro")
            return redirect(url_for("listar_clientes"))
        return redirect(url_for("detalhar_cliente", cliente_id=cliente_id))

    # ---------- clientes: cadastro ----------
    @app.route("/clientes/novo", methods=["GET", "POST"])
    def cadastrar_cliente():
        if request.method == "POST":
            ok, mensagem, cliente_id = clientes.cadastrar(request.form)
            if ok:
                flash(mensagem, "sucesso")
                return redirect(url_for("detalhar_cliente", cliente_id=cliente_id))
            flash(mensagem, "erro")
            return render_template(
                "cliente_form.html", cliente=request.form, editando=False,
                pacotes=pacotes.listar(), status_validos=STATUS_VALIDOS,
            )
        return render_template(
            "cliente_form.html", cliente={}, editando=False,
            pacotes=pacotes.listar(), status_validos=STATUS_VALIDOS,
        )

    # ---------- clientes: consulta por ID (busca na Árvore B) ----------
    @app.route("/clientes/<cliente_id>")
    def detalhar_cliente(cliente_id):
        cliente = clientes.consultar(cliente_id)
        if cliente is None:
            flash(f"Cliente {cliente_id} não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))
        pacote = None
        if cliente.get("pacote") is not None:
            pacote = pacotes.buscar(cliente["pacote"])
        return render_template(
            "cliente_detalhe.html",
            cliente=cliente,
            pacote=pacote,
            arvore=clientes.estatisticas(),
        )

    # ---------- clientes: alteração ----------
    @app.route("/clientes/<cliente_id>/editar", methods=["GET", "POST"])
    def editar_cliente(cliente_id):
        cliente = clientes.consultar(cliente_id)
        if cliente is None:
            flash(f"Cliente {cliente_id} não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))

        if request.method == "POST":
            ok, mensagem = clientes.alterar(cliente_id, request.form)
            if ok:
                flash(mensagem, "sucesso")
                return redirect(url_for("detalhar_cliente", cliente_id=cliente["id"]))
            flash(mensagem, "erro")
            return render_template(
                "cliente_form.html",
                cliente={**request.form, "id": cliente["id"]},
                editando=True, pacotes=pacotes.listar(), status_validos=STATUS_VALIDOS,
            )
        return render_template(
            "cliente_form.html", cliente=cliente, editando=True,
            pacotes=pacotes.listar(), status_validos=STATUS_VALIDOS,
        )

    # ---------- clientes: associação de eSIM e pacote ----------
    @app.route("/clientes/<cliente_id>/esim", methods=["GET", "POST"])
    def associar_esim(cliente_id):
        cliente = clientes.consultar(cliente_id)
        if cliente is None:
            flash(f"Cliente {cliente_id} não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))

        if request.method == "POST":
            ok, mensagem = clientes.associar_esim(cliente_id, request.form)
            if ok:
                flash(mensagem, "sucesso")
                return redirect(url_for("detalhar_cliente", cliente_id=cliente["id"]))
            flash(mensagem, "erro")
            return render_template(
                "cliente_esim.html", cliente=cliente, pacotes=pacotes.listar(),
                esim=request.form.get("esim", ""), pacote=request.form.get("pacote", ""),
            )
        return render_template(
            "cliente_esim.html", cliente=cliente, pacotes=pacotes.listar(),
            esim=cliente.get("esim") or "", pacote=str(cliente.get("pacote") or ""),
        )

    # ---------- consulta integrada cliente × destino ----------
    @app.route("/consulta")
    def consulta_integrada():
        cliente_id = request.args.get("cliente", "").strip()
        destino = request.args.get("destino", "").strip()
        resultado = None
        if cliente_id or destino:
            resultado = consulta.executar(cliente_id, destino)
        return render_template(
            "consulta.html", cliente_id=cliente_id, destino=destino.upper(),
            resultado=resultado,
        )

    # ---------- instrumentação das estruturas ----------
    @app.route("/metricas")
    def exibir_metricas():
        return render_template(
            "metricas.html",
            metricas=paises.metricas(),
            arvore=clientes.estatisticas(),
        )

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(debug=True)
