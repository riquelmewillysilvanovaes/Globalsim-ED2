# Globalsim-ED2

Desenvolvimento do GlobalSIM, um sistema web em Python e Flask para gerenciamento de países, clientes, eSIMs e pacotes de Internet. O projeto aplica Tabela Hash, Árvore B e Grafos para consultas de cobertura, gerenciamento de registros e cálculo de rotas de menor latência.

## Diferencial da Equipe: Simulação de Falhas e Recálculo de Rotas

* **Objetivo:** Simular quedas e indisponibilidades em conexões da rede internacional e recalcular automaticamente a melhor rota para o cliente.
* **Problema que resolve:** Evita a interrupção do serviço de eSIM quando um link internacional ou rota primária fica indisponível.
* **Como será integrado:**
  * **Etapa 1:** Modelagem inicial dos países atendidos com Tabela Hash e persistência em JSON.
  * **Etapa 2:** Associação dos clientes cadastrados na Árvore B aos destinos afetados por eventuais quedas.
  * **Etapa 3:** Interface para desativar manualmente enlaces do grafo e execução automática do algoritmo de Dijkstra para encontrar a rota alternativa de menor latência.
