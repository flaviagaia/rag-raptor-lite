"""RAPTOR-lite: árvore de resumos para recuperação em vários níveis de abstração.

RAPTOR (Sarthi et al., 2024) clusteriza os trechos e resume cada cluster
recursivamente, formando uma árvore. A busca pode então recuperar tanto a FOLHA (um
fato específico) quanto o RESUMO (a visão agregada de um tema). Perguntas "amplas"
("liste os valores por ano") são respondidas pelo nó de resumo; perguntas
"pontuais", pela folha.

Aqui a versão lite, offline e determinística:
- clusteriza as folhas por similaridade (KMeans sobre TF-IDF, seed fixa);
- monta um resumo por cluster de forma EXTRATIVA (concatena as folhas);
  NB: o RAPTOR original usa um LLM para resumir de forma abstrativa; o resumo
  extrativo mantém o experimento reprodutível sem API. Ver limitações no README.
- indexa folhas + resumos juntos e recupera o melhor nó.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class No:
    id: str
    texto: str
    nivel: int  # 0 = folha, 1 = resumo de cluster


def _resumo_extrativo(textos: list[str]) -> str:
    """Resumo determinístico: concatena as folhas (proxy do resumo do LLM)."""
    return " ".join(textos)


class Raptor:
    def __init__(self, folhas: list[No], n_clusters: int = 2) -> None:
        self.folhas = folhas
        vec0 = TfidfVectorizer(strip_accents="unicode")
        X = vec0.fit_transform(n.texto for n in folhas)
        km = KMeans(n_clusters=n_clusters, random_state=0, n_init=10)
        labels = km.fit_predict(X.toarray())

        self.resumos: list[No] = []
        for c in sorted(set(labels)):
            textos = [folhas[i].texto for i in range(len(folhas)) if labels[i] == c]
            self.resumos.append(No(id=f"resumo_{c}", texto=_resumo_extrativo(textos), nivel=1))

        self.arvore = list(folhas) + self.resumos
        self._vec = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")
        self._mat = self._vec.fit_transform(n.texto for n in self.arvore)
        self._folha_idx = [i for i, n in enumerate(self.arvore) if n.nivel == 0]

    def _sims(self, query: str):
        return cosine_similarity(self._vec.transform([query]), self._mat).ravel()

    def flat(self, query: str) -> str:
        """Só folhas: melhor trecho específico (sem visão agregada)."""
        sims = self._sims(query)
        best = max(self._folha_idx, key=lambda i: sims[i])
        return self.arvore[best].texto

    def raptor(self, query: str) -> str:
        """Folhas + resumos: recupera o melhor nó em qualquer nível."""
        sims = self._sims(query)
        best = int(sims.argmax())
        return self.arvore[best].texto


def load_folhas(path: Path) -> list[No]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [No(id=l["id"], texto=l["texto"], nivel=0) for l in data["leaves"]]


def completude(contexto: str, spans: list[str]) -> float:
    return sum(s in contexto for s in spans) / len(spans)
