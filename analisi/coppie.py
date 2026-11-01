"""Idee utente: (1) conta la COPPIA di fattori, non il singolo aspetto; (2) la compensazione Morpurgo agisce in DUE
direzioni (troppo bassa / troppo alta). Stesso confronto di multifattore.py: data vera contro 5 date finte della stessa
persona. Scopro su meta' A delle persone, verifico su meta' B (Holm)."""
import json, os
import numpy as np
from scipy.stats import ttest_1samp

if "costruisci" not in globals():  # in locale; su Kaggle multifattore e' incollato sopra
    _q = os.path.dirname(os.path.abspath(__file__))
    exec(open(os.path.join(_q, "multifattore.py"), encoding="utf-8").read().split('if __name__ == "__main__":')[0])


def _diff(X, y, g):
    """data vera - media delle sue finte, una riga per persona"""
    vere = X[y == 1]
    return vere - np.array([X[(g == k) & (y == 0)].mean(0) for k in g[y == 1]])


def coppie(X, y, g, top=20):
    """tutte le coppie di fattori 0/1 (entrambi presenti); per ogni primo fattore tengo le 3 coppie piu' forti in A"""
    bin_ = [j for j in range(X.shape[1]) if set(np.unique(X[:, j])) <= {0, 1}]
    from scipy.stats import poisson
    cand = []
    a = np.arange(int(y.sum())) % 2 == 0
    pers_a = g[y == 1][a]
    vere_a = (y == 1) & np.isin(g, pers_a)
    finte_a = (y == 0) & np.isin(g, pers_a)
    for n, i in enumerate(bin_[:-1]):
        P = X[:, [i]] * X[:, bin_[n + 1:]]
        k, att = P[vere_a].sum(0), P[finte_a].sum(0) / NFINTE
        p = np.minimum(1, 2 * np.minimum(poisson.cdf(k, att), poisson.sf(k - 1, att)))
        p[att < 5] = 1  # troppo rara per dire qualcosa (atteso < 5 casi)
        for c in np.argsort(p)[:3]:
            cand.append((p[c], i, bin_[n + 1 + c], _diff(P[:, [c]], y, g)[:, 0]))
    cand.sort(key=lambda t: t[0])
    out = []
    vere_idx = np.where(y == 1)[0]
    for _, i, j, d in cand[:top]:
        P = X[:, i] * X[:, j]
        pa, pb = p_conteggi(P, y, g, a), p_conteggi(P, y, g, ~a)
        out.append(dict(fattore=f"{NOMI_F[i]} + {NOMI_F[j]}", scarto_A=float(d[a].mean()), p_A=pa,
                        scarto_B=float(d[~a].mean()), p_B=pb, p_B_holm=min(1.0, pb * top)))
    return out


def p_conteggi(P, y, g, meta):
    """Test giusto per eventi rari (il t-test sulle medie gonfiava i p con conteggi ~0):
    k = date vere col fattore nella meta' di persone, atteso = date finte col fattore / 5; Poisson a due code."""
    from scipy.stats import poisson
    persone = g[y == 1][meta]
    k = int(P[(y == 1)][meta].sum())
    att = P[(y == 0) & np.isin(g, persone)].sum() / NFINTE
    if att == 0:
        return 1.0
    return float(min(1.0, 2 * min(poisson.cdf(k, att), poisson.sf(k - 1, att))))


def due_direzioni(X, y, g):
    """per ogni pianeta personale: compensazione bassa (<=10° perc.), alta (>=90°), estrema (una delle due)"""
    out = []
    for p in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
        j = NOMI_F.index(f"compensazione {p}")
        lo, hi = np.percentile(X[:, j], [10, 90])
        for nome, ind in [("bassa", X[:, j] <= lo), ("alta", X[:, j] >= hi),
                          ("estrema", (X[:, j] <= lo) | (X[:, j] >= hi))]:
            d = _diff(ind[:, None].astype(float), y, g)[:, 0]
            a = np.arange(len(d)) % 2 == 0
            P = ind.astype(float)
            out.append(dict(fattore=f"compensazione {p} {nome}", scarto_A=float(d[a].mean()),
                            p_A=p_conteggi(P, y, g, a), scarto_B=float(d[~a].mean()), p_B=p_conteggi(P, y, g, ~a)))
    for o in out:
        o["p_B_holm"] = min(1.0, o["p_B"] * len(out))
    return out


if __name__ == "__main__":
    ris = []
    for nome, lista in GRUPPI_TEST.items():
        lista = [x for x in lista if x in gruppi]
        if not lista:
            continue
        X, y, g = costruisci(lista)
        r = dict(gruppo=nome, coppie=coppie(X, y, g), due_direzioni=due_direzioni(X, y, g))
        ris.append(r)
        print(f"== {nome}", flush=True)
        for e in r["coppie"][:5] + r["due_direzioni"]:
            print(f"  {e['fattore'][:45]:45} A {100 * e['scarto_A']:+.2f} | B {100 * e['scarto_B']:+.2f}  "
                  f"p_holm={e['p_B_holm']:.3f}", flush=True)
        json.dump(ris, open(os.path.join(QUI, "risultati_coppie.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
