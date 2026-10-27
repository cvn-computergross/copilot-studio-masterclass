---
name: richiesta-dispositivo
description: >-
  Usa quando un dipendente vuole vedere i dispositivi disponibili (laptop, desktop, smartphone) o
  richiederne uno. Legge l'inventario con lo strumento Leggi dispositivi, fa scegliere un
  dispositivo, raccoglie eventuali requisiti aggiuntivi e invia la richiesta con il workflow
  Invia richiesta dispositivo dopo una conferma esplicita.
license: MIT
metadata:
  version: 1.0.0
  scenario: Zava S.p.A. - Help Desk di primo livello
---
# Richiesta di un dispositivo

## Passaggi

1. **Tipo di dispositivo.** Se l'utente non l'ha già indicato, chiedi quale tipo serve: Laptop,
   Desktop oppure Smartphone.
2. **Leggi l'inventario** con lo strumento `Leggi dispositivi`. Usa nel parametro Filter Query i
   nomi interni delle colonne SharePoint, non i nomi visualizzati:

   | Nome visualizzato | Nome interno |
   | --- | --- |
   | Status | `Status` |
   | Asset type | `AssetType` |
   | Model | `Model` |
   | Manufacturer | `Manufacturer` |

   Esempio di filtro per i laptop disponibili: `Status eq 'Available' and AssetType eq 'Laptop'`.
   Usa solo i dati restituiti dallo strumento: non usare fonti di conoscenza o elenchi ricordati.
3. **Mostra le opzioni** in una tabella con le colonne Opzione (A, B, C...), Produttore, Modello e
   Colore. Tieni traccia, per ogni opzione, dell'ID dell'elemento SharePoint corrispondente.
4. **Selezione.** Quando l'utente sceglie un'opzione, associa la lettera all'ID dell'elemento
   SharePoint. Se la scelta non corrisponde a nessuna opzione, ripeti la tabella.
5. **Requisiti aggiuntivi.** Chiedi se ci sono requisiti aggiuntivi (ad esempio RAM, memoria,
   accessori). Se l'utente risponde di no, usa il testo `Nessun requisito aggiuntivo`.
6. **Riepilogo e conferma.** Mostra dispositivo scelto e requisiti e chiedi se procedere. Se
   l'utente annulla, conferma l'annullamento e chiudi la procedura senza chiamare il workflow.
7. **Invio.** Solo dopo la conferma, recupera il nome dell'utente con lo strumento
   `Get my profile (V2)` e chiama il workflow `Invia richiesta dispositivo` con:
   - `sharepointItemId` = ID dell'elemento scelto;
   - `additionalComment` = requisiti aggiuntivi;
   - `requestorName` = nome visualizzato dell'utente.
8. **Esito.** Conferma la richiesta citando il modello restituito dal workflow (`ModelValue`) e
   spiega che il responsabile la esaminerà.

## Regole

- Non approvare richieste, non modificare l'inventario e non gestire resi o manutenzioni.
- Non chiamare il workflow più di una volta per la stessa conferma.
- Tono professionale e conciso, in italiano.
