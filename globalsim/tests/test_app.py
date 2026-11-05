"""Testes das rotas Flask e da consulta integrada, com JSONs próprios (não mexe em arquivos/)."""
import json

import pytest

from app import criar_app


@pytest.fixture
def cliente_http(tmp_path):
    paises = [
        {"codigo": "IT", "pais": "Itália", "regiao": "Europa", "operadora": "Operadora IT", "tecnologia": "5G"},
        {"codigo": "JP", "pais": "Japão", "regiao": "Ásia", "operadora": "Operadora JP", "tecnologia": "5G"},
    ]
    pacotes = [
        {"codigo": 102, "nome": "Europa Plus", "dados_gb": 10, "validade_dias": 30, "cobertura": "Europa"},
        {"codigo": 301, "nome": "Global", "dados_gb": 20, "validade_dias": 30, "cobertura": "Global"},
    ]
    clientes = [
        {"id": 58372, "nome": "Maria Silva", "email": "maria@email.com",
         "esim": "ESIM-83921", "pacote": 102, "status": "ativo"},
        {"id": 11111, "nome": "João Inativo", "email": "joao@email.com",
         "esim": "ESIM-11111", "pacote": 301, "status": "inativo"},
    ]
    for nome, dados in [("paises", paises), ("pacotes", pacotes), ("clientes", clientes)]:
        (tmp_path / f"{nome}.json").write_text(json.dumps(dados), encoding="utf-8")

    app = criar_app(
        caminho_paises=str(tmp_path / "paises.json"),
        caminho_clientes=str(tmp_path / "clientes.json"),
        caminho_pacotes=str(tmp_path / "pacotes.json"),
    )
    app.testing = True
    return app.test_client()


def pagina(resposta):
    return resposta.get_data(as_text=True)


@pytest.mark.parametrize("url", [
    "/", "/paises", "/paises/novo", "/cobertura?codigo=IT", "/metricas",
    "/clientes", "/clientes?pagina=abc", "/clientes/novo", "/clientes/58372",
    "/clientes/58372/editar", "/clientes/58372/esim", "/consulta",
])
def test_paginas_abrem(cliente_http, url):
    assert cliente_http.get(url).status_code == 200


def test_detalhe_mostra_caminho_da_busca(cliente_http):
    html = pagina(cliente_http.get("/clientes/58372"))
    assert "Maria Silva" in html
    assert "buscar(58372)" in html
    assert "nós visitados" in html


def test_cliente_inexistente_redireciona(cliente_http):
    resposta = cliente_http.get("/clientes/99999", follow_redirects=True)
    assert "Cliente 99999 não encontrado" in pagina(resposta)


def test_buscar_por_id_redireciona(cliente_http):
    resposta = cliente_http.get("/clientes/buscar?id=58372")
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/clientes/58372")


def test_cadastro_segue_prg(cliente_http):
    resposta = cliente_http.post("/clientes/novo", data={
        "id": "22222", "nome": "Ana Costa", "email": "ana@email.com",
        "status": "ativo", "esim": "", "pacote": "",
    })
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/clientes/22222")
    html = pagina(cliente_http.get("/clientes/22222"))
    assert "Ana Costa" in html
    assert "cadastrado com sucesso" in html


def test_cadastro_invalido_reexibe_formulario(cliente_http):
    resposta = cliente_http.post("/clientes/novo", data={
        "id": "58372", "nome": "Duplicada", "email": "d@email.com", "status": "ativo",
    })
    assert resposta.status_code == 200
    html = pagina(resposta)
    assert "Já existe um cliente" in html
    assert "Duplicada" in html  # mantém o que foi digitado


def test_editar_e_associar_esim(cliente_http):
    resposta = cliente_http.post("/clientes/58372/editar", data={
        "nome": "Maria S. Silva", "email": "maria@email.com", "status": "suspenso",
    })
    assert resposta.status_code == 302
    resposta = cliente_http.post("/clientes/58372/esim", data={"esim": "ESIM-00001", "pacote": "301"})
    assert resposta.status_code == 302
    html = pagina(cliente_http.get("/clientes/58372"))
    assert "Maria S. Silva" in html and "ESIM-00001" in html and "Global" in html


def test_rotas_de_alteracao_nao_aceitam_get_para_alterar(cliente_http):
    # GET em editar/esim só mostra o formulário; nada muda
    cliente_http.get("/clientes/58372/editar?nome=Hacker")
    assert "Hacker" not in pagina(cliente_http.get("/clientes/58372"))


def test_consulta_integrada_ok(cliente_http):
    html = pagina(cliente_http.get("/consulta?cliente=58372&destino=it"))
    assert "buscar(58372)" in html
    assert 'buscar(&#34;IT&#34;)' in html or 'buscar("IT")' in html
    assert "Maria Silva" in html and "Itália" in html and "Europa Plus" in html
    assert "Serviço liberado" in html


def test_consulta_pacote_nao_cobre(cliente_http):
    html = pagina(cliente_http.get("/consulta?cliente=58372&destino=JP"))
    assert "não cobre a região" in html


def test_consulta_cliente_inativo(cliente_http):
    html = pagina(cliente_http.get("/consulta?cliente=11111&destino=JP"))
    assert "inativo" in html
    assert "Serviço com restrições" in html


def test_consulta_erros(cliente_http):
    assert "Cliente 99999 não encontrado" in pagina(cliente_http.get("/consulta?cliente=99999&destino=IT"))
    assert "não é atendido" in pagina(cliente_http.get("/consulta?cliente=58372&destino=XX"))
    assert "número inteiro" in pagina(cliente_http.get("/consulta?cliente=abc&destino=IT"))


def test_metricas_mostram_arvore_b(cliente_http):
    html = pagina(cliente_http.get("/metricas"))
    assert "Métricas da Tabela Hash" in html
    assert "Métricas da Árvore B" in html
    assert "Nós por nível" in html
