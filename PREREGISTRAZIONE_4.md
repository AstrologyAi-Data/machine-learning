# Pre-registrazione 4: spazio allargato, lasso, coppie di segni

Scritta il 23/11/2026, prima di calcolare qualsiasi fattore nuovo e prima di guardare le persone nuove.

## Domanda
Con più fattori (coppie di segni, governanti in comune), un modello che sceglie da solo riconosce il giorno di nascita
vero di chi ha avuto depressione, suicidio o dipendenze meglio del caso?

## Dati
- **Imparare**: le persone già usate nelle prime tre verifiche (circa 11.500). Il modello non vede mai le persone nuove.
- **Verificare, una sola volta**: persone mai viste, trovate nelle categorie di Wikipedia in tedesco, francese, russo,
  spagnolo e italiano, tolte quelle già presenti negli altri gruppi (circa 1.200). Se la ricerca nel testo delle
  biografie è finita prima del lancio, si aggiungono le persone nuove che porta. Non dopo.
- Via il 1° gennaio. Luna a mezzogiorno locale, uguale per la data vera e per le finte.

## Fattori (circa 500)
I 363 già usati, più per ogni coppia di pianeti personali (Sole, Luna, Mercurio, Venere, Marte; 10 coppie):
distanza fra i segni (stesso segno, 1, 2, 3, 4, 5, 6 segni), stesso elemento, stessa modalità, governante in comune
(tabella di Morpurgo: Capricorno-Acquario, Sagittario-Pesci, Ariete-Scorpione, Toro-Bilancia, Gemelli-Vergine).

Aggiunta del 23/11/2026, prima del lancio e prima di ogni risultato: 10 conteggi di aspetti (totali, duri, morbidi,
congiunzioni, sestili e il numero di aspetti di ciascun pianeta personale). I fattori diventano circa 470.

## Modelli e test
Compito: fra la data vera e le 5 finte, trovare quella vera. Due confronti (giorni, anni; per gli anni solo pianeti
personali). Due modelli (lasso, alberi). Quattro test, AUC sulle persone nuove, una coda, **correzione di Holm sui 4**.
- **H1 (principale)**: lasso, confronto giorni, AUC > 0,5.
- Nullo: 1.000 rimescolamenti di quale data è la vera, dentro ogni persona nuova.
- Gli iperparametri si scelgono solo sulle persone vecchie.

## Stabilità
Il lasso viene riaddestrato su 20 sottoinsiemi del 80% delle persone vecchie. Un fattore conta come "tenuto" solo se
sta nel modello in almeno 16 volte su 20.

## Potenza
Con circa 1.200 persone nuove il test vede solo un AUC sopra circa 0,53. Un effetto più piccolo non si può escludere.

## Agenti che si contraddicono
Dopo i risultati, non prima: un agente propone cosa potrebbe essere un pattern, un secondo cerca di smontarlo
(correlazione fra fattori, persone doppie, epoca, date segnaposto). Non scelgono test né soglie: leggono solo i risultati.

## Cosa non si fa
Non si cambiano modelli, soglie o gruppi dopo aver visto i dati. Se qualcosa non torna si scrive nel README e si rifà
un nuovo piano.

## Risultati (15.827 persone nuove, mai viste; modello imparato su 11.531)

Piano rispettato, nessuna modifica dopo aver visto i dati. 473 fattori (coppie di segni, governanti in comune, conteggi di aspetti).

**H1 (lasso, confronto giorni): AUC 0,5000, p = 1,0. Non confermata.** Il lasso ha azzerato tutti i fattori: nessun fattore tenuto, nessuno stabile (16 volte su 20).

| Confronto | Modello | AUC | p | Holm (4 test) |
|---|---|---|---|---|
| giorni | lasso | 0,5000 | 1,00 | 1 |
| giorni | alberi | 0,4996 | 0,58 | 1 |
| anni | lasso | 0,4987 | 0,72 | 1 |
| anni | alberi | 0,5026 | 0,15 | 0,60 |

Nel confronto anni il lasso ha tenuto 89 fattori e non riconosce comunque le persone nuove: rumore.

**Conclusione**: quarta replica nulla, con più fattori e più persone. Con ~15.800 persone nuove il test vede un AUC sopra circa 0,51: un effetto più piccolo non si può escludere. Nota: la "compensazione" usata qui è la somma delle dignità, non la versione con le mancanze specifiche del segno; quest'ultima non è ancora stata testata.
