# Globalsim-ED2
Desenvolvimento do GlobalSIM, um sistema web em Python e Flask para gerenciamento de países, clientes, eSIMs e pacotes de Internet. O projeto aplica Tabela Hash, Árvore B e Grafos para consultas de cobertura, gerenciamento de registros e cálculo de rotas de menor latência.

## Como executar

```bash
cd globalsim
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug   # servidor de desenvolvimento
pytest -q                     # testes das estruturas
```

## Etapa 1 — Tabela Hash (`globalsim/estruturas/tabela_hash.py`)

Os países atendidos ficam numa Tabela Hash implementada do zero (sem `dict`), indexada pelo código do país (`BR`, `IT`, ...).

- **Colisões:** encadeamento separado. Cada posição do vetor (bucket) é uma lista de pares `[chave, valor]`; chaves que caem no mesmo índice ficam na mesma cadeia.
- **Função de hash:** polinomial própria, `h = (h * 31 + ord(c)) % capacidade` para cada caractere. Não usamos `hash()` do Python porque ele muda a cada execução, o que tornaria a instrumentação não reproduzível.
- **Capacidade e rehash:** começa em 7 (primo pequeno, para colisões e redimensionamento aparecerem com os países cadastrados). Quando o fator de carga passa de 0,75, a capacidade dobra e é arredondada para o próximo primo (7 → 17 → 37 ...), e todas as chaves são reinseridas.
- **Operações:** `inserir` (rejeita código duplicado), `buscar`, `atualizar`, `remover`, `listar`/`itens`.
- **Instrumentação** (`metricas()` / `estatisticas()`): capacidade, nº de elementos, fator de carga, colisões atuais e acumuladas, maior bucket, buckets usados, nº de rehashes, comparações da última busca e o mapa dos buckets (índice → chaves).
- **Persistência:** `arquivos/paises.json` é carregado na tabela ao iniciar e regravado após cada cadastro, alteração ou remoção (`servicos/paises_service.py`).
