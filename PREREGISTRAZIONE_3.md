# Terza verifica pre-registrata

Scritta **prima** di avere i dati. Persone: quelle trovate nelle categorie di Wikipedia inglese ("People with bipolar
disorder", "Suicides", "Deaths by drug overdose", "People with ADHD", "borderline", "PTSD"…) che **non** compaiono in
nessuna analisi precedente (né nei gruppi Wikidata, né nei test pre-registrati 1 e 2), con luogo di nascita e senza il
1° gennaio.

## Ipotesi primaria (una sola)

**H1.** La compensazione imparata dai dati (modello A di `ml_accorto.py`, addestrato **solo** sui gruppi iniziali, senza
cambiare niente) riconosce il giorno vero con AUC **maggiore di 0,5** nel confronto "±15 giorni". Una coda, p < 0,05.
Nelle due verifiche precedenti ha dato 51,7 e 48,0, quindi la media attesa se è solo rumore è 0,5.

## Altre ipotesi (Holm su 8)

Gli altri tre modelli di `ml_accorto.py` (B, C, D), nei due confronti (giorni, anni).

## Gruppi mai testati (esplorativi, FDR al 5%)

ADHD, borderline, PTSD: Luna in Pesci, Luna debole, Luna quadrato Nettuno, Luna quadrato Giove, Luna opposta al Sole,
con le probabilità. Servono solo a vedere se in un gruppo nuovo succede qualcosa di diverso, non a confermare.

## Come si leggono i risultati

- H1 con p < 0,05 su **tre** verifiche indipendenti su quattro: indizio da replicare con più dati.
- H1 non confermata: la compensazione imparata dai dati non riconosce le persone e l'ipotesi si chiude.
- Nessun gruppo nuovo che superi FDR: niente.

## Cosa non si fa

Non si cambiano modelli, soglie o gruppi dopo aver visto i dati. Se qualcosa non torna si scrive nel README e si
rifà un nuovo piano.
