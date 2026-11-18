---
name: apertura-ticket
description: >-
  Usa quando un dipendente vuole aprire un ticket di assistenza per il reparto IT. Raccoglie in
  modo guidato nome, cognome, email, tipologia e descrizione del problema, li valida e mostra un
  riepilogo da confermare.
license: MIT
metadata:
  version: 1.0.0
  scenario: Zava S.p.A. - Help Desk di primo livello
---
# Apertura di un ticket IT

Usa questa procedura quando l'utente chiede esplicitamente di aprire un ticket, oppure quando la
skill supporto-tecnico consiglia l'escalation e l'utente accetta.

## Dati da raccogliere

| Campo | Regola |
| --- | --- |
| Nome | Obbligatorio |
| Cognome | Obbligatorio |
| Email | Obbligatoria, deve avere un formato valido (nome@dominio) |
| Tipologia | Obbligatoria, una tra: Hardware, Software, Rete, Altro |
| Descrizione | Obbligatoria, massimo 2.000 caratteri: sintomi, quando succede, messaggi di errore |

## Passaggi

1. Riusa i dati già presenti nella conversazione (ad esempio il riepilogo di supporto-tecnico):
   non chiedere di nuovo ciò che l'utente ha già detto.
2. Chiedi i campi mancanti tutti insieme, in un unico messaggio con un elenco puntato.
3. Valida le risposte. Se l'email non è valida o la tipologia non è tra quelle ammesse, chiedi di
   correggere solo il campo sbagliato.
4. Mostra il riepilogo in una tabella con le colonne Campo e Valore e chiedi: "Confermi l'invio
   del ticket al reparto IT?".
5. Se l'utente conferma, rispondi che il ticket è pronto per l'invio e riporta il riepilogo. Se
   l'utente annulla, conferma l'annullamento e non conservare i dati.

## Regole

- Non chiedere informazioni personali diverse da quelle elencate.
- Non inventare valori: se un campo manca, chiedilo.
- Non dichiarare mai che il ticket è stato registrato in un sistema: in questa versione la skill
  prepara il ticket ma non lo invia.
