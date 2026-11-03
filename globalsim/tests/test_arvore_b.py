import json
import random

import pytest

from estruturas.arvore_b import ArvoreB, NoB
from servicos.clientes_service import ClientesService
from servicos.pacotes_service import PacotesService


def cliente(cliente_id, nome="Teste", pacote=102, status="ativo"):
    return {
        "id": cliente_id,
        "nome": nome,
        "email": f"c{cliente_id}@email.com",
        "esim": f"ESIM-{cliente_id % 100000:05d}",
        "pacote": pacote,
        "status": status,
    }


def chaves_aleatorias(quantidade, seed=42):
    return random.Random(seed).sample(range(10000, 100000), quantidade)


# ---------- verificação das propriedades da Árvore B ----------
def profundidades_das_folhas(no, profundidade, resultado):
    if no.folha:
        resultado.append(profundidade)
        return
    for filho in no.filhos:
        profundidades_das_folhas(filho, profundidade + 1, resultado)


def verificar_nos(arvore, no, eh_raiz, minimo, maximo):
    """Confere ocupação, ordem das chaves e separação entre os filhos de cada nó."""
    t = arvore.t
    assert len(no.chaves) <= 2 * t - 1
    if not eh_raiz:
        assert len(no.chaves) >= t - 1
    assert len(no.chaves) == len(no.valores)
    assert no.chaves == sorted(no.chaves)
    for chave in no.chaves:
        assert (minimo is None or chave > minimo) and (maximo is None or chave < maximo)

    if no.folha:
        assert no.filhos == []
        return
    assert len(no.filhos) == len(no.chaves) + 1
    for i, filho in enumerate(no.filhos):
        limite_inferior = no.chaves[i - 1] if i > 0 else minimo
        limite_superior = no.chaves[i] if i < len(no.chaves) else maximo
        verificar_nos(arvore, filho, False, limite_inferior, limite_superior)


def verificar_arvore(arvore):
    profundidades = []
    profundidades_das_folhas(arvore.raiz, 1, profundidades)
    assert len(set(profundidades)) == 1, "todas as folhas devem estar no mesmo nível"
    assert profundidades[0] == arvore.altura()
    verificar_nos(arvore, arvore.raiz, True, None, None)


def contar_nos(no):
    total = 1
    for filho in no.filhos:
        total += contar_nos(filho)
    return total


# ---------- estrutura ----------
def test_arvore_vazia():
    arvore = ArvoreB()
    assert arvore.tamanho() == 0
    assert arvore.buscar(123) is None
    assert arvore.percorrer_em_ordem() == []
    assert arvore.altura() == 1


def test_grau_minimo_invalido():
    with pytest.raises(ValueError):
        ArvoreB(t=1)


def test_inserir_e_buscar():
    arvore = ArvoreB()
    assert arvore.inserir(58372, cliente(58372, "Maria Silva"))
    assert arvore.buscar(58372)["nome"] == "Maria Silva"
    assert 58372 in arvore
    assert 1 not in arvore
    assert len(arvore) == 1


def test_duplicata_rejeitada_preserva_original():
    arvore = ArvoreB()
    for chave in chaves_aleatorias(50):
        arvore.inserir(chave, cliente(chave))
    alvo = chaves_aleatorias(50)[17]
    assert not arvore.inserir(alvo, cliente(alvo, "Outro"))
    assert arvore.buscar(alvo)["nome"] == "Teste"
    assert arvore.tamanho() == 50


def test_split_da_raiz_com_t2():
    # t=2: nó cheio com 3 chaves. A 4ª inserção divide a raiz e a mediana sobe.
    arvore = ArvoreB(t=2)
    for chave in [10, 20, 30]:
        arvore.inserir(chave, cliente(chave))
    assert arvore.metricas()["splits"] == 0
    assert arvore.altura() == 1

    arvore.inserir(40, cliente(40))
    assert arvore.raiz.chaves == [20]
    assert arvore.raiz.filhos[0].chaves == [10]
    assert arvore.raiz.filhos[1].chaves == [30, 40]
    metricas = arvore.metricas()
    assert metricas["splits"] == 1
    assert metricas["altura"] == 2
    assert metricas["total_nos"] == 3


def test_split_de_filho_interno():
    arvore = ArvoreB(t=2)
    for chave in [10, 20, 30, 40, 50]:
        arvore.inserir(chave, cliente(chave))
    # [20] -> [10] [30 40 50]; inserir 60 divide o filho cheio antes de descer
    arvore.inserir(60, cliente(60))
    assert arvore.raiz.chaves == [20, 40]
    assert arvore.raiz.filhos[2].chaves == [50, 60]
    verificar_arvore(arvore)


def test_mil_chaves_aleatorias():
    arvore = ArvoreB(t=3)
    chaves = chaves_aleatorias(1000)
    for chave in chaves:
        assert arvore.inserir(chave, cliente(chave))

    assert arvore.tamanho() == 1000
    for chave in chaves:
        assert arvore.buscar(chave)["id"] == chave
    assert arvore.buscar(5) is None  # menor que todas
    assert arvore.buscar(999999) is None  # maior que todas

    verificar_arvore(arvore)


def test_percurso_em_ordem_sai_ordenado():
    arvore = ArvoreB(t=3)
    chaves = chaves_aleatorias(1000)
    for chave in chaves:
        arvore.inserir(chave, cliente(chave))
    ids = [c["id"] for c in arvore.percorrer_em_ordem()]
    assert ids == sorted(chaves)


@pytest.mark.parametrize("t", [2, 3, 4, 5])
def test_propriedades_para_varios_graus(t):
    arvore = ArvoreB(t=t)
    for chave in chaves_aleatorias(500, seed=t):
        arvore.inserir(chave, cliente(chave))
    verificar_arvore(arvore)
    # o contador incremental de nós tem que bater com a contagem real
    assert arvore.metricas()["total_nos"] == contar_nos(arvore.raiz)


def test_insercao_ordenada_tambem_fica_valida():
    arvore = ArvoreB(t=3)
    for chave in range(1, 1001):
        arvore.inserir(chave, cliente(chave))
    verificar_arvore(arvore)
    assert [c["id"] for c in arvore.percorrer_em_ordem()] == list(range(1, 1001))


def test_atualizar():
    arvore = ArvoreB()
    for chave in chaves_aleatorias(100):
        arvore.inserir(chave, cliente(chave))
    alvo = chaves_aleatorias(100)[42]
    assert arvore.atualizar(alvo, cliente(alvo, "Novo Nome"))
    assert arvore.buscar(alvo)["nome"] == "Novo Nome"
    assert not arvore.atualizar(1, cliente(1))
    assert arvore.tamanho() == 100


def test_instrumentacao_da_busca():
    arvore = ArvoreB(t=3)
    chaves = chaves_aleatorias(1000)
    for chave in chaves:
        arvore.inserir(chave, cliente(chave))

    raiz = arvore.raiz.chaves[0]
    arvore.buscar(raiz)
    metricas = arvore.metricas()
    assert metricas["chave_ultima_busca"] == raiz
    assert metricas["nos_visitados_ultima_busca"] == 1
    assert metricas["comparacoes_ultima_busca"] == 1

    # busca que não acha percorre a altura inteira (raiz até uma folha)
    arvore.buscar(1)
    metricas = arvore.metricas()
    assert metricas["nos_visitados_ultima_busca"] == arvore.altura()
    caminho = arvore.estatisticas()["caminho_ultima_busca"]
    assert len(caminho) == arvore.altura()
    assert caminho[-1]["folha"]
    assert all(passo["indice_encontrado"] is None for passo in caminho)

    # inserir/atualizar não sobrescrevem a medição da última busca
    arvore.inserir(1, cliente(1))
    arvore.atualizar(chaves[0], cliente(chaves[0]))
    assert arvore.metricas()["chave_ultima_busca"] == 1


def test_estatisticas_niveis():
    arvore = ArvoreB(t=3)
    for chave in chaves_aleatorias(1000):
        arvore.inserir(chave, cliente(chave))
    estatisticas = arvore.estatisticas(niveis_exibidos=3)
    assert len(estatisticas["nos_por_nivel"]) == arvore.altura()
    assert estatisticas["nos_por_nivel"][0] == 1
    assert sum(estatisticas["nos_por_nivel"]) == estatisticas["total_nos"]
    assert len(estatisticas["niveis"]) == 3
    assert estatisticas["niveis"][0] == [arvore.raiz.chaves]
    assert 50 <= estatisticas["ocupacao_media"] <= 100


def test_no_cheio():
    no = NoB()
    no.chaves = [1, 2, 3, 4, 5]
    assert no.cheio(3)
    assert not no.cheio(4)


# ---------- serviço ----------
@pytest.fixture
def pacotes(tmp_path):
    registros = [
        {"codigo": 101, "nome": "Europa Basic", "dados_gb": 5, "validade_dias": 15, "cobertura": "Europa"},
        {"codigo": 102, "nome": "Europa Plus", "dados_gb": 10, "validade_dias": 30, "cobertura": "Europa"},
        {"codigo": 202, "nome": "América Plus", "dados_gb": 15, "validade_dias": 30, "cobertura": "América"},
        {"codigo": 301, "nome": "Global", "dados_gb": 20, "validade_dias": 30, "cobertura": "Global"},
    ]
    caminho = tmp_path / "pacotes.json"
    caminho.write_text(json.dumps(registros), encoding="utf-8")
    return PacotesService(str(caminho))


@pytest.fixture
def servico(tmp_path, pacotes):
    registros = [cliente(chave) for chave in chaves_aleatorias(300)]
    registros[0]["nome"] = "Maria Silva"
    caminho = tmp_path / "clientes.json"
    caminho.write_text(json.dumps(registros), encoding="utf-8")
    return ClientesService(str(caminho), pacotes)


def formulario(**campos):
    base = {"id": "58372", "nome": "Maria Silva", "email": "maria@email.com",
            "status": "ativo", "esim": "ESIM-83921", "pacote": "102"}
    base.update(campos)
    return base


def test_servico_carrega_clientes_na_arvore(servico):
    assert servico.total() == 300
    primeiro = chaves_aleatorias(300)[0]
    assert servico.consultar(str(primeiro))["nome"] == "Maria Silva"
    assert servico.consultar(f" {primeiro} ")["nome"] == "Maria Silva"
    assert servico.consultar("abc") is None
    assert servico.consultar("1") is None
    verificar_arvore(servico.arvore)


def test_servico_carga_e_reproduzivel(servico, pacotes):
    # mesma base -> mesma árvore em toda execução (instrumentação reproduzível)
    outro = ClientesService(servico.caminho_json, pacotes)
    assert outro.metricas()["splits"] == servico.metricas()["splits"]
    assert outro.arvore.raiz.chaves == servico.arvore.raiz.chaves


def test_servico_cadastrar_persiste(servico, pacotes):
    ok, _, cliente_id = servico.cadastrar(formulario(esim="esim-83921"))
    assert ok and cliente_id == 58372
    ok, mensagem, _ = servico.cadastrar(formulario())
    assert not ok and "Já existe" in mensagem

    recarregado = ClientesService(servico.caminho_json, pacotes)
    assert recarregado.total() == 301
    novo = recarregado.consultar(58372)
    assert novo["esim"] == "ESIM-83921"
    assert novo["pacote"] == 102

    # o JSON é gravado em ordem de ID (percurso em ordem)
    with open(servico.caminho_json, encoding="utf-8") as f:
        ids = [c["id"] for c in json.load(f)]
    assert ids == sorted(ids)


def test_servico_cadastrar_sem_esim(servico):
    ok, _, _ = servico.cadastrar(formulario(esim="", pacote=""))
    assert ok
    novo = servico.consultar(58372)
    assert novo["esim"] is None and novo["pacote"] is None


@pytest.mark.parametrize("campos, trecho", [
    ({"id": "abc"}, "ID"),
    ({"id": "0"}, "ID"),
    ({"id": "-5"}, "ID"),
    ({"nome": "  "}, "nome"),
    ({"email": "sem-arroba"}, "E-mail"),
    ({"status": "banido"}, "Status"),
    ({"esim": "ESIM-12"}, "ESIM-NNNNN"),
    ({"pacote": "999"}, "Pacote"),
])
def test_servico_validacao(servico, campos, trecho):
    ok, mensagem, _ = servico.cadastrar(formulario(**campos))
    assert not ok
    assert trecho in mensagem
    assert servico.total() == 300


def test_servico_alterar(servico, pacotes):
    alvo = chaves_aleatorias(300)[5]
    ok, _ = servico.alterar(str(alvo), {"nome": "Novo", "email": "novo@email.com", "status": "suspenso"})
    assert ok
    recarregado = ClientesService(servico.caminho_json, pacotes)
    alterado = recarregado.consultar(alvo)
    assert alterado["nome"] == "Novo"
    assert alterado["status"] == "suspenso"
    assert alterado["id"] == alvo
    assert alterado["esim"] == cliente(alvo)["esim"]  # alterar não mexe no eSIM

    ok, _ = servico.alterar("1", {"nome": "X", "email": "x@email.com", "status": "ativo"})
    assert not ok


def test_servico_associar_esim(servico, pacotes):
    alvo = chaves_aleatorias(300)[7]
    ok, _ = servico.associar_esim(alvo, {"esim": "12345", "pacote": "301"})
    assert ok
    alterado = ClientesService(servico.caminho_json, pacotes).consultar(alvo)
    assert alterado["esim"] == "ESIM-12345"
    assert alterado["pacote"] == 301

    ok, mensagem = servico.associar_esim(alvo, {"esim": "", "pacote": "301"})
    assert not ok
    ok, mensagem = servico.associar_esim(alvo, {"esim": "ESIM-12345", "pacote": "555"})
    assert not ok and "555" in mensagem


def test_servico_paginacao(servico):
    pagina = servico.listar_pagina(1, 25)
    assert pagina["total"] == 300
    assert pagina["total_paginas"] == 12
    assert len(pagina["clientes"]) == 25
    ultima = servico.listar_pagina(99, 25)  # página fora do intervalo vai para a última
    assert ultima["pagina"] == 12
    ids = []
    for numero in range(1, 13):
        for c in servico.listar_pagina(numero, 25)["clientes"]:
            ids.append(c["id"])
    assert ids == sorted(chaves_aleatorias(300))


def test_pacote_cobre_regiao(pacotes):
    europa = pacotes.buscar(102)
    america = pacotes.buscar(202)
    global_ = pacotes.buscar(301)
    italia = {"regiao": "Europa"}
    brasil = {"regiao": "América do Sul"}
    argentina = {"regiao": "America do Sul"}  # sem acento também vale
    japao = {"regiao": "Ásia"}
    assert pacotes.cobre(europa, italia)
    assert not pacotes.cobre(europa, brasil)
    assert pacotes.cobre(america, brasil)
    assert pacotes.cobre(america, argentina)
    assert not pacotes.cobre(america, japao)
    assert pacotes.cobre(global_, japao)
    assert pacotes.buscar(999) is None
