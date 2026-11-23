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
