import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from raptor import Raptor, completude, load_folhas  # noqa: E402

FOLHAS = load_folhas(ROOT / "data" / "trechos.json")
R = Raptor(FOLHAS, n_clusters=2)

Q_AMPLA = "Quais foram os valores do repasse por aluno ao longo dos anos?"
SPANS_AMPLA = ["60,00", "80,00", "100,00"]
Q_PONTUAL = "Qual foi o repasse por aluno em 2022?"


def test_constroi_resumos_de_cluster():
    assert len(R.resumos) == 2
    # Um resumo agrega os três anos de repasse num nó só.
    assert any(all(v in res.texto for v in SPANS_AMPLA) for res in R.resumos)


def test_flat_nao_responde_pergunta_ampla():
    # Só folhas: a melhor folha traz um ano, não os três.
    assert completude(R.flat(Q_AMPLA), SPANS_AMPLA) < 1.0


def test_raptor_responde_pergunta_ampla_pelo_resumo():
    assert completude(R.raptor(Q_AMPLA), SPANS_AMPLA) == 1.0


def test_raptor_nao_atrapalha_pergunta_pontual():
    assert completude(R.flat(Q_PONTUAL), ["80,00"]) == 1.0
    assert completude(R.raptor(Q_PONTUAL), ["80,00"]) == 1.0


def test_completude_media_melhora():
    consultas = [(Q_AMPLA, SPANS_AMPLA), (Q_PONTUAL, ["80,00"])]
    n = len(consultas)
    flat = sum(completude(R.flat(q), s) for q, s in consultas) / n
    rap = sum(completude(R.raptor(q), s) for q, s in consultas) / n
    assert rap > flat
    assert rap == 1.0
