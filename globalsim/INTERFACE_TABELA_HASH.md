# Interface da Tabela Hash (para quem implementa `estruturas/tabela_hash.py`)

O Flask já está pronto e chama a Tabela Hash por estes métodos. Basta substituir
o arquivo `estruturas/tabela_hash.py` mantendo a classe `TabelaHash` e as
assinaturas abaixo. Não é preciso mexer em `app.py` nem em `servicos/`.

| Método | Retorno | O que faz |
|---|---|---|
| `__init__(self, capacidade=11)` | – | Cria a tabela vazia (capacidade inicial opcional) |
| `inserir(self, chave, valor)` | `bool` | Insere. `True` se inseriu, `False` se a chave já existe (não sobrescreve) |
| `buscar(self, chave)` | `dict` ou `None` | Devolve o registro do país, ou `None` se não existir |
| `atualizar(self, chave, valor)` | `bool` | Troca o registro da chave. `True` se atualizou, `False` se a chave não existe |
| `remover(self, chave)` | `bool` | Remove. `True` se removeu, `False` se a chave não existe |
| `listar(self)` | `list[dict]` | Todos os registros (a ordem não importa, o serviço ordena) |
| `tamanho(self)` | `int` | Quantidade de países armazenados |
| `metricas(self)` | `dict` | Dados de instrumentação exibidos na tela de países |

## Detalhes importantes

- **Chave:** string de 2 letras maiúsculas (ex.: `"IT"`). O serviço já normaliza antes de chamar.
- **Valor:** o dict completo do país:
  `{"codigo": "IT", "pais": "Itália", "regiao": "Europa", "operadora": "Operadora IT", "tecnologia": "5G"}`
- **`metricas()`:** deve devolver um dict. O template mostra todas as chaves que vierem,
  então podem acrescentar outras. Sugestão de chaves:
  `tamanho`, `capacidade`, `fator_carga`, `colisoes`, `maior_cadeia`, `buckets_usados`.
- **Proibido na versão final:** usar `dict` do Python como mecanismo principal de busca.
  Listas internas (buckets) são permitidas se fizerem parte da implementação da estrutura.
- **Sugestão:** implementar a função de hash, o tratamento de colisões (encadeamento ou
  endereçamento aberto) e, se quiser, o rehash quando o fator de carga passar de ~0,7.
