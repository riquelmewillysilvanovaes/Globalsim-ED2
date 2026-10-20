"""
GlobalSIM - Etapa 1 (Flask + Tabela Hash)

Este arquivo só contém as rotas. A lógica fica em servicos/ e as
estruturas de dados em estruturas/.
"""
import os

from flask import Flask, flash, redirect, render_template, request, url_for

from servicos.paises_service import PaisesService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def criar_app(caminho_paises=None):
    app = Flask(__name__)
    app.secret_key = "globalsim-ed2-chave-de-desenvolvimento"

    caminho = caminho_paises or os.path.join(BASE_DIR, "arquivos", "paises.json")
    paises = PaisesService(caminho)

    # ---------- página inicial ----------
    @app.route("/")
    def index():
        return render_template("index.html", total=paises.tabela.tamanho())

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

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(debug=True)
