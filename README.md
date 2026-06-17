# rag-raptor-lite

RAPTOR-lite: uma **árvore de resumos** para recuperar no nível certo de abstração,
folha (um fato) ou resumo (a visão agregada de um tema).

> **Em uma frase:** perguntas amplas ("liste os valores por ano") não se respondem com
> um trecho só; o RAPTOR clusteriza os trechos e resume cada cluster numa árvore, e a
> busca recupera o resumo quando a pergunta é ampla e a folha quando é pontual.

> *RAPTOR-lite: cluster the chunks and summarize each cluster into a tree (Sarthi et
> al., 2024). A broad question is answered by the summary node that aggregates the
> cluster; a specific question by the leaf. Here the summaries are extractive and
> deterministic, so the demo runs offline with no LLM.*

---

## O problema

A recuperação plana traz os melhores trechos-folha. Para "qual foi o repasse em 2022?"
isso basta. Mas para "como o repasse evoluiu ao longo dos anos?" a resposta está
**espalhada** em vários trechos (2020, 2022, 2024). O top-1 traz um ano; o modelo
responde sem a visão de conjunto. Falta um nível de abstração acima da folha.

## Como funciona (o técnico)

RAPTOR (Sarthi et al., 2024) constrói uma árvore: clusteriza os trechos, resume cada
cluster, e repete recursivamente. A busca indexa todos os níveis, então pode recuperar
tanto o detalhe quanto o resumo.

Esta versão lite, offline e determinística:

1. clusteriza as folhas por similaridade (KMeans sobre TF-IDF, seed fixa);
2. monta um **resumo por cluster** de forma extrativa (concatena as folhas do cluster);
3. indexa folhas + resumos juntos e recupera o melhor nó em qualquer nível.

```
flat(query)   = melhor FOLHA por similaridade           (sem visão agregada)
raptor(query) = melhor NÓ (folha ou resumo)             (recupera no nível certo)
```

Complexidade: o clustering é feito uma vez na indexação; a busca é a mesma de sempre,
sobre alguns nós a mais (os resumos).

## Resultado (determinístico, offline)

Relatórios fictícios do Programa Alfa: trechos de repasse por ano (2020/2022/2024) e de
elegibilidade/adesão. KMeans separa os dois temas; o resumo do cluster de repasse
agrega os três anos.

| Consulta                                        | Tipo            | flat | RAPTOR-lite |
| ----------------------------------------------- | --------------- | ---- | ----------- |
| Valores do repasse ao longo dos anos            | ampla (agrega)  | 33%  | **100%**    |
| Repasse por aluno em 2022                       | pontual         | 100% | 100%        |
| **Completude média**                            |                 | **67%** | **100%** |

A pergunta ampla é respondida pelo nó de resumo; a pontual continua respondida (o
RAPTOR recupera em vários níveis, então a folha certa segue acessível).

Rode você mesmo:

```bash
pip install -r requirements.txt
python src/demo.py
python -m pytest -q
```

## Como explicar em 30 segundos

"Algumas perguntas pedem detalhe, outras pedem o panorama. Se eu só guardo trechos, o
panorama nunca aparece, porque está espalhado. O RAPTOR agrupa os trechos parecidos e
cria um resumo de cada grupo, formando uma árvore. Aí a busca pega a folha quando a
pergunta é específica e o resumo quando ela é ampla."

## Onde isso entra (degrau 2 da série)

Hierarquia, adjacência, remissão e vigência (degrau 1, `rag-legal-graph-lite`) usam a
estrutura que a norma já tem. O RAPTOR é degrau 2: cria uma estrutura nova (a árvore de
resumos) por clustering. É mais poderoso para perguntas de síntese, e mais caro
(clustering + resumo de cada nó). Vale quando há muitas perguntas "globais".

## Limitações honestas

- O RAPTOR original usa um **LLM** para resumir cada cluster de forma **abstrativa**.
  Aqui o resumo é **extrativo** (concatenação das folhas), para o experimento rodar
  offline e determinístico. Resumos abstrativos comprimem melhor e generalizam; o
  mecanismo de recuperação multi-nível é o mesmo.
- Uma só camada de resumo (não recursiva). RAPTOR empilha vários níveis; aqui um basta
  para mostrar a ideia.
- Corpus pequeno e fictício; o número de clusters é fixado (k=2). Em produção, o k e a
  profundidade são hiperparâmetros, e o clustering precisa de mais cuidado.
- Completude usa presença de spans (substring), proxy de "a informação está no
  contexto"; não mede a geração.

## Referências científicas (crédito aos autores)

- **Sarthi et al. (2024).** *RAPTOR: Recursive Abstractive Processing for Tree-Organized
  Retrieval.* ICLR. A técnica desta demo.
- **Lewis et al. (2020).** *Retrieval-Augmented Generation for Knowledge-Intensive NLP
  Tasks.* NeurIPS.
- **Edge et al. (2024).** *From Local to Global: A Graph RAG Approach to Query-Focused
  Summarization.* arXiv:2404.16130. Outra forma de responder perguntas globais.
- Corpus fictício; nenhuma relação com dados reais.

Bibliografia completa do portfólio em `REFERENCIAS.md`.

---

Part of my LinkedIn series on efficient RAG → [Flávia Gaia](https://www.linkedin.com/in/flavia-gaia/)
