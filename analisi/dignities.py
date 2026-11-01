"""
Dignita' essenziali secondo il sistema di Lisa Morpurgo (fonte: "Introduzione
all'astrologia" + riscontro incrociato con https://lestelleinterra.blogspot.com/
2014/02/astrologia-e-oroscopo-nei-nostri-tempi.html, tabella segno-per-segno
coerente e verificata: ogni segno opposto ha domicilio/esilio invertiti).

Ogni segno (tranne Leone/Cancro, domicilio solitario dei luminari) ha DUE
pianeti domiciliati. Include 2 pianeti transplutoniani IPOTETICI mai
confermati dall'astronomia (X, Y - la teoria di Morpurgo prevedeva la loro
esistenza per completare lo schema a 12 segni x 2 pianeti). Questi non hanno
effemeridi calcolabili (non esistono come corpi reali confermati) - sono
inclusi in tabella per fedelta' al sistema ma IGNORATI nel calcolo (nessuna
posizione, quindi mai "domicilio guadagnato" con precisione, verranno
semplicemente esclusi dal punteggio quando il pianeta del tema e' X/Y).

ponytail: qui NON distinguo domicilio "primario" vs "base" (gradazione di
forza) perche' la fonte usata per la tabella completa (blog, cross-validato)
non la riporta esplicitamente per tutti i segni; tratto i due domicili di
ogni pianeta come equivalenti (+2 entrambi). Se serve la gradazione esatta
richiede leggere pagina per pagina "Il Convitato di Pietra" (altro libro),
non fatto qui.
"""

DIGNITIES = {
    "Aries":       {"domicile": ["Mars", "Pluto"],    "exaltation": "Sun",     "detriment": ["Venus", "X"],     "fall": "Saturn"},
    "Taurus":      {"domicile": ["Venus", "X"],        "exaltation": "Jupiter", "detriment": ["Mars", "Pluto"],  "fall": "Mercury"},
    "Gemini":      {"domicile": ["Mercury", "Y"],       "exaltation": "Pluto",   "detriment": ["Jupiter", "Neptune"], "fall": "X"},
    "Cancer":      {"domicile": "Moon",                 "exaltation": "Venus",  "detriment": ["Uranus", "Saturn"],   "fall": "Mars"},
    "Leo":         {"domicile": "Sun",                  "exaltation": "Y",      "detriment": ["Saturn", "Uranus"],   "fall": "Neptune"},
    "Virgo":       {"domicile": ["Mercury", "Y"],       "exaltation": "Uranus", "detriment": ["Jupiter", "Neptune"], "fall": "Moon"},
    "Libra":       {"domicile": ["Venus", "X"],        "exaltation": "Saturn",  "detriment": ["Mars", "Pluto"],  "fall": "Sun"},
    "Scorpio":     {"domicile": ["Mars", "Pluto"],     "exaltation": "Mercury", "detriment": ["Venus", "X"],     "fall": "Jupiter"},
    "Sagittarius": {"domicile": ["Jupiter", "Neptune"], "exaltation": "X",      "detriment": ["Mercury", "Y"],    "fall": "Pluto"},
    "Capricorn":   {"domicile": ["Saturn", "Uranus"],   "exaltation": "Mars",   "detriment": "Moon",              "fall": "Venus"},
    "Aquarius":    {"domicile": ["Saturn", "Uranus"],   "exaltation": "Neptune","detriment": "Sun",               "fall": "Y"},
    "Pisces":      {"domicile": ["Jupiter", "Neptune"], "exaltation": "Moon",   "detriment": ["Mercury", "Y"],    "fall": "Uranus"},
}

HYPOTHETICAL_PLANETS = {"X", "Y"}  # nessuna effemeride reale disponibile

PERSONAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
ALL_COMPUTABLE_PLANETS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]

def _matches(field, planet_name):
    if field is None:
        return False
    if isinstance(field, list):
        return planet_name in field
    return field == planet_name

def dignity_score(planet_name, sign):
    """+2 domicilio, +1 esaltazione, -2 esilio, -1 caduta, 0 neutro.
    planet_name deve essere un pianeta reale (in ALL_COMPUTABLE_PLANETS)."""
    if planet_name in HYPOTHETICAL_PLANETS:
        raise ValueError(f"{planet_name} e' ipotetico, nessuna posizione calcolabile")
    d = DIGNITIES[sign]
    if _matches(d["domicile"], planet_name):
        return 2
    if _matches(d["exaltation"], planet_name):
        return 1
    if _matches(d["detriment"], planet_name):
        return -2
    if _matches(d["fall"], planet_name):
        return -1
    return 0

def compensatory_gains(chart_signs, aspects):
    """Per ogni pianeta personale, quali altri pianeti 'guadagna' per aspetto
    (indipendentemente dal proprio segno). Es: Luna in Vergine quadrato
    Nettuno -> la Luna guadagna Nettuno anche se Vergine non ce l'ha nativo."""
    gains = {p: set() for p in PERSONAL_PLANETS}
    for a in aspects:
        pair, kind = a.split(":")
        p1, p2 = pair.split("-")
        if p1 in PERSONAL_PLANETS:
            gains[p1].add(p2)
        if p2 in PERSONAL_PLANETS:
            gains[p2].add(p1)
    return gains


ASPECT_WEIGHT = {"conjunction": 1.0, "opposition": 1.0, "square": 0.8, "trine": 0.5, "sextile": 0.3}

# Gerarchia tra pianeti personali (domanda aperta utente: Sole e Luna contano
# di piu' di Mercurio/Venere/Marte? qui una prima ipotesi testabile, non un
# dato di fatto - da verificare empiricamente se il modello con questi pesi
# performa meglio di quello senza gerarchia).
PERSONAL_PLANET_IMPORTANCE = {"Sun": 1.0, "Moon": 1.0, "Mercury": 0.6, "Venus": 0.6, "Mars": 0.6}

def weighted_compensation(personal_planet, chart_signs, aspects):
    """Variante pesata (richiesta utente): invece di gain binario 0/1, somma su tutti
    gli aspetti del pianeta personale: peso_aspetto * dignity_score(altro_pianeta, suo_segno).
    Cattura "guadagno proporzionale alla forza di chi te lo da'" (un pianeta forte nel
    proprio segno che aspetta il tuo pianeta personale conta di piu' di uno debole),
    non solo presenza/assenza dell'aspetto."""
    total = 0.0
    for a in aspects:
        pair, kind = a.split(":")
        p1, p2 = pair.split("-")
        other = None
        if p1 == personal_planet:
            other = p2
        elif p2 == personal_planet:
            other = p1
        if other is None or other in HYPOTHETICAL_PLANETS or other not in ALL_COMPUTABLE_PLANETS:
            continue
        w = ASPECT_WEIGHT.get(kind, 0.0)
        other_sign = chart_signs.get(other)
        if other_sign is None:
            continue
        total += w * dignity_score(other, other_sign)
    return total


def _demo():
    print("=== Verifica coerenza tabella (segni opposti = domicilio/esilio invertiti) ===")
    OPPOSITES = [("Aries","Libra"),("Taurus","Scorpio"),("Gemini","Sagittarius"),
                 ("Cancer","Capricorn"),("Leo","Aquarius"),("Virgo","Pisces")]
    for a, b in OPPOSITES:
        dom_a = DIGNITIES[a]["domicile"]
        det_b = DIGNITIES[b]["detriment"]
        ok = set(dom_a if isinstance(dom_a, list) else [dom_a]) == set(det_b if isinstance(det_b, list) else [det_b] if det_b else [])
        print(f"  {a} domicilio={dom_a}  vs  {b} esilio={det_b}  -> {'OK' if ok else 'MISMATCH'}")

    print("\n=== Esempio utente: Luna Vergine quadrato Nettuno ===")
    print("Dignita' Luna in Vergine:", dignity_score("Moon", "Virgo"))  # Vergine non ha Luna in nessun ruolo -> 0
    print("Dignita' Luna in Cancro (domicilio):", dignity_score("Moon", "Cancer"))
    print("Dignita' Luna in Capricorno (esilio):", dignity_score("Moon", "Capricorn"))
    print("Dignita' Luna in Toro (nessun ruolo qui):", dignity_score("Moon", "Taurus"))
    print("Dignita' Luna in Vergine (caduta! -> -1):", dignity_score("Moon", "Virgo"))

    aspects = ["Moon-Neptune:square", "Sun-Mars:trine"]
    gains = compensatory_gains(None, aspects)
    print("\nGuadagni compensatori:")
    for p, g in gains.items():
        if g:
            print(f"  {p} guadagna: {g}")

if __name__ == "__main__":
    _demo()
