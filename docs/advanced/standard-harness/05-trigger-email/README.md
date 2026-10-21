# Lab S05 - Trigger autonomo via email

[Previous: S04](../04-grounding-e-valutazione/README.md) | [Back to Standard Harness](../index.md) | [Next: S06](../06-dossier-word/README.md)

> [!NOTE]
> Harness: **standard**. Tempo stimato: 75 minuti. Parti di questo laboratorio sono adattate da Microsoft Agent Academy (https://github.com/microsoft/agent-academy), Copyright (c) Microsoft Corporation, licenza MIT.

## Contesto

Molti proponenti non usano la chat: inviano il business case alla casella del PMO con un oggetto che inizia con "Proposta progetto". Oggi qualcuno controlla la casella, scarta risposte automatiche e newsletter, registra le proposte e avvisa i colleghi. Vogliamo che succeda da solo.

In questo laboratorio aggiungi all'Agente Demand IT un **trigger su evento**: quando arriva un'email, un flow di Power Automate la classifica, registra le proposte in PDF, e chiede all'agente di analizzarle e di avvisare il PMO in Teams con una **adaptive card**.

## Perché questa scelta

- **Trigger dell'agente invece di un flow separato.** Il trigger nasce dall'agente e invia all'agente un messaggio da elaborare: l'agente usa gli stessi strumenti della chat (analisi del documento) senza duplicare la logica.
- **La parte deterministica nel flow, la parte di giudizio nell'agente.** Filtrare gli allegati PDF, creare la riga, caricare il file sono passi fissi: li fa Power Automate. Analizzare il documento e scegliere che cosa comunicare li fa l'agente.
- **Due livelli di filtro: regole nel trigger, giudizio nel prompt.** Il primo livello è il trigger: **Subject Filter** `Proposta progetto` e **Only with Attachments** scartano gratis e in modo deterministico la gran parte dei messaggi (fuori ufficio senza allegati, newsletter, posta generica). Il secondo livello è un piccolo prompt che legge i messaggi rimasti, prima che venga creato qualsiasi record. Serve per i casi che le regole non possono distinguere: una domanda sul processo con un documento in bozza (da far verificare a una persona), una notifica di mancato recapito che contiene il messaggio originale come allegato, una risposta nella stessa conversazione ("RE: Proposta progetto") con un allegato che non è un business case. Nel percorso GitHub Copilot lo stesso ruolo lo svolge il nodo **Classify** del workflow.
- **Nessuna decisione autonoma irreversibile.** Quando l'agente lavora da solo non c'è nessuno a cui chiedere conferma: per questo l'automazione registra e analizza, ma **non** crea valutazioni. La valutazione richiede la conferma del programma da parte di un analista (S04).
- **Un'email per proposta, un'esecuzione per email.** L'impostazione **Split On** fa partire un'esecuzione per ogni messaggio, anche se ne arrivano diversi insieme.

## Obiettivi

1. Creare un prompt di classificazione delle email.
2. Aggiungere il trigger **When a new email arrives (V3)** all'agente e modificarlo in Power Automate.
3. Registrare le proposte ricevute per email e passare il codice all'agente.
4. Creare un agent flow che pubblica una adaptive card in Teams.
5. Provare il processo con le email di prova.

## Prerequisiti

- Laboratori S01-S04 completati.
- Una casella di posta del tenant di laboratorio (la tua) e accesso a Microsoft Teams.
- L'indirizzo dell'app **PMO Demand Hub** annotato nel Lab 00.
- Le email di prova in [`materiali/email`](../../../resources/advanced/email/).
- Un team in Microsoft Teams per il PMO, ad esempio `Zava PMO`, con un canale `Proposte` in cui il flow pubblicherà le notifiche. Per crearli: in Teams seleziona **Teams**, **+** (**Join or create a team**), **Create team**, nome `Zava PMO`; poi, nel team, **...**, **Add channel**, nome `Proposte`.

> [!NOTE]
> Per i partecipanti al corso il team `Zava PMO` con il canale `Proposte` è già creato nel loro Teams: verifica solo di vederlo e passa al passo 1.

## Passo 1 - Prompt "Classifica email PMO"

Non tutto ciò che arriva nella casella del PMO è una proposta, anche se l'oggetto contiene "Proposta progetto": risposte automatiche e newsletter usano le stesse parole. Un prompt di classificazione legge oggetto e testo e restituisce una sola parola, facile da usare in una condizione del flow.

1. **Tools**, **New tool**, **Prompt**, nome `Classifica email PMO`.
2. Istruzioni:

```text
Classifica un'email ricevuta dalla casella dell'Ufficio Demand e PMO IT di Zava. Rispondi con una sola parola tra le seguenti, senza altro testo.

Proposta: il mittente presenta una o più proposte di progetto IT e allega il business case, anche se inoltra il documento per conto di altri. Non scegliere questa categoria per risposte automatiche, per messaggi promozionali o quando il mittente dice che non sta presentando una proposta.
RispostaAutomatica: messaggio generato da un sistema e non da una persona: avviso di assenza, ferie o fuori ufficio, notifica di mancato recapito, conferma automatica di lettura o ricezione, anche se l'oggetto contiene "Proposta progetto" o il messaggio riporta l'allegato originale.
NonPertinente: newsletter, promozioni, spam o contenuti estranei al processo delle proposte.
Incerta: il messaggio non rientra chiaramente in nessuna delle categorie precedenti, ad esempio una domanda sul processo con un documento in bozza.

Oggetto: /Oggetto
Testo: /Testo
```

3. Crea gli input di testo `Oggetto` e `Testo` con valori di esempio presi da `email-02-risposta-automatica.txt`. Lascia l'output su **Text**.
4. Seleziona **Test** e prova i testi delle email 01, 02, 03 e 04: devi ottenere Proposta, RispostaAutomatica, NonPertinente e Incerta. Se una categoria è sbagliata, rendi più precisa la descrizione e riprova.
5. Seleziona **Save** (annulla l'eventuale configurazione come strumento).

![](./images/passo1-extra-01.png)

## Passo 2 - Aggiungere il trigger all'agente

Il trigger permette all'agente di lavorare senza che nessuno apra la chat: quando arriva un'email, parte un flow che può chiamare l'agente. Il filtro sull'oggetto e sugli allegati applica fin da subito le regole delle linee guida e riduce le esecuzioni inutili.

1. Apri l'**Agente Demand IT**, pagina **Overview**, sezione **Triggers**, e seleziona **Add trigger** (o **+ Add**).
2. Seleziona **When a new email arrives (V3)** e **Next**.

![](./images/passo2-extra-02.png)

3. **Trigger name**:

```text
Nuova proposta via email
```

![](./images/passo2-extra-03.png)

4. Verifica che le connessioni abbiano il segno di spunta verde (altrimenti crea una nuova connessione dal menu **...**) e seleziona **Next**.
5. Imposta i parametri:

| Parametro             | Valore              |
| --------------------- | ------------------- |
| Include Attachments   | Yes                 |
| Subject Filter        | `Proposta progetto` |
| Only with Attachments | Yes                 |

![](./images/passo2-extra-04.png)

> [!NOTE]
> Questi parametri sono il **primo livello** di filtro: costano nulla e tolgono la maggior parte del rumore. Non bastano da soli, perché non sanno leggere il contenuto: un'email con l'oggetto giusto e un allegato può essere una domanda, una notifica di mancato recapito o una risposta nella conversazione. Per questi casi aggiungerai al passo 3 il **secondo livello**, il prompt **Classifica email PMO**.

6. Seleziona **Create trigger** e poi **Close**. Il trigger compare nella sezione **Triggers**.

![](./images/passo2-extra-05.png)
## Passo 3 - Modificare il flow in Power Automate

Il flow generato dal trigger inoltra tutto all'agente. Prima di farlo vuoi decidere che cosa merita di arrivarci: classifichi l'email, scarti ciò che non è una proposta, registri ogni PDF allegato e solo allora chiedi all'agente di completare il lavoro. È qui che le regole del PMO diventano passi ripetibili.

1. Accanto al trigger seleziona **...** e poi **Edit in Power Automate**. Il flow contiene il trigger e l'azione **Sends a prompt to the specified copilot for processing**.

![](./images/passo3-extra-06.png)

![](./images/passo3-extra-07.png)

2. Apri le **Settings** del trigger, attiva **Split On** e imposta `@triggerOutputs()?['body/value']`: ogni email avvia un'esecuzione separata.

![](./images/passo3-extra-08.png)

3. Sotto il trigger aggiungi **Html to text** (connettore Content Conversion; crea la connessione se richiesto) con **Content** = contenuto dinamico **Body**.

![](./images/passo3-extra-09.png)

![](./images/passo3-extra-10.png)

4. Aggiungi **Run a prompt**, rinominalo `Classifica`, prompt **Classifica email PMO**, **Oggetto** = **Subject**, **Testo** = output di **Html to text**.

![](./images/passo3-extra-11.png)

5. Aggiungi **Condition** `Proposta rilevata`: a sinistra il contenuto dinamico **Text** di **Classifica**, operatore **contains**, a destra `Proposta`.

![](./images/passo3-extra-12.png)

   > [!NOTE]
   > Usiamo **contains** invece di **is equal to** per tollerare spazi o un a capo nella risposta del modello. Le altre categorie non contengono la parola "Proposta".

6. Nel ramo **True** aggiungi una **Condition** e rinominala `Allegato PDF`. Nel campo del valore scegli il contenuto dinamico **Attachments Content-Type**: Power Automate crea automaticamente un ciclo **For each** sugli allegati, che puoi rinominare `Per ogni allegato`. Imposta l'operatore **is equal to** e il valore `application/pdf`.

![](./images/passo3-extra-13.png)

7. Nel ramo **True** di **Allegato PDF** aggiungi:
   - **Add a new row** `Registra proposta email`, tabella **Proposals**: **Title** = espressione `item()?['name']`; **Cover Message** = espressione `if(greater(length(string(body('Html_to_text'))), 4000), substring(string(body('Html_to_text')), 0, 4000), string(body('Html_to_text')))`; **Source Email** = **From**; **Channel** = **Email**; **Proposal Status** = **Received**; **Submission Date** = `formatDateTime(utcNow(), 'yyyy-MM-dd')`;

![](./images/passo3-extra-14.png)


     > [!NOTE]
     > L'espressione di **Cover Message** cita l'azione **Html to text** come `Html_to_text`. Se nel tuo flow ha un nome diverso (ad esempio `Html_to_text_1` o un nome scelto da te), sostituiscilo nei tre punti dell'espressione, con `_` al posto degli spazi.

   - **Upload a file or an image** `Carica documento email`: **Content name** = `item()?['name']`, **Table name** = **Proposals**, **Row ID** = **Proposal** di **Registra proposta email**, **Column Name** = **Business Case Document**, **Content** = `item()?['contentBytes']`.

![](./images/passo3-extra-15.png)

8. Trascina l'azione **Sends a prompt to the specified copilot for processing** sotto **Carica documento email**, dentro il ramo **True**. 

![](./images/passo3-extra-16.png)

9. Nel campo **Body/message** cancella il contenuto e incolla:

```text
Analizza la proposta CODICE PROPOSTA ricevuta via email da MITTENTE con oggetto OGGETTO e poi notifica il PMO in Teams con lo strumento Notifica PMO in Teams.
```

   Sostituisci `CODICE PROPOSTA` con il contenuto dinamico **Proposal Code** di **Registra proposta email**, `MITTENTE` con **From** e `OGGETTO` con **Subject**.

![](./images/passo3-extra-17.png)

9. Torna al ramo **False** della prima condizione (**Proposta rilevata**). Aggiungi una **Condition** `Da verificare`: **Text** di **Classifica** **contains** `Incerta`. 

![](./images/passo3-extra-18.png)

10. Nel ramo **True** aggiungi **Send an email (V2)**, rinominala `Avvisa verifica manuale`: **To** il tuo indirizzo, **Subject** `Email PMO da verificare manualmente`. Nel campo **Body** seleziona l'icona **</>** (Code view), incolla il codice seguente e sostituisci i segnaposto con il contenuto dinamico: `[MITTENTE]` con **From**, `[OGGETTO]` con **Subject**, `[TESTO]` con l'output di **Html to text**. Le email RispostaAutomatica e NonPertinente non producono azioni.

```html
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;margin:16px auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);overflow:hidden;">
  <div style="height:6px;background:#f59e0b;"></div>
  <div style="padding:20px 24px;">
    <div style="font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.06em;">PMO Demand Hub · Da verificare</div>
    <div style="font-size:18px;font-weight:600;color:#111827;margin:6px 0 14px;">[OGGETTO]</div>
    <div style="font-size:13px;color:#374151;margin-bottom:14px;">Da <strong>[MITTENTE]</strong></div>
    <div style="font-size:13px;line-height:1.55;color:#374151;background:#f9fafb;border-radius:8px;padding:12px 14px;white-space:pre-wrap;">[TESTO]</div>
    <div style="font-size:12px;color:#6b7280;margin-top:14px;">La classificazione non è sicura che sia una proposta: nessun record è stato creato.</div>
  </div>
</div>
```

> [!TIP]
> Gli stili sono scritti nei tag perché Outlook ignora i fogli di stile. Dopo aver incollato l'HTML il campo resta in vista codice: è normale, l'editor visuale non gestisce questo tipo di formattazione. Puoi comunque sostituire i segnaposto con il contenuto dinamico (icona del fulmine o `/`).

![](./images/passo3-extra-19.png)

11. Seleziona **Save** e poi Publish.

![](./images/passo3-extra-20.png)

12. Torna ai dettagli del flow, seleziona **Edit** nella sezione **Details** e imposta **Plan** su **Copilot Studio**, poi **Save**: il flow userà la capacità di Copilot Studio invece di Power Automate.

![](./images/passo3-extra-21.png)

> [!TIP]
> Il ciclo sugli allegati gestisce anche email con più business case (prova `email-05-due-proposte.txt`): ogni PDF diventa una proposta distinta. Il file Word dello stesso messaggio viene ignorato dalla condizione: in un processo reale conviene avvisare il mittente di inviarlo in PDF.

## Passo 4 - Agent flow "Notifica PMO in Teams"

Una proposta arrivata di notte deve comparire davanti a un analista la mattina dopo. Una scheda in Teams con codice, proponente e programma, e un pulsante che apre l'app, rende visibile l'arrivo senza dover controllare Dataverse.

1. Apri **Intake Proposte**, **Tools**, **Add**, **New tool**, **Agent flow**.

![](./images/passo4-extra-22.png)

2. Input di testo del trigger: `CodiceProposta`, `Title`, `Requester`, `Program`, `Avvisi`.

![](./images/passo4-extra-23.png)

3. Aggiungi l'azione Microsoft Teams **Post card in a chat or channel**, accedi se richiesto e imposta:
   - **Post as**: **Flow bot**;
   - **Post in**: **Chat with Flow bot** (oppure **Channel**, se hai un team del PMO);
   - **Recipient**: il tuo account, selezionato dall'elenco.
4. Nel campo **Adaptive Card** incolla il JSON sotto, poi sostituisci i testi in maiuscolo con il contenuto dinamico degli input e `INDIRIZZO-APP` con l'indirizzo dell'app PMO Demand Hub annotato nel Lab 00 (fino al parametro `appid` incluso):

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    { "type": "TextBlock", "text": "Nuova proposta ricevuta via email", "weight": "Bolder", "size": "Medium", "wrap": true },
    { "type": "TextBlock", "text": "Registrata e analizzata automaticamente dall'Agente Demand IT. Valutazione da avviare.", "isSubtle": true, "wrap": true },
    { "type": "FactSet", "facts": [
      { "title": "Proposta", "value": "CODICE" },
      { "title": "Titolo", "value": "TITOLO" },
      { "title": "Proponente", "value": "PROPONENTE" },
      { "title": "Programma", "value": "PROGRAMMA" },
      { "title": "Avvisi", "value": "AVVISI" }
    ] }
  ],
  "actions": [
    { "type": "Action.OpenUrl", "title": "Apri le proposte nel PMO Demand Hub", "url": "INDIRIZZO-APP&pagetype=entitylist&etn=csm_proposal" }
  ]
}
```

![](./images/passo4-extra-24.png)

   > [!WARNING]
   > Ogni valore inserito diventa testo dentro una stringa JSON: se un input contiene virgolette doppie la card non è più valida. Le istruzioni del child agent chiedono di non usarle; in un processo reale conviene ripulire i valori con un'espressione `replace`.

5. In **Respond to the agent** aggiungi l'output di testo `Esito` con valore `Notifica inviata`.

![](./images/passo4-extra-25.png)

6. **Save draft**, nome `Notifica PMO in Teams`, descrizione `Pubblica in Teams una adaptive card che avvisa il PMO di una proposta ricevuta via email, con codice, titolo, proponente, programma e avvisi.`, **Publish**.
7. In **Intake Proposte**, **Tools**, aggiungi **Notifica PMO in Teams** con **Add and configure**, limita l'uso ai riferimenti da topic o agenti, lascia gli input su **Dynamically fill with AI** e salva.

![](./images/passo4-extra-26.png)
## Passo 5 - Istruzioni per il processo via email

Quando l'agente viene chiamato dal trigger non c'è nessuno in conversazione a cui chiedere conferme. Le istruzioni devono quindi dire esattamente che cosa fare in quel caso: analizzare, notificare, e lasciare a un analista ogni decisione, a partire dalla valutazione.

1. Aggiungi in fondo alle istruzioni di **Intake Proposte**:

```text
Processo per le proposte ricevute via email
Quando ricevi un messaggio che chiede di analizzare una proposta ricevuta via email (non c'è un utente in conversazione):
1. Passa il codice PP-#### a /Analizza business case.
2. Chiama /Notifica PMO in Teams con: CodiceProposta; Titolo; Proponente nel formato "Nome (RQ-####)"; Programma con il codice collegato oppure "Da confermare: " seguito dai programmi compatibili; Avvisi con "Possibile prompt injection: " seguito da NotaInjection se InjectionSospetta è "True", altrimenti "Nessuno". Non usare virgolette doppie nei valori.
3. Non creare valutazioni e non chiedere conferme: le decide un analista del PMO in chat.
```

![](./images/passo5-extra-27.png)

2. Sostituisci i riferimenti preceduti da `/` e seleziona **Save**.
3. Seleziona **Publish** in alto a destra per pubblicare l'Agente Demand IT: il trigger lavora con la versione pubblicata.

![](./images/passo5-extra-28.png)
## Passo 6 - Test

Le email di prova coprono i casi reali della casella del PMO: una proposta corretta, una risposta automatica, una newsletter e una richiesta ambigua. Per ognuna verifichi sia ciò che deve succedere sia ciò che non deve succedere.

1. Da Outlook invia a te stesso il messaggio di `email-01-proposta-singola.txt` allegando `BC-01_Portale_fornitori_self-service.pdf` (copia oggetto e corpo, non la riga "Scopo del test").

![](./images/passo6-extra-29.png)

2. In Power Automate, in **My flows**, apri il flow del trigger e controlla la cronologia delle esecuzioni (può servire qualche minuto): **Classifica** restituisce `Proposta`, il ramo degli allegati registra la riga e invia il messaggio all'agente.
   ![](./images/passo6-extra-30.png)
   
3. In Copilot Studio, nell'Agente Demand IT, apri **Activity**: compare una sessione automatica. Selezionala e segui nella mappa la chiamata a **Analizza business case** e a **Notifica PMO in Teams**.
   
   ![](./images/passo6-extra-31.png)
   
2. In Teams apri la chat con **Workflows** (Flow bot): la card riporta codice, titolo, proponente e programma. Il pulsante apre l'elenco delle proposte.

![](./images/passo6-extra-32.png)
![](./images/passo6-extra-33.png)

3. Invia i messaggi di `email-02-risposta-automatica.txt` e `email-03-newsletter.txt` **con un PDF allegato**: le esecuzioni terminano senza creare proposte. L'allegato serve a farli passare dal primo livello (oggetto e allegati), così vedi lavorare il secondo: è la situazione di una notifica di mancato recapito o di una newsletter che cita "Proposta progetto" e porta un documento.
4. Invia `email-04-richiesta-ambigua.txt`: ricevi l'email "Email PMO da verificare manualmente" e nessuna proposta viene creata.

## Verifica

1. Solo le email classificate come Proposta creano righe in **Proposals**, con **Channel** Email.
2. Ogni proposta ricevuta via email viene analizzata (titolo, proponente, programma) e notificata in Teams.
3. Nessuna valutazione viene creata dall'automazione.

## Cosa hai imparato

- Come un trigger dell'agente viene esteso in Power Automate e invia un messaggio all'agente.
- Come classificare un input con un prompt prima di scrivere dati.
- Come pubblicare una adaptive card in Teams da un agent flow.
- Perché un agente autonomo non deve prendere decisioni che richiedono una conferma umana.

## Riferimenti Microsoft Learn

- [Add an event trigger](https://learn.microsoft.com/microsoft-copilot-studio/authoring-triggers-about)
- [Office 365 Outlook connector](https://learn.microsoft.com/connectors/office365/)
- [Microsoft Teams connector](https://learn.microsoft.com/connectors/teams/)
- [Use your prompt in Power Automate](https://learn.microsoft.com/ai-builder/use-a-custom-prompt-in-flow)
