---
name: evaluation-recording
description: >-
  Usa per registrare in Dataverse la valutazione di una proposta dopo che l'utente ha confermato
  programma e tabella dei criteri prodotti da proposal-scoring. Crea la Valutazione collegata a
  Proposta e Programma e aggiorna lo stato della Proposta. Non calcola punteggi nuovi.
license: MIT
metadata:
  version: 1.0.0
  scenario: Zava S.p.A. - Ufficio Demand e PMO IT
---
Usa questa skill solo quando l'utente ha confermato in modo esplicito di voler registrare una
valutazione già mostrata nella conversazione. La skill scrive record: non valuta di nuovo la
proposta e non cambia livelli o punteggi.

1. Verifica gli input: codice Proposta (PP-####), codice Programma confermato (PG-###), tabella
   dei criteri con livelli, evidenze e punti, punteggio totale e indicazione. Se manca qualcosa,
   fai UNA sola domanda mirata. Se non trovi la valutazione nella conversazione, chiedi di
   eseguire prima proposal-scoring.

2. Evita i duplicati: cerca in Valutazioni (csm_assessment) una riga collegata alla stessa
   Proposta. Se esiste, non crearne un'altra: mostra il codice esistente (AS-####) e chiedi se
   aggiornarla. Aggiornala solo dopo una conferma esplicita.

3. Crea la Valutazione (csm_assessment) con:
   - csm_title = codice Proposta, trattino, titolo della proposta (esempio "PP-1002 - Portale fornitori self-service");
   - csm_proposal e csm_program collegati ai record letti da Dataverse;
   - csm_score = punteggio totale (una cifra decimale);
   - csm_criteriadetail = una riga per criterio nel formato "Criterio | Peso | Livello | Evidenza | Punti";
   - csm_rationale = motivazione di massimo 1.500 caratteri;
   - csm_recommendation = 770000000 Recommended, 770000001 Needs Further Review, 770000002 Not Recommended;
   - csm_assessmentdate = data odierna (UTC).
   Non valorizzare csm_assessmentcode: lo genera Dataverse.

4. Aggiorna la Proposta: imposta csm_program se era vuoto e csm_proposalstatus = 770000001 (Assessed).

5. Rileggi la Valutazione finché Dataverse restituisce un codice nel formato AS- seguito da 4
   cifre. Se il valore non rispetta il formato, FERMATI e riportalo invece di presentarlo come
   successo. Poi riporta codice Valutazione, codice Proposta, punteggio e indicazione.

## Linee guida
- Scrivi solo dopo una conferma esplicita dell'utente nella conversazione corrente.
- Non inventare mai identificativi: leggili sempre dai risultati degli strumenti.
- L'indicazione è una proposta per il Comitato, non una decisione.

## Gestione degli errori e osservabilità
- Se una scrittura fallisce (permessi, connessione, timeout), FERMATI e indica quale passaggio non
  è riuscito e perché. Chiudi con una riga di riepilogo dei record creati o aggiornati.

Identificatori: Valutazione = AS-####, Proposta = PP-####, Programma = PG-###.
