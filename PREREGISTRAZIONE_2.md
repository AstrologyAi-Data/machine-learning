# Seconda verifica pre-registrata

Scritta **prima** di guardare i dati. Persone: i casi nuovi trovati con QLever (Wikidata) che non erano in nessuna
analisi precedente (né nei gruppi Wikidata, né nel testo di Wikipedia, né nelle altre lingue), con luogo di nascita,
senza le date del 1° gennaio.

## Ipotesi primaria (una sola)

**H1.** La "Luna debole" (esilio o caduta secondo `dignities.py`) è **meno frequente** del previsto. Una coda,
p < 0,05. È la stessa ipotesi della prima verifica, che non si era confermata (102 contro 110 attese, p 0,21). Se anche
qui non si conferma, la si abbandona come indizio.

## Ipotesi secondarie (Holm su 4)

Luna in Pesci, Luna quadrato Nettuno, Luna quadrato Giove, Luna opposta al Sole (due code).

## Metodo

Identico alla prima verifica: Luna con le probabilità (24 punti nella giornata), data vera contro 5 date finte della
stessa persona (1-15 giorni), statistica (osservate − attese) / radice(attese).

## Machine learning

Gli stessi 4 modelli di `ml_accorto.py`, addestrati **solo** sulle persone dei gruppi iniziali, verificati **una volta**
sulle persone nuove, con 1.000 rimescolamenti e Holm su 8 test.

## Come si leggono i risultati

- H1 con p < 0,05 su due verifiche indipendenti: **indizio da replicare** con più dati. Non è una conferma.
- Altrimenti: "Luna debole meno frequente" era rumore.
