# Lab S05 - Trigger autonomo via email

[Previous: S04](../04-grounding-e-valutazione/README.md) | [Back to Standard Harness](../index.md) | [Next: S06](../06-dossier-word/README.md)

<!-- icon: clock-countdown --> **Tempo stimato:** ~75 minuti · <!-- icon: toolbox f-standard --> **Harness:** standard

## Scenario

Con S04 il ciclo in chat è completo: un business case allegato viene registrato, analizzato e valutato dopo la conferma di un analista. Il processo del PMO però nasce dalla casella email condivisa, dove le proposte arrivano in formati diversi e spesso senza tutte le informazioni richieste.

Questo lab aggiunge il secondo canale di ingresso dello schema generale di S01: le email passano da un flow che le filtra e registra le proposte, poi l'agente le analizza con gli stessi strumenti della chat e avvisa il PMO in Teams. La valutazione resta in chat, perché richiede la conferma di una persona del PMO.

Molti proponenti non usano la chat: inviano il business case alla casella del PMO con un oggetto che inizia con "Proposta progetto". Oggi qualcuno controlla la casella, scarta risposte automatiche e newsletter, registra le proposte e avvisa i colleghi. L'obiettivo è che succeda da solo.

In questo lab verrà aggiunto all'Agente Demand IT un **trigger su evento**: quando arriva un'email, un flow di Power Automate la classifica, registra le proposte in PDF e chiede all'agente di analizzarle e di avvisare il PMO in Teams con una **adaptive card**. In particolare verranno svolte le seguenti attività:

- Creare un prompt di classificazione delle email.
- Aggiungere il trigger **When a new email arrives (V3)** all'agente e modificarlo in Power Automate.
- Registrare le proposte ricevute per email e passare il codice all'agente.
- Creare un agent flow che pubblica una adaptive card in Teams.
- Provare il processo con le email di prova.

> [!NOTE]
> **Partecipanti al corso**
>
> La card arriva nella chat con **Flow bot** del proprio account: non serve creare team o canali. Per i partecipanti al corso il team `Zava PMO` con il canale `Proposte` è già creato nel loro Teams e si può usare, se si preferisce, per pubblicare la card nel canale (variante facoltativa della sezione *Agent flow "Notifica PMO in Teams"*).

::: details <!-- icon: lightbulb f-instructions --> Perché questa scelta
- **Trigger dell'agente invece di un flow separato.** Il trigger nasce dall'agente e invia all'agente un messaggio da elaborare: l'agente usa gli stessi strumenti della chat (analisi del documento) senza duplicare la logica.
- **La parte deterministica nel flow, la parte di giudizio nell'agente.** Filtrare gli allegati PDF, creare la riga, caricare il file sono passi fissi: li fa Power Automate. Analizzare il documento e scegliere che cosa comunicare li fa l'agente.
- **Due livelli di filtro: regole nel trigger, giudizio nel prompt.** Il primo livello è il trigger: **Subject Filter** `Proposta progetto` e **Only with Attachments** scartano gratis e in modo deterministico la gran parte dei messaggi (fuori ufficio senza allegati, newsletter, posta generica). Il secondo livello è un piccolo prompt che legge i messaggi rimasti, prima che venga creato qualsiasi record. Serve per i casi che le regole non possono distinguere: una domanda sul processo con un documento in bozza (da far verificare a una persona), una notifica di mancato recapito che contiene il messaggio originale come allegato, una risposta nella stessa conversazione ("RE: Proposta progetto") con un allegato che non è un business case. Nel percorso GitHub Copilot lo stesso ruolo lo svolge il nodo **Classify** del workflow.
- **Nessuna decisione autonoma irreversibile.** Quando l'agente lavora da solo non c'è nessuno a cui chiedere conferma: per questo l'automazione registra e analizza, ma **non** crea valutazioni. La valutazione richiede la conferma del programma da parte di un analista (S04).
- **Un'email per proposta, un'esecuzione per email.** L'impostazione **Split On** fa partire un'esecuzione per ogni messaggio, anche se ne arrivano diversi insieme.
:::

## Che cosa si costruisce

Lo schema mostra il flow del trigger costruito in questo lab: l'agente viene chiamato solo dopo la classificazione con il prompt **Classifica email PMO** e la registrazione di ogni PDF in Dataverse, e non crea valutazioni. Analisi del documento e notifica in Teams le svolge l'agente, con gli strumenti di **Intake Proposte**. Gli allegati che non sono PDF vengono ignorati; le email incerte producono un avviso per la verifica manuale; risposte automatiche e messaggi non pertinenti terminano senza azioni.

![Flow del trigger email: classificazione, registrazione dei PDF, chiamata all'agente e notifica del PMO in Teams](../../images/workflow-email-standard.svg)

## Prerequisiti

Per svolgere questo lab occorre avere:

- completato i laboratori S01-S04;
- una casella di posta del tenant di laboratorio (la propria) e accesso a Microsoft Teams;
- l'indirizzo dell'app **PMO Demand Hub** annotato nel Lab 00;
- le email di prova in [`resources/advanced/email`](../../../resources/advanced/email/);
- facoltativo: un team in Microsoft Teams per il PMO, ad esempio `Zava PMO`, con un canale `Proposte`, solo se si vuole pubblicare la card nel canale invece che nella chat con Flow bot. Per crearli: in Teams selezionare **Teams**, **+** (**Join or create a team**), **Create team**, nome `Zava PMO`; poi, nel team, **...**, **Add channel**, nome `Proposte`.

## Prompt "Classifica email PMO"

Non tutto ciò che arriva nella casella del PMO è una proposta, anche se l'oggetto contiene "Proposta progetto": risposte automatiche e newsletter usano le stesse parole. Un prompt di classificazione legge oggetto e testo e restituisce una sola parola, facile da usare in una condizione del flow.

### Creare il prompt di classificazione

1. Selezionare **Tools**, **New tool**, **Prompt** e inserire il nome:

```
Classifica email PMO
```

2. Copiare e incollare le seguenti istruzioni:

```text
Classifica un'email ricevuta dalla casella dell'Ufficio Demand e PMO IT di Zava. Rispondi con una sola parola tra le seguenti, senza altro testo.

Proposta: il mittente presenta una o più proposte di progetto IT e allega il business case, anche se inoltra il documento per conto di altri. Non scegliere questa categoria per risposte automatiche, per messaggi promozionali o quando il mittente dice che non sta presentando una proposta.
RispostaAutomatica: messaggio generato da un sistema e non da una persona: avviso di assenza, ferie o fuori ufficio, notifica di mancato recapito, conferma automatica di lettura o ricezione, anche se l'oggetto contiene "Proposta progetto" o il messaggio riporta l'allegato originale.
NonPertinente: newsletter, promozioni, spam o contenuti estranei al processo delle proposte.
Incerta: il messaggio non rientra chiaramente in nessuna delle categorie precedenti, ad esempio una domanda sul processo con un documento in bozza.

Oggetto: /Oggetto
Testo: /Testo
```

3. Creare gli input di testo `Oggetto` e `Testo` con valori di esempio presi da [`email-02-risposta-automatica.txt`](../../../resources/advanced/email/email-02-risposta-automatica.txt). Lasciare l'output su **Text**.
4. Selezionare **Test** e provare i testi delle email 01, 02, 03 e 04: si devono ottenere Proposta, RispostaAutomatica, NonPertinente e Incerta. Se una categoria è sbagliata, rendere più precisa la descrizione e riprovare.
5. Selezionare **Save** (annullare l'eventuale configurazione come strumento).

![](./images/passo1-extra-01.png)

## Trigger "Nuova proposta via email"

Il trigger permette all'agente di lavorare senza che nessuno apra la chat: quando arriva un'email, parte un flow che può chiamare l'agente. Il filtro sull'oggetto e sugli allegati applica fin da subito le regole delle linee guida e riduce le esecuzioni inutili.

### Aggiungere il trigger all'agente

1. Aprire l'**Agente Demand IT**, pagina **Overview**, sezione **Triggers**, e selezionare **Add trigger** (o **+ Add**).
2. Selezionare **When a new email arrives (V3)** e **Next**.

![](./images/passo2-extra-02.png)

3. Nel campo **Trigger name** inserire:

```text
Nuova proposta via email
```

![](./images/passo2-extra-03.png)

4. Verificare che le connessioni abbiano il segno di spunta verde (altrimenti creare una nuova connessione dal menu **...**) e selezionare **Next**.
5. Impostare i parametri:

| Parametro             | Valore              |
| --------------------- | ------------------- |
| Include Attachments   | Yes                 |
| Subject Filter        | `Proposta progetto` |
| Only with Attachments | Yes                 |

![](./images/passo2-extra-04.png)

> [!NOTE]
> **Primo livello di filtro**
>
> Questi parametri sono il **primo livello** di filtro: costano nulla e tolgono la maggior parte del rumore. Non bastano da soli, perché non sanno leggere il contenuto: un'email con l'oggetto giusto e un allegato può essere una domanda, una notifica di mancato recapito o una risposta nella conversazione. Per questi casi nel flow verrà aggiunto il **secondo livello**, il prompt **Classifica email PMO**.

6. Selezionare **Create trigger** e poi **Close**. Il trigger compare nella sezione **Triggers**.

![](./images/passo2-extra-05.png)

### Classificare l'email nel flow

Il flow generato dal trigger inoltra tutto all'agente. Prima di farlo occorre decidere che cosa merita di arrivarci: classificare l'email, scartare ciò che non è una proposta, registrare ogni PDF allegato e solo allora chiedere all'agente di completare il lavoro. È qui che le regole del PMO diventano passi ripetibili.

1. Accanto al trigger selezionare **...** e poi **Edit in Power Automate**. Il flow contiene il trigger e l'azione **Sends a prompt to the specified copilot for processing**.

![](./images/passo3-extra-06.png)

![](./images/passo3-extra-07.png)

2. Aprire le **Settings** del trigger, attivare **Split On** e impostare il valore seguente: ogni email avvia un'esecuzione separata.

```
@triggerOutputs()?['body/value']
```

![](./images/passo3-extra-08.png)

3. Sotto il trigger aggiungere **Html to text** (connettore Content Conversion; creare la connessione se richiesto) con **Content** = contenuto dinamico **Body**.

![](./images/passo3-extra-09.png)

![](./images/passo3-extra-10.png)

4. Aggiungere **Run a prompt**, rinominarlo `Classifica` e impostare: prompt **Classifica email PMO**, **Oggetto** = **Subject**, **Testo** = output di **Html to text**.

![](./images/passo3-extra-11.png)

5. Aggiungere una **Condition** e rinominarla `Proposta rilevata`: a sinistra il contenuto dinamico **Text** di **Classifica**, operatore **contains**, a destra `Proposta`.

![](./images/passo3-extra-12.png)

> [!NOTE]
> **Perché contains**
>
> Si usa **contains** invece di **is equal to** per tollerare spazi o un a capo nella risposta del modello. Le altre categorie non contengono la parola "Proposta".

### Registrare le proposte in PDF

1. Nel ramo **True** di **Proposta rilevata** aggiungere una **Condition** e rinominarla `Allegato PDF`. Nel campo del valore scegliere il contenuto dinamico **Attachments Content-Type**: Power Automate crea automaticamente un ciclo **For each** sugli allegati, che si può rinominare `Per ogni allegato`. Impostare l'operatore **is equal to** e il valore `application/pdf`.

![](./images/passo3-extra-13.png)

2. Nel ramo **True** di **Allegato PDF** aggiungere l'azione **Add a new row**, rinominarla `Registra proposta email`, tabella **Proposals**, e impostare le seguenti proprietà:

| Property        | How to Set                      | Details / Expression                                                                                                                                                       |
| --------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Title           | Expression (fx icon)            | `item()?['name']`                                                                                                                                                          |
| Cover Message   | Expression (fx icon)            | `if(greater(length(string(body('Html_to_text'))), 4000), substring(string(body('Html_to_text')), 0, 4000), string(body('Html_to_text')))`                                   |
| Source Email    | Dynamic data (thunderbolt icon) | **From**                                                                                                                                                                   |
| Channel         | Select                          | **Email**                                                                                                                                                                  |
| Proposal Status | Select                          | **Received**                                                                                                                                                               |
| Submission Date | Expression (fx icon)            | `formatDateTime(utcNow(), 'yyyy-MM-dd')`                                                                                                                                   |

![](./images/passo3-extra-14.png)

> [!NOTE]
> **Nome dell'azione Html to text**
>
> L'espressione di **Cover Message** cita l'azione **Html to text** come `Html_to_text`. Se nel proprio flow ha un nome diverso (ad esempio `Html_to_text_1` o un nome scelto liberamente), sostituirlo nei tre punti dell'espressione, con `_` al posto degli spazi.

3. Sotto **Registra proposta email** aggiungere l'azione **Upload a file or an image**, rinominarla `Carica documento email` e impostare le seguenti proprietà:

| Property     | How to Set                      | Details                                       |
| ------------ | ------------------------------- | --------------------------------------------- |
| Content name | Expression (fx icon)            | `item()?['name']`                             |
| Table name   | Select                          | **Proposals**                                 |
| Row ID       | Dynamic data (thunderbolt icon) | **Proposal** di **Registra proposta email**   |
| Column Name  | Select                          | **Business Case Document**                    |
| Content      | Expression (fx icon)            | `item()?['contentBytes']`                     |

![](./images/passo3-extra-15.png)

### Inviare la proposta all'agente

1. Trascinare l'azione **Sends a prompt to the specified copilot for processing** sotto **Carica documento email**, dentro il ramo **True**.

![](./images/passo3-extra-16.png)

2. Nel campo **Body/message** cancellare il contenuto e incollare:

```text
Analizza la proposta CODICE PROPOSTA ricevuta via email da MITTENTE con oggetto OGGETTO e poi notifica il PMO in Teams con lo strumento Notifica PMO in Teams.
```

3. Sostituire `CODICE PROPOSTA` con il contenuto dinamico **Proposal Code** di **Registra proposta email**, `MITTENTE` con **From** e `OGGETTO` con **Subject**.

![](./images/passo3-extra-17.png)

### Avvisare per le email da verificare

1. Tornare al ramo **False** della prima condizione (**Proposta rilevata**). Aggiungere una **Condition** e rinominarla `Da verificare`: **Text** di **Classifica** **contains** `Incerta`.

![](./images/passo3-extra-18.png)

2. Nel ramo **True** aggiungere **Send an email (V2)** e rinominarla `Avvisa verifica manuale`. Impostare **To** con il proprio indirizzo e **Subject** con:

```
Email PMO da verificare manualmente
```

3. Nel campo **Body** selezionare l'icona **</>** (Code view) e incollare il codice seguente:

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

4. Sostituire i segnaposto con il contenuto dinamico: `[MITTENTE]` con **From**, `[OGGETTO]` con **Subject**, `[TESTO]` con l'output di **Html to text**. Le email RispostaAutomatica e NonPertinente non producono azioni.

> [!TIP]
> **Stili e vista codice**
>
> Gli stili sono scritti nei tag perché Outlook ignora i fogli di stile. Dopo aver incollato l'HTML il campo resta in vista codice: è normale, l'editor visuale non gestisce questo tipo di formattazione. Si possono comunque sostituire i segnaposto con il contenuto dinamico (icona del fulmine o `/`).

![](./images/passo3-extra-19.png)

### Salvare e pubblicare il flow

1. Selezionare **Save** e poi **Publish**.

![](./images/passo3-extra-20.png)

2. Tornare ai dettagli del flow, selezionare **Edit** nella sezione **Details** e impostare **Plan** su **Copilot Studio**, poi **Save**: il flow userà la capacità di Copilot Studio invece di Power Automate.

![](./images/passo3-extra-21.png)

> [!TIP]
> **Email con più allegati**
>
> Il ciclo sugli allegati gestisce anche email con più business case (provare [`email-05-due-proposte.txt`](../../../resources/advanced/email/email-05-due-proposte.txt)): ogni PDF diventa una proposta distinta. Il file Word dello stesso messaggio viene ignorato dalla condizione: in un processo reale conviene avvisare il mittente di inviarlo in PDF.

## Agent flow "Notifica PMO in Teams"

Una proposta arrivata di notte deve comparire davanti a un analista la mattina dopo. Una scheda in Teams con codice, proponente e programma, e un pulsante che apre l'app, rende visibile l'arrivo senza dover controllare Dataverse.

### Creare l'agent flow

1. Aprire **Intake Proposte** e selezionare **Tools**, **Add**, **New tool**, **Agent flow**.

![](./images/passo4-extra-22.png)

2. Nel nodo del trigger aggiungere gli input di testo `CodiceProposta`, `Title`, `Requester`, `Program`, `Avvisi`.

![](./images/passo4-extra-23.png)

3. Aggiungere l'azione Microsoft Teams **Post card in a chat or channel**, accedere se richiesto e impostare:

| Property  | Value                                                                   |
| --------- | ----------------------------------------------------------------------- |
| Post as   | **Flow bot**                                                            |
| Post in   | **Chat with Flow bot** (oppure **Channel**, se si usa il canale `Proposte` del team `Zava PMO`) |
| Recipient | il proprio account, selezionato dall'elenco (con **Channel**: team `Zava PMO` e canale `Proposte`) |

4. Nel campo **Adaptive Card** incollare il JSON seguente:

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

5. Sostituire i testi in maiuscolo con il contenuto dinamico degli input e `INDIRIZZO-APP` con l'indirizzo dell'app PMO Demand Hub annotato nel Lab 00 (fino al parametro `appid` incluso).

![](./images/passo4-extra-24.png)

> [!WARNING]
> **Virgolette nei valori**
>
> Ogni valore inserito diventa testo dentro una stringa JSON: se un input contiene virgolette doppie la card non è più valida. Le istruzioni del child agent chiedono di non usarle; in un processo reale conviene ripulire i valori con un'espressione `replace`.

6. Selezionare il nodo **Respond to the agent** e aggiungere l'output di testo `Esito` con valore `Notifica inviata`.

![](./images/passo4-extra-25.png)

7. Selezionare **Save draft** e impostare nome e descrizione:
   - **Flow name**: `Notifica PMO in Teams`
   - **Description**: `Pubblica in Teams una adaptive card che avvisa il PMO di una proposta ricevuta via email, con codice, titolo, proponente, programma e avvisi.`
8. Selezionare **Publish**.

### Aggiungere lo strumento a Intake Proposte

1. In **Intake Proposte**, scheda **Tools**, aggiungere **Notifica PMO in Teams** con **Add and configure**.
2. Limitare l'uso ai riferimenti da topic o agenti, lasciare gli input su **Dynamically fill with AI** e salvare.

![](./images/passo4-extra-26.png)

## Istruzioni per il processo via email

Quando l'agente viene chiamato dal trigger non c'è nessuno in conversazione a cui chiedere conferme. Le istruzioni devono quindi dire esattamente che cosa fare in quel caso: analizzare, notificare, e lasciare a un analista ogni decisione, a partire dalla valutazione.

### Aggiornare le istruzioni di Intake Proposte

1. Aggiungere in fondo alle istruzioni di **Intake Proposte**:

```text
Processo per le proposte ricevute via email
Quando ricevi un messaggio che chiede di analizzare una proposta ricevuta via email (non c'è un utente in conversazione):
1. Passa il codice PP-#### a /Analizza business case.
2. Chiama /Notifica PMO in Teams con: CodiceProposta; Titolo; Proponente nel formato "Nome (RQ-####)"; Programma con il codice collegato oppure "Da confermare: " seguito dai programmi compatibili; Avvisi con "Possibile prompt injection: " seguito da NotaInjection se InjectionSospetta è "True", altrimenti "Nessuno". Non usare virgolette doppie nei valori.
3. Non creare valutazioni e non chiedere conferme: le decide un analista del PMO in chat.
```

![](./images/passo5-extra-27.png)

2. Nei punti in cui le istruzioni contengono un nome preceduto da `/`, sostituire il riferimento con lo strumento corrispondente e selezionare **Save**.
3. Selezionare **Publish** in alto a destra per pubblicare l'Agente Demand IT: il trigger lavora con la versione pubblicata.

![](./images/passo5-extra-28.png)

## Testare l'agente

Le email di prova coprono i casi reali della casella del PMO: una proposta corretta, una risposta automatica, una newsletter e una richiesta ambigua. Per ognuna occorre verificare sia ciò che deve succedere sia ciò che non deve succedere.

### Proposta ricevuta via email

1. Da Outlook inviare a se stessi il messaggio di [`email-01-proposta-singola.txt`](../../../resources/advanced/email/email-01-proposta-singola.txt) allegando [`BC-01_Portale_fornitori_self-service.pdf`](../../../resources/advanced/business-case/BC-01_Portale_fornitori_self-service.pdf) (copiare oggetto e corpo, non la riga "Scopo del test").

![](./images/passo6-extra-29.png)

2. In Power Automate, in **My flows**, aprire il flow del trigger e controllare la cronologia delle esecuzioni (può servire qualche minuto): **Classifica** restituisce `Proposta`, il ramo degli allegati registra la riga e invia il messaggio all'agente.

![](./images/passo6-extra-30.png)

3. In Copilot Studio, nell'Agente Demand IT, aprire **Activity**: compare una sessione automatica. Selezionarla e seguire nella mappa la chiamata a **Analizza business case** e a **Notifica PMO in Teams**.

![](./images/passo6-extra-31.png)

4. In Teams aprire la chat con **Workflows** (Flow bot), oppure il canale `Proposte` se si è scelto **Channel**: la card riporta codice, titolo, proponente e programma. Il pulsante apre l'elenco delle proposte.

![](./images/passo6-extra-32.png)

![](./images/passo6-extra-33.png)

5. Aprire l'app **PMO Demand Hub**, **Proposals**: la nuova proposta ha **Channel** Email. In **Assessments** non c'è nessuna valutazione per questa proposta: l'automazione non crea valutazioni.

### Email da scartare o da verificare

1. Inviare i messaggi di [`email-02-risposta-automatica.txt`](../../../resources/advanced/email/email-02-risposta-automatica.txt) e [`email-03-newsletter.txt`](../../../resources/advanced/email/email-03-newsletter.txt) **con un PDF allegato**: le esecuzioni terminano senza creare proposte.

> [!NOTE]
> **Perché allegare un PDF**
>
> L'allegato serve a far passare i messaggi dal primo livello di filtro (oggetto e allegati), così si vede lavorare il secondo: è la situazione di una notifica di mancato recapito o di una newsletter che cita "Proposta progetto" e porta un documento.

2. Inviare [`email-04-richiesta-ambigua.txt`](../../../resources/advanced/email/email-04-richiesta-ambigua.txt): si riceve l'email "Email PMO da verificare manualmente" e nessuna proposta viene creata.

> [!IMPORTANT]
> **Lab Completato**
>
> L'Agente Demand IT ora lavora anche senza chat: le email del PMO vengono classificate, le proposte registrate, analizzate e notificate in Teams. In questo lab si è visto:
>
> - come un trigger dell'agente viene esteso in Power Automate e invia un messaggio all'agente;
> - come classificare un input con un prompt prima di scrivere dati;
> - come pubblicare una adaptive card in Teams da un agent flow;
> - perché un agente autonomo non deve prendere decisioni che richiedono una conferma umana.
