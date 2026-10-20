# Interface da Tabela Hash (para quem implementa `estruturas/tabela_hash.py`)

O Flask já está pronto e chama a Tabela Hash por estes métodos. Basta substituir
o arquivo `estruturas/tabela_hash.py` mantendo a classe `TabelaHash` e as
assinaturas abaixo. Não é preciso mexer em `app.py` nem em `servicos/`.

| Método | Retorno | O que faz |
|---|---|---|
| `__init__(self, capacidade=7)` | – | Cria a tabela vazia (capacidade arredondada para o próximo primo) |
| `inserir(self, chave, valor)` | `bool` | Insere. `True` se inseriu, `False` se a chave já existe (não sobrescreve) |
| `buscar(self, chave)` | `dict` ou `None` | Devolve o registro do país, ou `None` se não existir |
| `atualizar(self, chave, valor)` | `bool` | Troca o registro da chave. `True` se atualizou, `False` se a chave não existe |
| `remover(self, chave)` | `bool` | Remove. `True` se removeu, `False` se a chave não existe |
| `listar(self)` | `list[dict]` | Todos os registros (a ordem não importa, o serviço ordena) |
| `tamanho(self)` | `int` | Quantidade de países armazenados |
| `metricas(self)` | `dict` | Dados de instrumentação exibidos na tela de países (só valores simples) |
| `estatisticas(self)` | `dict` | `metricas()` + `mapa_buckets` (lista de `{indice, chaves}`) para a página `/instrumentacao` |
| `itens(self)` | `list[tuple]` | Pares `(chave, valor)` na ordem dos buckets |
| `__len__`, `__contains__` | – | `len(tabela)` e `"IT" in tabela` |

## Detalhes importantes

- **Chave:** string de 2 letras maiúsculas (ex.: `"IT"`). O serviço já normaliza antes de chamar.
- **Valor:** o dict completo do país:
  `{"codigo": "IT", "pais": "Itália", "regiao": "Europa", "operadora": "Operadora IT", "tecnologia": "5G"}`
- **`metricas()`:** devolve `tamanho`, `capacidade`, `fator_carga`, `colisoes` (chaves que hoje
  dividem bucket), `colisoes_acumuladas` (inserções em bucket ocupado desde o início),
  `maior_bucket`, `buckets_usados`, `rehashes` e `comparacoes_ultima_busca`.
- **Implementação:** encadeamento separado, hash polinomial própria
  (`h = (h * 31 + ord(c)) % capacidade`) e rehash para o próximo primo ≥ 2× a capacidade
  quando o fator de carga passa de 0,75. Detalhes em `estruturas/tabela_hash.py`.
