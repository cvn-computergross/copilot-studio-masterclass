# Lab S02 - Sistema multi-agente

[Previous: S01](../01-agente-orchestratore/README.md) | [Back to Standard Harness](../index.md) | [Next: S03](../03-prompt-multimodale/README.md)

<!-- icon: clock-countdown --> **Tempo stimato:** ~90 minuti · <!-- icon: toolbox f-standard --> **Harness:** standard

Parti di questo laboratorio sono adattate da Microsoft Agent Academy (https://github.com/microsoft/agent-academy), Copyright (c) Microsoft Corporation, licenza MIT.

## Scenario

In S01 l'Agente Demand IT ha imparato a rispondere sulle regole del processo. Un proponente però vuole consegnare il suo business case, e oggi lo fa per email: un analista apre il documento, lo registra nel foglio Excel e, più avanti, organizza la revisione con sponsor e architetto. Questo lab porta in chat due passaggi del processo: la registrazione della proposta nel PMO Demand Hub e la preparazione della revisione.

Il sistema cresce secondo un principio che vale per tutto il percorso, il **minimo privilegio**: ogni agente riceve solo gli strumenti che gli servono. Il child agent dell'intake scrive nel PMO Demand Hub; lo specialista della revisione legge, non scrive.

Il PMO ha due esigenze con caratteristiche diverse:

- **Intake dei business case.** Un proponente allega un documento in chat: va registrato nel PMO Demand Hub con il file originale, sempre allo stesso modo. È un lavoro interno all'Agente Demand IT, senza un pubblico proprio.
- **Preparazione della revisione.** Sponsor e architetti devono prepararsi alla sessione di revisione: briefing sulla proposta, domande mirate sui criteri più pesanti. È un servizio con un pubblico proprio, che il PMO vuole riusare anche in altri contesti e che potrebbe essere mantenuto da un altro team.

In questo laboratorio viene creato un **child agent** per l'intake, con un **agent flow** che salva il documento, e un **connected agent** per la revisione, l'**Agente Comitato**, che legge i dati del PMO Demand Hub.

::: details <!-- icon: lightbulb f-instructions --> Perché questa scelta
- **Child agent per l'intake.** Un child agent vive dentro l'agente padre: condivide il ciclo di vita e la pubblicazione, ha istruzioni e strumenti propri e viene invocato quando la richiesta corrisponde alla sua descrizione. È la scelta giusta per una sotto-procedura che non ha senso fuori dall'Agente Demand IT.
- **Agent flow invece di un topic per salvare il file.** Salvare il documento richiede più passaggi lato server (creare la riga, caricare il file, restituire il codice) senza interagire con l'utente: un flow li esegue in sequenza, con input e output tipizzati.
- **Strumento usabile solo dal child agent.** Il flow di intake non deve essere chiamato dall'orchestratore in contesti sbagliati: viene reso disponibile solo quando il child agent lo richiama esplicitamente.
- **Connected agent per la revisione.** Un connected agent è un agente completo, pubblicato a sé, con istruzioni, conoscenza e ciclo di rilascio propri. L'orchestratore gli delega un compito ben definito e ne integra la risposta. Ha senso quando lo specialista ha un pubblico o un responsabile diverso, o può servire ad altri agenti.
- **Dataverse come conoscenza dello specialista.** Nella standard harness lo specialista può interrogare direttamente le tabelle del PMO come conoscenza, in sola lettura e con i permessi dell'utente. Nel percorso GitHub Copilot lo stesso risultato si ottiene con il Dataverse MCP Server.
- **Solo PDF in questa fase.** Il prompt che analizzerà il documento in S03 accetta come input solo PDF o immagini. Il child agent quindi accetta il PDF e chiede di convertire i file Word: è un vincolo della standard harness che il percorso GitHub Copilot non ha.
:::

## Che cosa si costruisce

Lo schema mostra l'architettura completa della standard harness alla fine del percorso. In questo lab nascono le due deleghe principali dell'**Agente Demand IT**: l'intake al child agent **Intake Proposte**, che per ora ha il solo agent flow **Carica business case**, e la preparazione della revisione all'**Agente Comitato**. Gli altri agent flow, il topic del dossier e il trigger email si aggiungono in S03-S06.

![Architettura multi-agente della Standard Harness](../../images/architettura-standard.svg)

## Prerequisiti

Per svolgere questo lab occorre avere terminato il laboratorio S01 ed avere creato l'**Agente Demand IT**. Servono inoltre i business case [`BC-01_Portale_fornitori_self-service.pdf`](../../../resources/advanced/business-case/BC-01_Portale_fornitori_self-service.pdf) e [`BC-05_Nuova_intranet_e_hub_dipendenti.docx`](../../../resources/advanced/business-case/BC-05_Nuova_intranet_e_hub_dipendenti.docx).

## Intake Proposte

L'intake ha regole proprie (un file per volta, solo PDF, nessuna valutazione senza conferma) e strumenti che servono solo a lui. Isolarlo in un child agent tiene corte le istruzioni dell'orchestratore e rende l'intake un componente che si modifica senza toccare il resto. Il child agent vive dentro l'orchestratore e si rilascia con lui.

### Creare il child agent

1. Aprire l'**Agente Demand IT** e selezionare la scheda **Agents**.
2. Selezionare **Add** e poi **New child agent**.

![](./images/passo1-01.png)

![](./images/passo1-02.png)

3. Nel campo **Name** inserire `Intake Proposte`
4. Nel campo **When will this be used?** selezionare **The agent chooses**
5. Nel campo **Description** inserire:

```text
Registra nel PMO Demand Hub i business case delle proposte di progetto IT allegati in chat o ricevuti per email, analizza il documento e, quando richiesto, crea la valutazione con i criteri del programma.
```

6. Nella sezione **Knowledge** del child agent disattivare **Web Search** se presente.
7. Selezionare **Save**.

![](./images/passo1-03.png)

### Configurare l'agent flow Carica business case

Per registrare una proposta servono operazioni che il modello da solo non può fare: creare una riga in Dataverse, caricare il PDF nella colonna file, rileggere il codice assegnato. Un agent flow le esegue sempre nello stesso ordine e restituisce all'agente solo ciò che serve (il codice PP-####), senza che il modello debba conoscere i dettagli di Dataverse.

1. Nel child agent **Intake Proposte** individuare la sezione **Tools**.

> [!WARNING]
> **Attenzione**
>
> Questa non è la scheda **Tools** dell'agente padre: la sezione si trova scorrendo sotto le istruzioni del child agent.

![](./images/passo2-01.png)

![](./images/passo2-02.png)

2. Selezionare **Add**, **New tool** e poi **Agent flow**. Si apre il designer con il trigger **When an agent calls the flow** e l'azione **Respond to the agent**.

![](./images/passo2-03.png)

3. Selezionare il trigger e, con **Add an input**, creare i seguenti input:

| Tipo | Nome            | Descrizione                                                           |
| ---- | --------------- | --------------------------------------------------------------------- |
| File | `BusinessCase`  | `Il file PDF del business case allegato dall'utente`                  |
| Text | `Messaggio`     | `Messaggio di accompagnamento del proponente, massimo 4000 caratteri` |
| Text | `EmailMittente` | `Email di chi ha inviato il business case`                            |

![](./images/passo2-04.png)

4. Sotto il trigger aggiungere l'azione **Microsoft Dataverse**, **Add a new row**.

![](./images/passo2-05.png)

5. Rinominare il nodo in `Crea proposta`, impostare **Table name** su **Proposals** e selezionare **Show all**.
6. Compilare le colonne seguenti:

| Colonna                      | Come impostarla      | Valore                                                                          |
| ---------------------------- | -------------------- | ------------------------------------------------------------------------------- |
| Titolo                       | Contenuto dinamico   | **BusinessCase name** dal trigger (titolo provvisorio, verrà sostituito in S03) |
| Messaggio di accompagnamento | Espressione (**fx**) | vedere sotto                                                                    |
| Email di origine             | Contenuto dinamico   | **EmailMittente**                                                               |
| Canale                       | Elenco               | **Chat**                                                                        |
| Stato proposta               | Elenco               | **Received**                                                                    |
| Data di presentazione        | Espressione          | `formatDateTime(utcNow(), 'yyyy-MM-dd')`                                        |

![](./images/passo2-06.png)

![](./images/passo2-07.png)

![](./images/passo2-08.png)

7. Per **Messaggio di accompagnamento** inserire la seguente espressione, che tronca il testo a 4.000 caratteri:

```text
if(greater(length(coalesce(triggerBody()?['text'], '')), 4000), substring(triggerBody()?['text'], 0, 4000), coalesce(triggerBody()?['text'], ''))
```

> [!NOTE]
> **Nome interno dell'input**
>
> `text` è il nome interno del primo input di testo del trigger (`Messaggio`). Se nel proprio flow il nome è diverso, costruire l'espressione inserendo il contenuto dinamico **Messaggio** al posto di `triggerBody()?['text']`.

![](./images/passo2-09.png)

![](./images/passo2-10.png)

8. Sotto **Crea proposta** aggiungere **Microsoft Dataverse**, **Upload a file or an image**.

> [!WARNING]
> **Attenzione**
>
> Fare attenzione a non scegliere l'azione dal nome molto simile *Upload a file or an image to the selected environment*.

9. Rinominare il nodo in `Carica documento` e impostare le seguenti proprietà:

| Proprietà | Valore |
| --- | --- |
| Content name | **BusinessCase name** |
| Table name | **Proposals** |
| Row ID | **Proposal** (identificatore della riga) da **Crea proposta** |
| Column Name | **Business Case Document** |
| Content | **BusinessCase contentBytes** |

![](./images/passo2-extra-01.png)

10. Selezionare **Respond to the agent** e aggiungere un output di testo:
    - **Name**: `CodiceProposta`
    - **Value**: **Proposal Code** da **Crea proposta**
    - **Description**: `Il codice PP-#### della proposta registrata`

![](./images/passo2-extra-02.png)

11. Selezionare **Save draft**.
12. Nella scheda **Overview** selezionare **Edit** e impostare:
    - **Flow name**: `Carica business case`
    - **Description**: `Registra una nuova proposta nel PMO Demand Hub con il file del business case e restituisce il codice PP-####.`
13. Tornare al **Designer** e selezionare **Publish**.

![](./images/passo2-extra-03.png)

### Collegare il flow al child agent

Il flow esiste, ma l'agente deve sapere quando usarlo e con quali valori. La descrizione stretta (solo un PDF, una volta per messaggio) e la limitazione ai riferimenti delle istruzioni evitano chiamate premature; il mapping degli input passa il file allegato dalla conversazione al flow.

1. Tornare all'**Agente Demand IT**, scheda **Agents**, aprire **Intake Proposte** e nella sua sezione **Tools** selezionare **Add**.

![](./images/passo3-extra-04.png)

![](./images/passo3-extra-05.png)

![](./images/passo3-extra-06.png)

2. Filtrare per **Flow**, selezionare **Carica business case** e poi **Add and configure**.
3. Impostare la descrizione:

```text
Registra nel PMO Demand Hub il business case allegato in chat. REGOLA RIGIDA: chiamalo solo quando il messaggio corrente contiene esattamente un allegato con estensione .pdf, una sola volta per messaggio.
```

![](./images/passo3-extra-07.png)

4. In **Additional details**, se è disponibile l'opzione **When this tool may be used**, scegliere **Only when referenced by topics or agents**: così solo il child agent, che lo cita nelle sue istruzioni, può usarlo.

![](./images/passo3-extra-08.png)

5. Configurare gli input. Il file arriva come due valori, contenuto e nome; selezionare **Add input** se non compaiono:

| Input         | Fill using               | Valore                                                |
| ------------- | ------------------------ | ----------------------------------------------------- |
| contentBytes  | Custom value             | Formula: `First(System.Activity.Attachments).Content` |
| name          | Custom value             | Formula: `First(System.Activity.Attachments).Name`    |
| Messaggio     | Dynamically fill with AI | **Customize**, descrizione sotto                      |
| EmailMittente | Custom value             | Scheda **System**: `User.Email`                       |

![](./images/passo3-extra-09.png)

![](./images/passo3-extra-10.png)

![](./images/passo3-extra-11.png)

6. Per l'input **Messaggio** selezionare **Customize** e inserire la descrizione:

```text
Ricava dal contesto il messaggio con cui l'utente accompagna il business case. Non chiedere nulla all'utente: se non c'è un messaggio, usa "Business case caricato in chat". REGOLA RIGIDA: massimo 4000 caratteri.
```

7. In **Advanced** di **Messaggio** impostare **How many reprompts** su **Don't repeat** e, in **No valid entity found**, **Set variable to value** con:

```text
Business case caricato in chat
```

![](./images/passo3-extra-12.png)

![](./images/passo3-extra-13.png)

8. Selezionare **Save**.

> [!NOTE]
> **Formule utilizzate**
>
> - `System.Activity.Attachments` → contiene gli allegati del messaggio corrente.
> - `First(...)` → prende il primo allegato.
> - `.Content` → restituisce il contenuto del file; `.Name` → restituisce il nome.
>
> Fissare questi input con formule evita che il modello debba "indovinare" il file.

### Definire le istruzioni del child agent

Le istruzioni del child agent sono la procedura di intake scritta come la seguirebbe un analista: controlli sul file prima di tutto, registrazione una sola volta, risposta con il codice. Sono anche il posto in cui si dice che cosa fare quando le condizioni non sono rispettate, ad esempio un file Word.

1. Aprire **Intake Proposte** e incollare nelle **Instructions**:

```text
Gestisci l'intake dei business case delle proposte di progetto IT. Usa gli strumenti solo se il passaggio corrisponde esattamente al processo descritto; altrimenti spiega che non puoi aiutare.

Processo di intake via chat
1. Controlli sul file
   - Procedi solo se /System.Activity.Attachments contiene esattamente un file.
   - Se ci sono più file, chiedi di caricarli uno alla volta e fermati.
   - Se il file non ha estensione .pdf, fermati: spiega che il PMO analizza il business case in PDF con testo selezionabile e chiedi di esportare il documento in PDF (ad esempio da Word con Salva con nome, PDF). Non accettare immagini o scansioni.
2. Registrazione
   - Chiama /Carica business case una sola volta per lo stesso messaggio.
3. Esito
   - Riporta sempre il codice della proposta [CodiceProposta] (PP-####) e spiega che il documento è stato registrato.

Identificatori: Proposta = PP-####. Non inventarli mai.
```

![](./images/passo4-extra-14.png)

2. Nei punti in cui le istruzioni contengono un nome preceduto dallo slash (`/`), selezionare il testo che segue il carattere `/` e scegliere l'elemento dinamico. Impostare:
   - `System.Activity.Attachments` (Variabile)
   - `Carica business case` (Tool)
3. Selezionare **Save**.

## Agente Comitato

La preparazione della revisione ha un pubblico diverso (sponsor e architetti) e potrebbe servire anche ad altri agenti del gruppo. Per questo diventa un agente autonomo, con istruzioni, conoscenza e pubblicazione proprie, che l'orchestratore chiama come agente connesso.

### Creare l'Agente Comitato

1. Tornare a **Agents** e selezionare **Create blank agent**.
2. Inserire il nome `Agente Comitato` e, in **Advanced settings**, selezionare la soluzione **PMO Demand IT** e lo schema name `csm_agentecomitato_std`. Selezionare **Create**.

![](./images/passo5-extra-15.png)

![](./images/passo5-extra-16.png)

3. Come **Descrizione** inserire:

```text
Prepara sponsor e architetti alla sessione di revisione delle proposte di progetto IT con briefing e domande basati sui dati del PMO Demand Hub.
```

![](./images/passo5-extra-17.png)

4. Nella sezione **Instructions** inserire:

```text
Sei l'Agente Comitato di Zava S.p.A. Aiuti sponsor interni, architetti di riferimento e analisti del PMO a prepararsi alla sessione di revisione di una proposta di progetto IT. Non contatti mai i proponenti.

Rispondi su dati del PMO solo quando servono a preparare la revisione di una proposta specifica. Usa le tabelle Proposal, Requester, Program, Evaluation Criterion e Assessment per preparare briefing e domande mirate.

Identificatori validi:
- Proposta (csm_proposalcode della tabella Proposal): PP-####
- Valutazione (csm_assessmentcode della tabella Assessment): AS-####
- Proponente (csm_requestercode della tabella Requester): RQ-####
- Programma (csm_programcode della tabella Program): PG-###

Come lavori:
- Se manca un'informazione necessaria (ad esempio il codice della proposta), fai una domanda di chiarimento.
- Basa ogni risposta sui dati: non inventare e non indovinare.
- Collega punti di forza e rischi ai criteri con il peso più alto del programma.
- Sii conciso, professionale e basato sulle evidenze.
```

![](./images/passo5-extra-18.png)

5. Nella scheda **Overview**, sezione **Model**, scegliere **Claude Sonnet 4.6**, come per l'Agente Demand IT.

> [!NOTE]
> **Modello dell'agente connesso**
>
> L'Agente Comitato è un agente autonomo: non eredita il modello dell'orchestratore, va impostato anche qui.

6. Selezionare **Save**.

### Configurare Dataverse come conoscenza

Lo specialista deve rispondere su proposte, criteri e valutazioni reali. Aggiungere le tabelle del PMO come conoscenza gli permette di cercarle e citarle senza strumenti di scrittura: per un agente che prepara briefing, la sola lettura è esattamente ciò che serve.

1. Nella pagina **Knowledge** dell'Agente Comitato selezionare **Add knowledge** e poi **Dataverse**.

![](./images/passo6-extra-19.png)

2. Nel campo di ricerca scrivere `csm_` e selezionare le cinque tabelle: **Program**, **Evaluation Criterion**, **Requester**, **Proposal**, **Assessment**.

![](./images/passo6-extra-20.png)

3. Selezionare **Add to agent** e attendere che la fonte sia pronta.
4. Aprire **Settings**, **Generative AI** e impostare:
   - **Use information from the Web**: disattivato;
   - **Allow ungrounded responses**: disattivato;

![](./images/passo6-extra-21.png)

   - **File uploads**: disattivato (lo specialista non riceve file).

![](./images/passo6-extra-22.png)

5. Nella sezione dedicata agli altri agenti (in **Settings**, **Generative AI** o **Agents**, a seconda della versione) attivare **Let other agents connect to and use this one**.

![](./images/passo6-extra-23.png)

6. Selezionare **Save** e poi **Publish**, e attendere la conferma.

![](./images/passo6-extra-24.png)

> [!IMPORTANT]
> **Pubblicazione**
>
> Un agente diventa collegabile solo dopo la **pubblicazione**. Se nel passaggio successivo l'Agente Comitato appare grigio, non è stato pubblicato.

### Collegare l'Agente Comitato all'orchestratore

Collegando lo specialista, la descrizione inserita diventa il criterio con cui l'orchestratore decide di delegare. Deve dire per che cosa usarlo e, altrettanto importante, per che cosa non usarlo.

1. Aprire l'**Agente Demand IT**, scheda **Agents**, e selezionare **Add an agent** (o **Add**, poi **Connect an existing agent**).

![](./images/passo7-extra-25.png)

2. Selezionare **Agente Comitato** e impostare la **Description**:

```text
Usalo per preparare la sessione di revisione di una proposta (PP-####) e per ogni domanda sui dati registrati nel PMO Demand Hub: proposte, proponenti, programmi, criteri con i pesi in vigore e valutazioni. Produce briefing per sponsor e architetto, domande mirate sui criteri con peso più alto e rischi da approfondire. Non usarlo per registrare business case, calcolare o registrare valutazioni o generare documenti.
```

3. Lasciare attiva l'opzione **Pass conversation history to this agent** e selezionare **Add agent**.

![](./images/passo7-extra-26.png)

4. Nella scheda **Agents** verificare di vedere **Intake Proposte** come child agent e **Agente Comitato** come connected agent.

![](./images/passo7-extra-27.png)

> [!TIP]
> **La descrizione decide la delega**
>
> Una descrizione troppo ampia ("risponde su proposte, programmi e criteri") farebbe delegare allo specialista anche domande che l'orchestratore gestisce meglio da solo. Scrivere anche che cosa lo specialista **non** deve fare.

## Delega dell'orchestratore

L'orchestratore ora ha due collaboratori. Due righe esplicite nelle istruzioni rendono la delega prevedibile: intake e valutazione vanno a **Intake Proposte**, preparazione della revisione all'**Agente Comitato**.

### Aggiornare le istruzioni dell'orchestratore

1. Aprire l'**Agente Demand IT** e aggiungere in fondo alle **Instructions**:

```text
# Delega
- Quando l'utente allega un business case o chiede di registrare, analizzare o valutare una proposta, delega a /Intake Proposte.
- Quando l'utente chiede di prepararsi alla revisione di una proposta, chiede domande o un briefing per sponsor o architetto, oppure chiede dati registrati nel PMO Demand Hub (proposte, programmi, criteri e pesi in vigore, valutazioni), delega sempre a /Agente Comitato. Non rispondere con la tua conoscenza: i documenti del PMO descrivono le regole, ma i criteri e i pesi in vigore sono solo nei dati che legge /Agente Comitato.
- Usa la tua conoscenza solo per domande sulle regole del processo (formati, struttura del business case, soglie, tempi).
- Quando /Agente Comitato ha già risposto all'utente, non ripetere e non riassumere la sua risposta. Aggiungi al massimo una frase con il passo successivo.
```

2. Sostituire i riferimenti preceduti da `/` con gli agenti corrispondenti e selezionare **Save**.

![](./images/passo8-extra-28.png)

> [!NOTE]
> **Evitare le risposte doppie**
>
> L'Agente Comitato risponde direttamente in chat e restituisce lo stesso contenuto all'orchestratore. Senza l'ultima riga della sezione Delega l'orchestratore ripete la risposta e l'utente la vede due volte.

## Testare il sistema multi-agente

Il test copre i tre percorsi costruiti: un file non ammesso che deve essere rifiutato senza chiamare il flow, un PDF che deve diventare una proposta e una richiesta di preparazione che deve arrivare allo specialista. La mappa delle attività indica chi ha fatto che cosa.

### Rifiuto di un file Word

1. Nel pannello **Test** dell'Agente Demand IT avviare una nuova sessione.
2. Allegare [`BC-05_Nuova_intranet_e_hub_dipendenti.docx`](../../../resources/advanced/business-case/BC-05_Nuova_intranet_e_hub_dipendenti.docx) e scrivere:

```text
Ecco la nostra proposta per la nuova intranet
```

![](./images/passo9-extra-29.png)

Il child agent deve rifiutare il file Word e chiedere il PDF, senza chiamare il flow.

### Registrazione di un business case PDF

1. In una nuova sessione allegare [`BC-01_Portale_fornitori_self-service.pdf`](../../../resources/advanced/business-case/BC-01_Portale_fornitori_self-service.pdf) e scrivere:

```text
Vi invio il business case del portale fornitori per la valutazione
```

![](./images/passo9-extra-30.png)

Nella mappa delle attività deve comparire **Intake Proposte** che chiama **Carica business case**; la risposta riporta un codice `PP-####`.

> [!WARNING]
> **SystemError**
>
> Se si riceve *Si è verificato un errore. Codice errore: SystemError* e nella mappa il nodo **Intake Proposte** mostra *No steps were taken*, controllare il modello dell'**Agente Demand IT** (scheda **Overview**, sezione **Model**): impostarlo su **Claude Sonnet 4.6**, salvare, aprire **New test session** e riprovare. Il child agent usa sempre il modello dell'agente padre.

![](./images/passo9-extra-31.png)

![](./images/passo9-extra-32.png)

2. Aprire l'app **PMO Demand Hub**, **Proposals**: la nuova riga ha come titolo il nome del file, **Channel** Chat, **Proposal Status** Received e il PDF nella colonna **Business Case Document**.

![](./images/passo9-extra-33.png)

![](./images/passo9-extra-34.png)

### Delega all'Agente Comitato

Lo schema mostra il percorso della richiesta: l'orchestratore delega all'Agente Comitato, che legge i dati della proposta in Dataverse e prepara briefing e domande sui criteri più pesati. La risposta dello specialista arriva direttamente all'utente; l'orchestratore aggiunge al massimo una frase.

![Preparazione della revisione con l'agente connesso](../../images/workflow-revisione.svg)

1. Provare la delega allo specialista, sostituendo `PP-####` con il codice restituito nella prova precedente:

```text
Devo prepararmi alla revisione della proposta PP-####. Quali sono i criteri del programma PG-100 con i pesi in vigore? Preparami tre domande per lo sponsor.
```

2. Osservare nella mappa delle attività la chiamata all'**Agente Comitato**.

> [!WARNING]
> **Prima risposta lenta**
>
> La prima risposta dell'Agente Comitato dopo la pubblicazione può richiedere fino a 5 minuti. Attendere prima di riprovare.

> [!TIP]
> **L'orchestratore non delega**
>
> Se l'orchestratore risponde da solo citando **Conoscenza PMO** invece di delegare, controllare tre cose: la riga sulla delega all'Agente Comitato nelle istruzioni (sezione *Aggiornare le istruzioni dell'orchestratore*), con il riferimento `/Agente Comitato` inserito come elemento dinamico e non come testo; la descrizione dell'agente connesso (sezione *Collegare l'Agente Comitato all'orchestratore*), che deve citare i dati del PMO Demand Hub; una **New test session** dopo il salvataggio. Le linee guida del PMO contengono anche un elenco dei criteri, ed è per questo che l'orchestratore è tentato di rispondere da solo.

> [!IMPORTANT]
> **Lab Completato**
>
> Il primo sistema multi-agente del PMO è funzionante: l'Agente Demand IT delega l'intake al child agent **Intake Proposte** e la preparazione della revisione al connected agent **Agente Comitato**. In questo laboratorio si è visto:
>
> - la differenza tra child agent e connected agent e quando usare ciascuno;
> - come un agent flow riceve un file dalla chat tramite `System.Activity.Attachments`;
> - come limitare l'uso di uno strumento al child agent;
> - come pubblicare uno specialista e scriverne la descrizione di delega.
