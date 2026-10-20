import json

import pytest

from estruturas.tabela_hash import TabelaHash, _eh_primo
from servicos.paises_service import PaisesService


def pais(codigo, nome="Teste"):
    return {
        "codigo": codigo,
        "pais": nome,
        "regiao": "Regiao",
        "operadora": f"Operadora {codigo}",
        "tecnologia": "5G",
    }


def codigos_de_duas_letras():
    codigos = []
    for a in range(ord("A"), ord("Z") + 1):
        for b in range(ord("A"), ord("Z") + 1):
            codigos.append(chr(a) + chr(b))
    return codigos


def test_inserir_e_buscar():
    tabela = TabelaHash()
    assert tabela.inserir("BR", pais("BR", "Brasil"))
    assert tabela.buscar("BR")["pais"] == "Brasil"
    assert tabela.tamanho() == 1
    assert len(tabela) == 1
    assert "BR" in tabela


def test_buscar_inexistente():
    tabela = TabelaHash()
    tabela.inserir("BR", pais("BR"))
    assert tabela.buscar("XX") is None
    assert "XX" not in tabela


def test_duplicata_rejeitada_preserva_original():
    tabela = TabelaHash()
    assert tabela.inserir("IT", pais("IT", "Itália"))
    assert not tabela.inserir("IT", pais("IT", "Outro"))
    assert tabela.buscar("IT")["pais"] == "Itália"
    assert tabela.tamanho() == 1


def test_atualizar():
    tabela = TabelaHash()
    tabela.inserir("JP", pais("JP", "Japão"))
    assert tabela.atualizar("JP", pais("JP", "Japão (novo)"))
    assert tabela.buscar("JP")["pais"] == "Japão (novo)"
    assert not tabela.atualizar("XX", pais("XX"))
    assert tabela.tamanho() == 1


def test_remover():
    tabela = TabelaHash()
    tabela.inserir("FR", pais("FR"))
    tabela.inserir("ES", pais("ES"))
    assert tabela.remover("FR")
    assert tabela.buscar("FR") is None
    assert tabela.buscar("ES") is not None
    assert not tabela.remover("FR")
    assert tabela.tamanho() == 1


def test_hash_deterministica_e_dentro_da_capacidade():
    a = TabelaHash(capacidade=7)
    b = TabelaHash(capacidade=7)
    for codigo in codigos_de_duas_letras():
        assert a._hash(codigo) == b._hash(codigo)
        assert 0 <= a._hash(codigo) < 7


def test_colisao_forcada():
    tabela = TabelaHash(capacidade=7)
    # procura duas chaves que caem no mesmo bucket
    alvo = tabela._hash("BR")
    outra = None
    for codigo in codigos_de_duas_letras():
        if codigo != "BR" and tabela._hash(codigo) == alvo:
            outra = codigo
            break
    assert outra is not None

    tabela.inserir("BR", pais("BR", "Brasil"))
    tabela.inserir(outra, pais(outra, "Colidiu"))

    metricas = tabela.metricas()
    assert metricas["colisoes"] == 1
    assert metricas["colisoes_acumuladas"] == 1
    assert metricas["maior_bucket"] == 2

    assert tabela.buscar("BR")["pais"] == "Brasil"
    assert tabela.metricas()["comparacoes_ultima_busca"] == 1
    assert tabela.buscar(outra)["pais"] == "Colidiu"
    assert tabela.metricas()["comparacoes_ultima_busca"] == 2

    # remover a primeira da cadeia não pode perder a segunda
    assert tabela.remover("BR")
    assert tabela.buscar(outra)["pais"] == "Colidiu"


def test_rehash_preserva_todos_os_itens():
    tabela = TabelaHash(capacidade=7)
    codigos = codigos_de_duas_letras()[:200]
    for codigo in codigos:
        assert tabela.inserir(codigo, pais(codigo))

    metricas = tabela.metricas()
    assert metricas["rehashes"] > 0
    assert _eh_primo(metricas["capacidade"])
    assert metricas["fator_carga"] <= 0.75
    assert tabela.tamanho() == len(codigos)
    for codigo in codigos:
        assert tabela.buscar(codigo)["codigo"] == codigo


def test_rehash_acontece_ao_passar_de_075():
    tabela = TabelaHash(capacidade=7)
    for codigo in ["BR", "PT", "ES", "FR", "IT"]:  # 5/7 = 0,71
        tabela.inserir(codigo, pais(codigo))
    assert tabela.metricas()["rehashes"] == 0
    tabela.inserir("US", pais("US"))  # 6/7 = 0,86 -> rehash para 17
    assert tabela.metricas()["rehashes"] == 1
    assert tabela.metricas()["capacidade"] == 17


def test_listar_itens_e_estatisticas():
    tabela = TabelaHash()
    for codigo in ["BR", "PT", "IT"]:
        tabela.inserir(codigo, pais(codigo))

    codigos_listados = sorted(p["codigo"] for p in tabela.listar())
    assert codigos_listados == ["BR", "IT", "PT"]
    assert sorted(chave for chave, _ in tabela.itens()) == ["BR", "IT", "PT"]

    estatisticas = tabela.estatisticas()
    mapa = estatisticas["mapa_buckets"]
    assert len(mapa) == estatisticas["capacidade"]
    chaves_no_mapa = sorted(c for bucket in mapa for c in bucket["chaves"])
    assert chaves_no_mapa == ["BR", "IT", "PT"]
    assert mapa[tabela._hash("IT")]["chaves"].count("IT") == 1


@pytest.fixture
def servico(tmp_path):
    # JSON próprio do teste: não depende do arquivos/paises.json, que muda com o uso
    registros = []
    for codigo in ["BR", "PT", "ES", "FR", "IT", "US", "CA", "JP"]:
        registros.append(pais(codigo))
    registros[4]["pais"] = "Itália"
    caminho = tmp_path / "paises.json"
    caminho.write_text(json.dumps(registros), encoding="utf-8")
    return PaisesService(str(caminho))


def test_servico_carrega_paises_na_hash(servico):
    assert servico.tabela.tamanho() == 8
    assert servico.consultar(" it ")["pais"] == "Itália"
    assert servico.consultar("XX") is None
    metricas = servico.metricas()
    assert metricas["capacidade"] == 17
    assert metricas["rehashes"] == 1


def test_servico_crud_persiste(servico):
    ok, _ = servico.cadastrar(pais("de", "Alemanha"))
    assert ok
    ok, _ = servico.cadastrar(pais("DE", "Alemanha"))
    assert not ok

    recarregado = PaisesService(servico.caminho_json)
    assert recarregado.consultar("DE")["pais"] == "Alemanha"

    ok, _ = recarregado.remover("DE")
    assert ok
    assert PaisesService(servico.caminho_json).consultar("DE") is None
