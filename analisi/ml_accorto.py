"""ML con accortezze (piano fissato PRIMA di guardare, 02/11/2026):
- IMPARA su persone 'vecchie' (gruppi Wikidata strutturati), VERIFICA una sola volta su persone NUOVE (testo Wikipedia:
  'attempted suicide', 'antidepressant'), escluse quelle presenti anche nei gruppi vecchi. Via il 1° gennaio.
- 2 confronti: 'giorni' (stessa persona ±1-15 giorni) e 'anni' (stesso giorno ±1-5 anni, solo pianeti personali:
  niente Giove..Plutone, che insegnerebbero l'anno).
- 3 modelli: A compensazione IMPARATA (pesi scelti dai dati: pianeta personale x aspetto x dignita' dell'altro),
  B logistica su tutti i fattori, C alberi. Iperparametri scelti solo sulle persone vecchie (CV per persona).
- Test: AUC sulle nuove; nullo = 1000 rimescolamenti di quale data e' la vera, dentro ogni persona nuova. Holm sui 6.
Su Kaggle sopra questo file sono incollati: DATI, dignities, testa di multifattore.py."""
import json, os
import numpy as np
from datetime import date
from sklearn.linear_model import LogisticRegressionCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

VECCHI = ["suicidio", "depressione", "bipolare", "alcolismo", "dipendenze", "overdose", "schizofrenia", "ansia",
          "disturbi alimentari", "PTSD", "OCD", "tentato suicidio", "autolesionismo"]
NUOVI = ["tentato suicidio (testo)", "antidepressivi (testo)"]
PERS = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
CLASSI = ["domicilio", "esaltazione", "neutro", "caduta", "esilio"]
CL = {2: "domicilio", 1: "esaltazione", 0: "neutro", -1: "caduta", -2: "esilio"}
LENTI_NOMI = ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
NOMI_C = [f"{p} {k} pianeta in {c}" for p in PERS for _, k in TIPI for c in CLASSI]


def feat_comp(d, lon_geo, solo_veloci):
    """conteggi pianeta personale x aspetto x dignita' dell'altro pianeta (Luna solo se certa tutto il giorno)"""
    tz = (lon_geo or 0) / 15
    jd0 = swe.julday(d.year, d.month, d.day, 0 - tz)
    s0, a0 = stato(jd0)
    s1, a1 = stato(jd0 + 1)
    luna_ok = lon_geo is not None and s0[1] == s1[1]
    f = np.zeros(len(NOMI_C))
    for (i, j), k in a0.items():
        if a1.get((i, j)) != k or (1 in (i, j) and not luna_ok):
            continue
        for p, q in ((i, j), (j, i)):
            if NOMI[p] not in PERS or (solo_veloci and NOMI[q] in LENTI_NOMI):
                continue
            c = CL[dignity_score(NOMI[q], SEGNI[s0[q]])]
            f[NOMI_C.index(f"{NOMI[p]} {k} pianeta in {c}")] += 1
    return f


def tabella(persone, modo):
    global SPOSTA
    SPOSTA = modo
    keep = [i for i, n in enumerate(NOMI_F) if modo == "giorni" or (not any(l in n for l in LENTI_NOMI)
                                                                    and not n.startswith("compensazione"))]
    XA, XB, y, g = [], [], [], []
    import random
    for n, p in enumerate(persone):
        rnd = random.Random(p["id"])
        d = date.fromisoformat(p["data"])
        for t, dd in enumerate([d] + [finta(d, rnd) for _ in range(NFINTE)]):
            XA.append(feat_comp(dd, p["lon"], modo == "anni"))
            XB.append(np.array(feature(dd, p["lon"]))[keep])
            y.append(int(t == 0)); g.append(n)
    return np.array(XA), np.array(XB, float), np.array(y), np.array(g)


def auc_nullo(y, g, pred, rnd, n=1000):
    vero = roc_auc_score(y, pred)
    idx = [np.where(g == k)[0] for k in np.unique(g)]
    nulli = []
    for _ in range(n):
        y2 = np.zeros_like(y)
        for ii in idx:
            y2[rnd.choice(ii)] = 1
        nulli.append(roc_auc_score(y2, pred))
    return vero, nulli, (1 + sum(x >= vero for x in nulli)) / (1 + n)


if __name__ == "__main__":
    print("PIANO: impara su vecchi, verifica una volta su nuovi; 3 modelli + composto x 2 confronti; Holm su 8", flush=True)
    vecchi = {p["id"]: p for k in VECCHI if k in gruppi for p in gruppi[k] if p["data"][5:] != "01-01"}
    nuovi = {p["id"]: p for k in NUOVI if k in gruppi for p in gruppi[k]
             if p["data"][5:] != "01-01" and p["id"] not in vecchi}
    print(f"persone vecchie {len(vecchi)}, nuove {len(nuovi)}", flush=True)
    ris, rnd = [], np.random.default_rng(42)
    for modo in ("giorni", "anni"):
        XAv, XBv, yv, gv = tabella(list(vecchi.values()), modo)
        XAn, XBn, yn, gn = tabella(list(nuovi.values()), modo)
        print(f"== {modo}: tabelle pronte", flush=True)
        cv = list(GroupKFold(5).split(XAv, yv, gv))
        preds = {}
        modelli = {
            "A compensazione imparata": (make_pipeline(StandardScaler(), LogisticRegressionCV(Cs=8, cv=cv, max_iter=2000, scoring="roc_auc")), XAv, XAn),
            "B logistica tutti i fattori": (make_pipeline(StandardScaler(), LogisticRegressionCV(Cs=8, cv=cv, max_iter=2000, scoring="roc_auc")), XBv, XBn),
            "C alberi": (HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, early_stopping=True), XBv, XBn),
        }
        for nome, (m, Xv, Xn) in modelli.items():
            m.fit(Xv, yv)
            pred = m.predict_proba(Xn)[:, 1]
            preds[nome] = pred
            vero, nulli, p = auc_nullo(yn, gn, pred, rnd)
            r = dict(confronto=modo, modello=nome, auc=round(vero, 4), nullo_95=round(float(np.percentile(nulli, 95)), 4),
                     p=round(p, 4), nulli=[round(x, 4) for x in nulli[:200]], n_nuovi=len(nuovi))
            if nome.startswith("A"):
                lr = m[-1]
                coef = lr.coef_[0] / m[0].scale_  # peso per un aspetto in piu'
                r["pesi_imparati"] = {NOMI_C[i]: round(float(c), 4) for i, c in enumerate(coef)}
                r["C_scelto"] = float(lr.C_[0])
            ris.append(r)
            print(f"  RISULTATO {modo} | {nome}: AUC nuovi {vero:.4f} | caso 95% {r['nullo_95']} | p={p:.4f}", flush=True)
        # D: modelli composti (idea utente) = media dei ranghi delle previsioni di A, B, C; deciso prima dei risultati
        from scipy.stats import rankdata
        pred = np.mean([rankdata(v) for v in preds.values()], axis=0)
        vero, nulli, p = auc_nullo(yn, gn, pred, rnd)
        ris.append(dict(confronto=modo, modello="D modelli composti (A+B+C)", auc=round(vero, 4),
                        nullo_95=round(float(np.percentile(nulli, 95)), 4), p=round(p, 4),
                        nulli=[round(x, 4) for x in nulli[:200]], n_nuovi=len(nuovi)))
        print(f"  RISULTATO {modo} | D composti: AUC nuovi {vero:.4f} | p={p:.4f}", flush=True)
    ordine = sorted(range(len(ris)), key=lambda i: ris[i]["p"])
    prec = 0
    for k, i in enumerate(ordine):
        prec = max(prec, min(1, (len(ris) - k) * ris[i]["p"]))
        ris[i]["p_holm"] = round(prec, 4)
    for r in ris:
        print(f"  FINALE {r['confronto']} | {r['modello']}: AUC {r['auc']} p={r['p']} Holm={r['p_holm']}", flush=True)
    json.dump(ris, open(os.path.join(QUI, "ml_accorto.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
