"""Test multifattoriale (idea utente: la compensazione Morpurgo agisce combinando molti fattori).
Per ogni persona: data vera (classe 1) + 5 date finte della stessa persona spostate 1-15 giorni (classe 0).
Feature: segni di tutti i pianeti (Luna solo se certa nel giorno), dignita' Morpurgo, compensazione pesata per pianeta
personale, aspetti fra tutte le coppie, conteggi quadrati/trigoni/opposizioni.
Modelli: regressione logistica e gradient boosting, CV a 5 fold per persona (vera e finte nello stesso fold), AUC.
Nullo: rimescolo QUALE delle 6 date e' la vera, dentro ogni persona (50 volte logistica, 10 boosting, in parallelo).
AUC 0.5 = il modello non distingue la data vera da quelle vicine."""
import json, os, random, time
from datetime import date, timedelta
import numpy as np
import swisseph as swe
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

QUI = os.environ.get("QUI", os.path.dirname(os.path.abspath(__file__)))
if "DATI" not in globals():  # in locale; su Kaggle dati e dignities sono incollati sopra
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dignities import dignity_score, weighted_compensation
    DATI = open(os.path.join(QUI, "wikidata_gruppi.json")).read()
gruppi = json.loads(DATI)
GRUPPI_TEST = {
    "suicidio": ["suicidio"],
    "tentato suicidio (testo)": ["tentato suicidio (testo)"],
    "antidepressivi (testo)": ["antidepressivi (testo)"],
    "psichiatrici (depr+bip+schizo+ansia+DCA+PTSD+OCD)": ["depressione", "bipolare", "schizofrenia", "ansia",
                                                         "disturbi alimentari", "PTSD", "OCD"],
    "sostanze (alcol+dip+overdose)": ["alcolismo", "dipendenze", "overdose"],
    "tutti": list(gruppi),
}
ORB, NFINTE, T0 = 8, 5, time.time()
# "giorni": stessa persona ±1-15 giorni (Luna fa tutto il giro, stagione uguale)
# "anni": stesso giorno dell'anno, ±1-5 anni (stagione uguale; Mercurio, Venere, Marte, Giove, Saturno si spostano molto)
SPOSTA = os.environ.get("SPOSTA", "giorni")


def finta(d, rnd):
    if SPOSTA == "anni":
        a = d.year + rnd.choice([-1, 1]) * rnd.randint(1, 5)
        return d.replace(year=a, day=28) if (d.month, d.day) == (2, 29) else d.replace(year=a)
    return d + timedelta(days=rnd.choice([-1, 1]) * rnd.randint(1, 15))
PL = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO]
NOMI = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
SEGNI = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
         "Aquarius", "Pisces"]
TIPI = [(0, "conjunction"), (180, "opposition"), (90, "square"), (120, "trine"), (60, "sextile")]


def ang(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def stato(jd):
    lon = [swe.calc_ut(jd, p)[0][0] for p in PL]
    segni = [int(l // 30) for l in lon]
    asp = {}
    for i in range(10):
        for j in range(i + 1, 10):
            for a, k in TIPI:
                if abs(ang(lon[i], lon[j]) - a) <= ORB:
                    asp[(i, j)] = k
    return segni, asp


def feature(d, lon_geo):
    """vettore di feature; la Luna (indice 1) entra solo se segno/aspetto uguali a inizio e fine giorno"""
    tz = (lon_geo or 0) / 15
    jd0 = swe.julday(d.year, d.month, d.day, 0 - tz)
    s0, a0 = stato(jd0)
    s1, a1 = stato(jd0 + 1)
    luna_ok = lon_geo is not None
    f = []
    for i in range(10):
        oh = [0] * 12
        if i != 1 or (luna_ok and s0[1] == s1[1]):
            oh[s0[i]] = 1
        f += oh
    dign = []
    for i in range(10):
        certo = i != 1 or (luna_ok and s0[1] == s1[1])
        dign.append(dignity_score(NOMI[i], SEGNI[s0[i]]) if certo else 0)
    f += dign
    asp = {k: v for k, v in a0.items() if a1.get(k) == v and (1 not in k or luna_ok)}
    for i in range(10):
        for j in range(i + 1, 10):
            f += [int(asp.get((i, j)) == k) for _, k in TIPI]
    segni_n = {NOMI[i]: SEGNI[s0[i]] for i in range(10)}
    lista = [f"{NOMI[i]}-{NOMI[j]}:{k}" for (i, j), k in asp.items()]
    f += [weighted_compensation(p, segni_n, lista) for p in ["Sun", "Moon", "Mercury", "Venus", "Mars"]]
    f += [sum(v == k for v in asp.values()) for k in ("square", "trine", "opposition")]
    return f


CACHE = {}  # id persona -> righe di feature (una persona puo' stare in piu' gruppi)


def costruisci(nomi_gruppi):
    # una persona in piu' gruppi conta una volta; via il 1° gennaio (data segnaposto frequente in Wikidata)
    persone = {p["id"]: p for g in nomi_gruppi for p in gruppi[g] if p["data"][5:] != "01-01"}
    X, y, gid = [], [], []
    for n, (k, p) in enumerate(persone.items()):
        if k not in CACHE:
            rnd = random.Random(k)
            d = date.fromisoformat(p["data"])
            date_ = [d] + [finta(d, rnd) for _ in range(NFINTE)]
            CACHE[k] = [feature(dd, p["lon"]) for dd in date_]
        for t, f in enumerate(CACHE[k]):
            X.append(f); y.append(int(t == 0)); gid.append(n)
        if (n + 1) % 1000 == 0:
            print(f"  feature {n + 1}/{len(persone)}  ({(time.time() - T0) / 60:.1f} min dall'inizio)", flush=True)
    return np.array(X, float), np.array(y), np.array(gid)


def auc_cv(modello, X, y, g):
    pred = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g):
        m = modello()
        m.fit(X[tr], y[tr])
        pred[te] = m.predict_proba(X[te])[:, 1]
    # coda (idea utente: il segnale puo' stare in una piccola porzione di persone):
    # quota di date vere nel 2% dei punteggi piu' alti; il caso da' 1/6
    top = np.argsort(-pred)[:max(1, len(pred) // 50)]
    return roc_auc_score(y, pred), float(y[top].mean())


def mescola(y, g, rnd):
    """per ogni persona sceglie a caso quale delle 6 righe e' 'vera'"""
    y2 = np.zeros_like(y)
    for k in np.unique(g):
        idx = np.where(g == k)[0]
        y2[rnd.choice(idx)] = 1
    return y2


NOMI_F = ([f"{p} in {s}" for p in NOMI for s in SEGNI] + [f"dignita {p}" for p in NOMI]
          + [f"{NOMI[i]} {k} {NOMI[j]}" for i in range(10) for j in range(i + 1, 10) for _, k in TIPI]
          + [f"compensazione {p}" for p in ["Sun", "Moon", "Mercury", "Venus", "Mars"]] + ["n square", "n trine", "n opposition"])


def esplora(X, y, g, top=10):
    """Ricerca libera: per ogni fattore, data vera - media delle sue finte. Scopro su meta' A, confermo su meta' B."""
    from scipy.stats import ttest_1samp
    vere = X[y == 1]
    finte = np.array([X[(g == k) & (y == 0)].mean(0) for k in g[y == 1]])
    diff = vere - finte
    a = np.arange(len(diff)) % 2 == 0
    pa = [ttest_1samp(diff[a, j], 0).pvalue if diff[a, j].std() > 0 else 1 for j in range(X.shape[1])]
    migliori = np.argsort(pa)[:top]
    out = []
    for j in migliori:
        pb = ttest_1samp(diff[~a, j], 0).pvalue if diff[~a, j].std() > 0 else 1
        out.append(dict(fattore=NOMI_F[j], scarto_A=round(float(diff[a, j].mean()), 4), p_A=float(pa[j]),
                        scarto_B=round(float(diff[~a, j].mean()), 4), p_B=float(pb), p_B_holm=min(1.0, float(pb) * top)))
    return out


NJOBS = -1  # processi per i rimescolamenti (1 con GPU)
MODELLI = {
    "logistica": (lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=500)), 50),
    "boosting": (lambda: HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, max_leaf_nodes=15), 10),
}

if __name__ == "__main__":
    ris = []
    for nome, lista in GRUPPI_TEST.items():
        lista = [x for x in lista if x in gruppi]
        if not lista:
            continue
        print(f"== {nome}", flush=True)
        X, y, g = costruisci(lista)
        assert X.shape[1] == len(NOMI_F)
        es = esplora(X, y, g)
        ris.append(dict(gruppo=nome, esplorazione=es))
        for e in es:
            print(f"  ESPLORA {e['fattore']:28} A {e['scarto_A']:+.4f} p={e['p_A']:.4f} | B {e['scarto_B']:+.4f} "
                  f"p_holm={e['p_B_holm']:.3f}", flush=True)
        for mn, (mod, nperm) in MODELLI.items():
            vero, coda = auc_cv(mod, X, y, g)
            rnd = np.random.default_rng(1)
            from joblib import Parallel, delayed
            t1 = time.time()
            ys = [mescola(y, g, rnd) for _ in range(nperm)]
            risultati_perm = Parallel(n_jobs=NJOBS)(delayed(auc_cv)(mod, X, yy, g) for yy in ys)
            nulli, code_n = [c[0] for c in risultati_perm], [c[1] for c in risultati_perm]
            p_coda = (1 + sum(c >= coda for c in code_n)) / (1 + nperm)
            print(f"  {mn}: {nperm} permutazioni in {(time.time() - t1) / 60:.1f} min", flush=True)
            p = (1 + sum(n >= vero for n in nulli)) / (1 + nperm)
            r = dict(gruppo=nome, persone=int(g.max() + 1), modello=mn, auc=round(vero, 4),
                     nullo_medio=round(float(np.mean(nulli)), 4), nullo_95=round(float(np.percentile(nulli, 95)), 4),
                     p=round(p, 4), nulli=[round(x, 4) for x in nulli],
                     coda_2pct=round(coda, 4), coda_nulli=[round(x, 4) for x in code_n], p_coda=round(p_coda, 4))
            ris.append(r)
            print(f"  RISULTATO {nome} {mn}: AUC {vero:.4f}  nullo {np.mean(nulli):.4f} (95%: {r['nullo_95']})  p={p:.3f}"
                  f" | coda 2% {coda:.3f} vs caso {np.mean(code_n):.3f} p={p_coda:.3f}",
                  flush=True)
            json.dump(ris, open(os.path.join(QUI, "risultati_multifattore.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
