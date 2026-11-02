# Cielo e difficoltà: machine learning

Se l'astrologia funziona come un insieme di tanti piccoli fattori, un modello che li guarda tutti insieme dovrebbe
riconoscere il giorno di nascita vero di chi ha avuto depressione, suicidio o dipendenze.
**Risultato: indovina come una moneta.**

![Tutte le prove](grafici/t3_tutte_le_prove.png)

## Impostazione

- **Compito**: per ogni persona ci sono 6 date, quella vera e 5 finte. Il modello deve trovare quella vera.
  - confronto **giorni**: le finte sono spostate di ±1-15 giorni (si muove soprattutto la Luna);
  - confronto **anni**: stesso giorno dell'anno, ±1-5 anni, con solo i pianeti personali, perché Giove e gli altri
    pianeti lenti insegnerebbero al modello l'anno invece del cielo.
- **Fattori**: 363 in tutto: segni di tutti i pianeti, dignità, aspetti fra tutte le coppie, compensazione
  secondo Lisa Morpurgo, conteggi di quadrati, trigoni e opposizioni.
- **Modelli**: regressione logistica, alberi (gradient boosting), rete neurale su GPU, e i tre modelli combinati.
- **Compensazione imparata** (`ml_accorto.py`, modello A): i pesi non sono scelti a mano. Il modello impara un peso per
  ogni combinazione pianeta personale × aspetto × dignità dell'altro pianeta.
- **Prova del caso**: lo stesso modello su dati in cui la data "vera" è scelta a caso, da 50 a 1.000 volte.
- **Verifica**: si scopre su una metà delle persone e si controlla sull'altra. In `ml_accorto.py` si impara su ~8.000
  persone e si verifica una sola volta su ~1.900 persone nuove.
- **Coda**: si controlla anche il 2% di date più "sospette", nel caso il segnale stia in poche persone.

## Risultati

![Tutto insieme](grafici/3_tutto_insieme.png)

Aspetti e coppie che sembravano più presenti, verificati su altre persone:

![Aspetti nascosti](grafici/4_aspetti_nascosti.png)
![Coppie](grafici/5_coppie.png)

Confronto **anni**, solo pianeti personali: due modelli sono un po' fuori dal caso (p 0,04), ma su 8 prove può
succedere. È un indizio debole, da replicare su dati nuovi.

![Altri anni](grafici/ml_veloci.png)

## Lezioni da chi ci ha già provato

- Confrontare **gruppi diversi** (per esempio sportivi contro scienziati) fa uscire sempre qualcosa (55-58%), perché
  quei gruppi differiscono per epoca, ceto e stagione di nascita. Confrontando la persona con sé stessa si resta a ~50%.
- Con poche decine di temi il machine learning impara il rumore.
- Senza la prova del caso qualsiasi accuratezza sembra un successo.

## File

| File | Contenuto |
|---|---|
| `analisi/multifattore.py` | 363 fattori, modelli, prova del caso, ricerca libera su metà A e metà B |
| `analisi/coppie.py` | coppie di fattori e compensazione nelle due direzioni (test di Poisson per gli eventi rari) |
| `analisi/ml_accorto.py` | piano fissato prima, impara sulle persone vecchie e verifica su quelle nuove, compensazione imparata, modelli composti |
| `analisi/contesto_vs_cielo.py` | contesto (paese, mestiere, fama, soldi) contro cielo |
| `risultati/` | risultati in JSON |

Dipendenze: `pip install pyswisseph scikit-learn scipy numpy` (e `torch` per la rete neurale).
I dati vengono dal repo **statistiche** (`scarica_wikidata.py`).

## Verifica finale su persone nuove (`ml_accorto.py`)

Piano fissato prima di guardare: il modello impara su 8.253 persone e viene verificato **una sola volta** su 1.552
persone nuove, mai viste (dal testo di Wikipedia). Ci sono 4 modelli (compensazione imparata, tutti i fattori, alberi,
composti) per 2 confronti (giorni, anni), con la correzione di Holm sugli 8 test.

![Verifica finale](grafici/ml_accorto.png)

**Tutti e 8 = caso** (AUC 48,6–50,7 su 100, p corretto = 1). L'indizio del confronto "anni" non si ripete.
Pesi imparati per la compensazione: domicilio +0,03, caduta −0,03, quindi nella direzione di Morpurgo. Ma la
regolarizzazione li schiaccia verso 0 e il modello non riconosce le persone nuove: sono rumore.

## Contesto contro cielo

Contesto: paese, mestiere, sesso, fama (numero di Wikipedia), patrimonio, titolo nobiliare, università, decennio di nascita.
Controllo: persone famose nate negli stessi anni, scelte a caso.

![Contesto contro cielo](grafici/grafico_contesto.png)

Il contesto da solo riconosce il gruppo 76 volte su 100. Il cielo da solo 56, ma tra persone diverse il cielo misura
anche l'epoca e le date "segnaposto" del 1° gennaio, quindi non è un segnale. Quando il cielo si aggiunge al contesto
non migliora niente (0,751 contro 0,751 con il cielo rimescolato, p = 0,52).

## Luna con le probabilità (ora di nascita ignota)

Invece di escludere le persone con la Luna incerta (circa il 40% dei giorni), ogni condizione pesa per la frazione delle
24 ore in cui è vera. Tornano tutte le persone, e il test è più sensibile.

![Luna con le probabilità](grafici/prob_luna.png)

Nessuna ipotesi regge la correzione per i 20 confronti. "Luna debole" (esilio o caduta secondo le dignità) esce meno
spesso del previsto, cioè al contrario dell'ipotesi, nei suicidi (p 0,048), in alcol e droghe (p 0,011) e in tutti
(p 0,032). I gruppi si sovrappongono, quindi non sono tre conferme indipendenti. Da replicare sulle persone nuove.

## Potenza: quanto serve per vedere un effetto

Effetto minimo che il test trova 8 volte su 10 (p < 0,05):

| Condizione (frequenza) | 500 persone | 2.000 | 10.000 | 50.000 |
|---|---|---|---|---|
| Luna in Pesci (8,3%) | +48% | +24% | +11% | +5% |
| Luna debole (11%) | +41% | +21% | +9% | +4% |
| Luna quadrato Giove (2%) | +97% | +49% | +22% | +10% |
| aspetto raro (0,5%) | +194% | +97% | +43% | +19% |

Con i 7.000 suicidi il test vede effetti del 10-12% sulla Luna; con i gruppi piccoli solo effetti del 30-40%.

## Pesi della compensazione scelti dai dati, con pochi parametri

`analisi/pesi_pochi_parametri.py`: invece di 125 pesi, solo 10: uno per ogni aspetto (5) e uno per ogni dignità (5),
moltiplicati. Perdita del case-crossover (la data vera contro le sue 5 finte), regolarizzazione scelta con una
divisione interna, 3 divisioni ripetute per persona, prova del caso con 10 rimescolamenti.

Su 3.000 persone: **AUC 0,498** (il caso è 0,500), prima scelta giusta 16,8% (caso 16,7%), p = 0,36.
Pesi imparati: opposizione +1,0, congiunzione +0,43, quadrato −0,13, trigono −0,04; domicilio +0,07, esaltazione +0,11,
caduta +0,09, esilio −0,04. Non seguono la regola di Morpurgo (domicilio ed esaltazione positivi, esilio e caduta
negativi) e nessuno si distingue dal rumore.

Con una regolarizzazione troppo forte i pesi di dignità vanno a zero e il modello non può imparare niente: nella
prova a 300 persone il risultato era quello. Va scelta con attenzione.

**Conclusione sui numeri scelti dai dati**: né con 125 parametri, né con 10, né su persone nuove i pesi riconoscono le
persone meglio del caso.
