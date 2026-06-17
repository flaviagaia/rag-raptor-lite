"""Demo: vector flat (só folhas) vs RAPTOR-lite (folhas + resumos) (~1s).

    python src/demo.py
"""

from __future__ import annotations

from pathlib import Path

from raptor import Raptor, completude, load_folhas

ROOT = Path(__file__).parent.parent

# Q1 é "ampla" (precisa agregar vários anos); Q2 é "pontual" (um fato só).
CONSULTAS = [
    ("Quais foram os valores do repasse por aluno ao longo dos anos?",
     ["60,00", "80,00", "100,00"], "ampla (agrega)"),
    ("Qual foi o repasse por aluno em 2022?",
     ["80,00"], "pontual"),
]


def main() -> None:
    folhas = load_folhas(ROOT / "data" / "trechos.json")
    r = Raptor(folhas, n_clusters=2)

    print("=" * 78)
    print("RAPTOR-lite: recuperar no nível certo (folha vs resumo)")
    print("=" * 78)

    soma = {"flat": 0.0, "raptor": 0.0}
    for q, spans, tipo in CONSULTAS:
        cf = r.flat(q)
        cr = r.raptor(q)
        soma["flat"] += completude(cf, spans)
        soma["raptor"] += completude(cr, spans)
        print(f"\nP: {q}   [{tipo}]")
        print(f"   flat   (completude {completude(cf, spans):.0%}): {cf}")
        print(f"   raptor (completude {completude(cr, spans):.0%}): {cr}")

    n = len(CONSULTAS)
    print("\n" + "-" * 78)
    print(f"Completude média: flat {soma['flat']/n:.0%}, RAPTOR-lite {soma['raptor']/n:.0%}")
    print("(o resumo de cluster responde a pergunta ampla; a folha, a pontual)")


if __name__ == "__main__":
    main()
