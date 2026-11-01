"""Contesto (soldi, status, paese, mestiere, fama...) contro cielo: chi finisce nel gruppo (suicidio, ecc.)?
Casi = gruppi Wikidata; controlli = persone famose qualsiasi nate lo stesso anno (giorno a caso).
Modelli (gradient boosting, CV 5 fold): solo contesto, solo cielo, contesto + cielo.
Nullo per il cielo: rimescolo i cieli fra le persone (il contesto resta) 20 volte -> quanto 'aiuta' un cielo a caso."""
import json, os, time
import numpy as np
from collections import Counter
from datetime import date
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

QUI = os.environ.get("QUI", os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(QUI, "multifattore.py"), encoding="utf-8").read().split('if __name__ == "__main__":')[0]) \
    if "feature" not in globals() else None  # in locale riusa feature(); su Kaggle e' gia' incollato sopra
if "CTX" not in globals():
    CTX = open(os.path.join(QUI, "contesto.json")).read()
ctx = json.loads(CTX)
controlli = ctx["controlli"]
C = ctx["contesto"]
T0 = time.time()


def tabella(persone):
    tutte = [C.get(p["id"], {}) for p in persone]
    top = lambda k, n: [x for x, _ in Counter(c.get(k) for c in tutte if c.get(k)).most_common(n)]
    return top("paese", 30), top("mestiere", 50), top("sesso", 3)


def riga_ctx(p, paesi, mestieri, sessi):
    c = C.get(p["id"], {})
    return ([int(c.get("paese") == x) for x in paesi] + [int(c.get("mestiere") == x) for x in mestieri]
            + [int(c.get("sesso") == x) for x in sessi]
            + [np.log1p(c.get("fama", 0)), c.get("soldi", 0), c.get("nobile", 0), c.get("universita", 0),
               int(p["data"][:4]) // 10])


def auc(X, y):
    pred = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15).fit(X[tr], y[tr])
        pred[te] = m.predict_proba(X[te])[:, 1]
    return roc_auc_score(y, pred)


if __name__ == "__main__":
    ris = []
    for nome, lista in {"suicidio": ["suicidio"], "tutti i gruppi": list(gruppi)}.items():
        casi = list({p["id"]: p for g in lista if g in gruppi for p in gruppi[g]}.values())
        persone = casi + controlli
        y = np.array([1] * len(casi) + [0] * len(controlli))
        paesi, mestieri, sessi = tabella(persone)
        Xc = np.array([riga_ctx(p, paesi, mestieri, sessi) for p in persone], float)
        Xs = np.array([feature(date.fromisoformat(p["data"]), p["lon"]) for p in persone], float)
        print(f"== {nome}: casi {len(casi)} controlli {len(controlli)} ({(time.time() - T0) / 60:.1f} min)", flush=True)
        a_ctx, a_sky, a_both = auc(Xc, y), auc(Xs, y), auc(np.hstack([Xc, Xs]), y)
        rnd = np.random.default_rng(0)
        nulli = [auc(np.hstack([Xc, Xs[rnd.permutation(len(Xs))]]), y) for _ in range(20)]
        p = (1 + sum(n >= a_both for n in nulli)) / 21
        r = dict(gruppo=nome, casi=len(casi), controlli=len(controlli), auc_contesto=round(a_ctx, 4),
                 auc_cielo=round(a_sky, 4), auc_entrambi=round(a_both, 4), nulli_entrambi=[round(x, 4) for x in nulli],
                 p_cielo_aggiunge=round(p, 4))
        ris.append(r)
        print(f"  CONTESTO {a_ctx:.3f} | CIELO {a_sky:.3f} | ENTRAMBI {a_both:.3f} vs cielo a caso "
              f"{np.mean(nulli):.3f} (p={p:.3f})", flush=True)
        json.dump(ris, open(os.path.join(QUI, "risultati_contesto.json"), "w", encoding="utf-8"), indent=1)
