# Lab 08 - Autonomous Hiring Agent

[Previous: Lab 07](../07-multi-agent-hiring/README.md) | [Back to README](../../README.md) | [Next: Lab 09](../09-multimodal-resume-prompt/README.md)

>[!warning] Prerequisito
>Per completare questo lab è necessario avere completato il laboratorio precedente sul sistema *Multi Agente*
### Use Case

**Come** HR Recruiter

**Vorrei** essere notificato quando arriva una email nella mia casella postale contente un CV, che dev'essere automaticamente caricato sul database

### Realizzazione Tecnica

La richiesta verrà gestita in due modi:

1. Configurando un *event trigger* per ogni email in arrivo che:
	1. Controlla se il `contentType` del file, contenente il formato, è un `PDF`
	2. Estrae il file e lo carica su Dataverse attraverso i Power Platform Connectors
	3. Invia un prompt all'agente per ulteriore elaborazione passando come input i parametri derivati dai connettori Dataverse

2. Aggiungendo un nuovo agent flow al figlio **Application Intake Agent** che viene attivato dal prompt all'interno dell'event trigger.
	- L'agente utilizza i parametri di input passati dal prompt per riempire un'adaptive card da pubblicare in un canale Microsoft Teams per notificare il team HR di Recruiting. L'adaptive card conterrà un link alla tabella Dataverse che può essere anche visualizzata dall'**Hiring Agent**.

## Automatizzare le email dei candidati

### Caricamento di CV ricevuti via email su Dataverse

1. All'interno di **Hiring Agent** scorrere all'interno della scheda di **Overview** fino alla sezione **Triggers and Channels** (o semplicemente **Triggers**, a seconda della versione) e premere **+ Add**

![](./images/3-addTrigger.png)

2. Nella lista dei trigger, selezionare **When a new email arrives (V3)** e selezionare **Next**.

![](./images/3-selectTrigger.png)

3. Nella schermata seguente, modificare il campo **Trigger name** con:

```
When a new email arrives from an applicant
```

>[!note] Nota
>Assicurarsi che tutte le connessioni alle app siano accompagnate da una spunta verde. Se non è così, selezionare il menu con **...** e premere su **New connection reference** per creare una nuova connessione.

![](./images/3-triggerName.png)

4. L'ultimo passaggio è quello di impostare le proprietà degli input del trigger. Aggiornare le seguenti proprietà con le seguenti:

|Property|How to Set|Details|
|---|---|---|
|**Include Attachments (Optional)**|Dropdown|Yes|
|**Subject Filter (Optional)**|Type/Enter with keyboard|Application|
|**Only with Attachments (Optional)**|Dropdown|Yes|

![](./images/3-triggerSettings.png)

5. Una volta creato, un messaggio di conferma apparirà indicando che il trigger è stato aggiunto all'agente. Selezionare **Close** e il trigger sarà elencato nella sezione dei **Triggers**.
6. Selezionare i tre puntini **...** accanto al trigger e premere **Edit in Power Automate**.

![](./images/3-editInPowerAutomate.png)

7. Il trigger caricherà quindi un flusso all'interno del portale Power Automate. All'interno della schermata è possibile aggiungere ulteriore logica e azioni per altre automazioni. La situazione iniziale è data dal trigger in cima, seguito dall'azione **Sends a prompt to the specific copilot for processing**

![](./images/3-EditInPowerAutomate-x.png)

8. Di base, il trigger **When a new email arrives** in Power Automate potrebbe processare multiple email insieme se arrivano contemporaneamente, facendo partire un unico flusso per il gruppo. Per evitare questo comportamento ed assicurarsi che il flusso parta in maniera separata per ogni singola mail, nei **Settings** del trigger abilitare il valore **Split On** e selezionare `@triggerOutputs()?['body/value']` .

![](./images/3-UpdateTriggerSettings-x.png)

9. Il primo passaggio è quello di controllare che l'allegato sia in formato PDF, perché l'agente potrebbe ad esempio processare (erroneamente) immagini derivanti dalle firme delle email. Selezionare il simbolo **+** sotto il trigger e selezionare **Control** all'interno della sezione **Built in tools**

![](./images/3-Control.png)

10. Selezionare l'azione **Condition**

![](./images/3-AddConditionAction.png)

11. Nel campo **Choose value**, selezionare l'icona con il fulmine (valore dinamico)
12. Nella ricerca, inserire

```
content type
```

13. Selezionare il parametro **Attachments Content-Type** proveniente dal trigger

![](./images/3-lowconditionval.png)

>[!tip] Approfondimento: **For each**
>Dopo avere selezionato **Attachments Content-Type** su Power Automate sarà apparsa automaticamente un azione di tipo **For each**.
>
>Questo avviene quando si seleziona un parametro (contenuto dinamico) che rappresenta una lista di oggetti (array). Power Automate riconosce che probabilmente si vuole processare ogni elemento singolarmente, per cui crea automaticamente un ciclo *Apply to each* intorno all'azione. 
>
>Questo assicura che l'azione si attiverà una volta per ogni elemento della lista, invece di cercare di processare tutta la lista in un colpo solo, che potrebbe creare errori.   

![](./images/3-ForEach.png)

>[!tip] Approfondimento: **Trigger Condition** vs. **Conditional Control Logic**
>In questo caso è stata utilizzata una logica condizionale tradizionale (*if ... else*), ma come alternativa più performante i triggers in Power Automate possono contenere una condizione insita nella loro azione. Le condizioni di trigger possono accedere al contenuto del payload.
>
>In questo caso, gli allegati si trovano in un array all'interno del body del trigger chiamato `attachments`. La seguente espressione controlla se l'array degli allegati non è vuoto **E** se il tipo del primo elemento è `application/pdf`. Notare che questo controlla solo il primo allegato.
>```
>    @and(not(empty(triggerOutputs()?['body/attachments'])),equals(toLower(first(triggerOutputs()?['body/attachments'])?['contentType']),'application/pdf'))
>```
>La condizione può essere specificata all'interno dell'azione trigger nella scheda **Settings**:
>
>![](./images/3-triggercondition.png)

14. All'interno del campo **Choose a value** alla destra del blocco **Condition** inserire il seguente valore:

```
application/pdf
```

Questo garantisce che per ogni file in allegato verrà controllato che il formato sia .PDF.

![](./images/3-EqualToValue-x.png)

15. All'interno del percorso **True**, premere il tasto **+** e cercare `html to text`. Selezione l'azione **html to text**.

>[!tip] Approfondimento: **HTML to text**
>L’azione **HTML to text** in **Power Automate** viene utilizzata per convertire contenuti formattati in **HTML** in **plain text**. È particolarmente utile quando si ricevono dati (come **email**, contenuti web o risposte da **API**) che contengono **HTML tags**, e si desidera estrarre solo il testo leggibile senza formattazione o codice.
>
>**Quando utilizzarla?**
>
>- Quando si vuole estrarre **testo leggibile** da email, pagine web o risposte **API** che contengono **HTML**.
>- Prima di inviare contenuti a sistemi che **non supportano la formattazione HTML** (come **SMS**, messaggi **Teams** o **database**).
>- Per **ripulire i dati** prima di ulteriori attività di **processing** o **analysis**.

![](./images/3-AddHTMLToTextAction-x.png)

16. Creare una nuova connessione per l'azione **Html to text** andando a selezionare **Create new**

![](./images/3-createnewhtmlconnection.png)

17. Una volta che l'azione è configurabile, occorre aggiungere il parametro **Body** dal trigger. All'interno del campo **Content**, selezionare l'icona con il fulmine.

![](./images/3-AddDynamicContent-x.png)

18. All'interno della scheda **Dynamic content**, cercare `body` e selezionare il campo **Body**, quindi **Add**.

![](./images/3-AddDynamicContent.png)

19. Una volta completata l'azione, tornare al flusso e aggiungere una nuova azione sotto **Html to text** premendo il tasto **+**. Cercare `Dataverse add` e selezionare l'azione **Add a new row**.

![](./images/3-AddANewRow-x.png)

20. Per chiarezza, rinominare l'azione in `Add a new Resume row`
21. All'interno del parametro **Table name**, cercare `res` e selezionare la tabella **Resumes**
22. All'interno del parametro **Resume Title**, selezionare l'**icona fx** sulla destra

![](./images/3-AddDynamicContent2-x.png)

23. Nella scheda **Function**, inserire la seguente espressione e premere **Add**

```
item()?['name']
```

>[!tip] Approfondimento: funzione **item()**
>Quando si utilizza un’azione **Apply to each**, **Power Automate** scorre ogni elemento di una **collection (array)**. La funzione **`item()`** viene usata principalmente all’interno di azioni come **Apply to each (o For each)**, **Select** o **Filter array**.
>
>**`item()`** restituisce l’**elemento corrente** in fase di elaborazione in un **loop** o in un’operazione su un **array**. 
>
>Ad esempio, l'espressione `item()?['Email']` recupera la proprietà *Email* dell'elemento corrente. 
>
>Se sono presenti loop annidati, è possibile usare `items('LoopName')` per fare riferimento agli elementi di uno specifico loop.

24. Mancano ancora diversi parametri da configurare. Selezionare **Show all** e all'interno del campo **Cover Letter** premere l'icona **fx**. Nella scheda **Function** inserire la seguente espressione (utilizzata anche nel laboratorio precedente), e premere **Add**

```
if(greater(length(body('Html_to_text')), 2000), substring(body('Html_to_text'), 0, 2000), body('Html_to_text'))
```

Questa espressione controlla se il testo dell'azione **Html to text** è più grande di 2000 caratteri, in tal caso ritorna un valore troncato ai primi 2000 caratteri; altrimenti restituisce il valore originale.

![](./images/3-CoverLetterParameter-x.png)

25. Nel campo **Source Email Address**, selezionare l'icona con il fulmine e cercare `from` scegliendo il valore **From** dal trigger, in quanto contiene l'indirizzo mail richiesto.

![](./images/3-FromParameter-x.png)

26. Nel campo **Upload Date**, selezionare l'icona **fx**. All'interno della scheda **Function**, inserire la seguente espressione e premere **Add**

```
utcNow()
```

![](./images/3-UploadDateParameter-x.png)

27. L'azione **Add a new Resume row** è completata. Tornare al designer del flusso ed aggiungere una nuova azione premendo il tasto **+** sotto il nodo appena configurato. Cercare `Dataverse upload` e selezionare l'azione **Upload a file or an image**

![](./images/3-AddUploadAFileOrAnImage-x.png)

28. Per chiarezza, rinominare l'azione in `Upload Resume File`
29. All'interno del campo **Content name**, selezionare l'icona **fx**. Nella scheda **Function**, utilizzare la seguente espressione

```
item()?['name']
```

![](./images/3-ContentNameParameter-x.png)

30. Per il campo **Table name**, cercare `resumes` tra i campi dinamici e selezionare la tabella **Resumes** e premere **Add**

![](./images/3-SelectResumesTable-x.png)

31. Per il campo **Row ID**, cercare `id` tra i campi dinamici e selezionare il parametro **Resume** all'interno dell'azione *Add a new Resume row* e premere **Add**

![](./images/3-RowIDParameter-x.png)

32. Nel campo **Column name** espandere il menu a tendina e selezionare **Resume PDF**

![](./images/3-ColumnNameParameter-x.png)

33. Nell'ultimo campo **Content**, selezionare l'icona **fx** sulla destra. All'interno della scheda **Function**, inserire la seguente espressione e premere **Add**

```
item()?['contentBytes']
```

![](./images/3-CollapseAction-x.png)

34. A questo punto selezionare con il mouse l'azione finale **Sends a prompt to the specified copilot for processing** e trascinarla graficamente sotto l'azione precedentemente configurata sotto il percorso *True*, come mostrato in figura

![](./images/3-DragAndDropAction-x.png)

35. Infine, selezionare l'azione **Sends a prompt to the specified copilot for processing** per configurarla. 
36. Nel campo **Body/message**, eliminare tutto il contenuto esistente.

![](./images/3-ClearBodyParameter-x.png)

37. Copiare e incollare il seguente testo all'interno del campo **Body/message**, ed evidenziare il testo `RESUME ID PLACEHOLDER`

```
Send [ResumeId (text)] = "RESUME ID PLACEHOLDER" and [ResumeTitle (text_1)] = "RESUME TITLE PLACEHOLDER" and [ResumeNumber (text_2)]= "RESUME NUMBER PLACEHOLDER" to the Tool "Notify Teams Applicant channel" in the child agent "Application Intake Agent"
```

![](./images/3-ReplaceResumeIDPlaceholder-x.png)

38. Selezionare l'icona con il fulmine. Cercare `resume` e selezionare il parametro **Resume** dall'azione *Add a new Resume row*, poi premere **Add**

![](./images/3-SelectResumeParameter-x.png)

39. Evidenziare il testo `RESUME TITLE PLACEHOLDER`, selezionare il simbolo con il fulmine a destra. Cercare `title`, selezionare il parametro **Resume Title** dall'azione *Add a new Resume row*  e premere **Add**

![](./images/3-SelectResumeTitleParameter.png)

40. Evidenziare il testo `RESUME NUMBER PLACEHOLDER`, selezionare il simbolo con il fulmine a destra. Cercare `resume number`, selezionare il parametro **Resume Number** dall'azione *Add a new Resume row*  e premere **Add**

![](./images/3-SelectResumeNumberParameter.png)

41. La configurazione del flusso è completata! Premere **Salva** in alto a destra.

![](./images/3-saveTriggerFlow-x.png)

42. Per modificare gli ultimi dettagli del flusso, premere su **Back** in alto a sinistra

![](./images/3-Back-x.png)

43. Selezionare **Edit** nella sezione **Details** e aggiornare il **Plan** all'opzione **Copilot Studio**. Premere **Save** e confermare un eventuale pop-up.

>[!info] Nota Licensing
>Convertire il piano in Copilot Studio consente di gestire il flusso di trigger in Copilot Studio e consumare capacity Copilot Studio invece di Power Automate

![](./images/3-ChangePlanDetails-x.png)

44. Una volta aggiornato il piano, premere nuovamente **Edit** per tornare nell'editor e poi pubblicare il flusso con **Publish**. Il flusso di trigger è terminato!

![](./images/3-Published-x.png)

### Notificare un canale Teams con Adaptive Card

Il prossimo passaggio consiste nel creare un nuovo agent flow per l'agent figlio **Intake Application Agent** che prende i valori passati dal flusso trigger e posta una Adaptive Card in un canale Teams. La notifica farà presente al team di recruiting che un nuovo PDF è stato caricato così possono subito revisionarlo.

1. All'interno dell'**Hiring Agent**, navigare nella scheda **Agents** e selezionare **Application Intake Agent**

![](./images/3-selectAppIntakeAgent.png)

2. Scorrere in basso nella sezione **Tools** e selezionare **+ Add**

![](./images/3-addToolHiring.png)

3. All'interno del menu, premere **+ New tool** e selezionare **Agent flow**

![](./images/3-newTool.png)

4. Attendere il caricamento dell'agent flow designer. All'interno del trigger **When an agent calls the flow**, selezionare **+ Add an input**

![](./images/3-SelectAddAnInput.png)

5. Aggiungere un input per ognuno dei parametri contenuti nella tabella in basso. Selezionare il tipo di input opportuno ed inserire il nome. In questo caso non occorre inserire una descrizione perché nel prompt di partenza sono esplicitati chiaramente (l'ultima azione configurata nel primo flusso).

| Type | Name           |
| ---- | -------------- |
| Text | `ResumeId`     |
| Text | `ResumeTitle`  |
| Text | `ResumeNumber` |

![](./images/3-AddNewAction.png)

6. Premere il tasto **+** sotto il trigger. Cercare `post` e selezionare l'azione **Post card in a chat or channel** nel gruppo dei connettori Microsoft Teams. 

![](./images/3-SelectPostCardInAChatOrChannel.png)

7. Effettuare il **Sing in** se richiesto dal sistema
8. Configurare i parametri seguendo la tabella seguente

| Parameter   | Details                                                             |
| ----------- | ------------------------------------------------------------------- |
| **Post as** | Selezionare l'opzione `Flow bot`                                    |
| **Post in** | Selezionare l'opzione `Channel`                                     |
| **Team**    | Selezionare un team disponibile nell'ambiente a cui si ha accesso   |
| **Channel** | Selezionare un canale disponibile nell'ambiente a cui si ha accesso |

![](./images/3-ConfigureParameters.png)

9. Selezionare il campo **Adaptive Card** ed incollare all'interno il contenuto del seguente JSON

```
{
    "type": "AdaptiveCard",
    "speak": "New Resume Uploaded",
    "body": [
        {
            "inlines": [
                {
                    "type": "TextRun",
                    "size": "Small",
                    "text": "Resume table updated",
                    "selectAction": {
                        "url": "https://adaptivecards.io",
                        "type": "Action.OpenUrl"
                    }
                }
            ],
            "type": "RichTextBlock"
        },
        {
            "columns": [
                {
                    "width": "auto",
                    "items": [
                        {
                            "type": "Icon",
                            "name": "DocumentArrowUp",
                            "color": "Accent"
                        }
                    ],
                    "type": "Column"
                },
                {
                    "width": "stretch",
                    "items": [
                        {
                            "size": "Large",
                            "text": "New Resume Uploaded",
                            "weight": "Bolder",
                            "wrap": true,
                            "type": "TextBlock"
                        }
                    ],
                    "verticalContentAlignment": "Center",
                    "spacing": "Small",
                    "type": "Column"
                }
            ],
            "spacing": "Small",
            "type": "ColumnSet"
        },
        {
            "type": "Table",
            "targetWidth": "AtLeast:Narrow",
            "columns": [
                {
                    "width": 1
                },
                {
                    "width": 2
                }
            ],
            "rows": [
                {
                    "type": "TableRow",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Resume Number",
                                    "wrap": true,
                                    "weight": "Bolder"
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        },
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "RESUME NUMBER PLACEHOLDER",
                                    "wrap": true
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        }
                    ]
                },
                {
                    "type": "TableRow",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Name",
                                    "wrap": true,
                                    "weight": "Bolder"
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        },
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "RESUME NAME PLACEHOLDER",
                                    "wrap": true
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        }
                    ]
                },
                {
                    "type": "TableRow",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Status",
                                    "wrap": true,
                                    "weight": "Bolder"
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        },
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Waiting for Review",
                                    "wrap": true
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        }
                    ]
                },
                {
                    "type": "TableRow",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Due Date",
                                    "wrap": true,
                                    "weight": "Bolder"
                                }
                            ]
                        },
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "May 21, 2023",
                                    "wrap": true
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "TableRow",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "Priority",
                                    "wrap": true,
                                    "weight": "Bolder"
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        },
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "ColumnSet",
                                    "columns": [
                                        {
                                            "type": "Column",
                                            "width": "auto",
                                            "items": [
                                                {
                                                    "type": "Icon",
                                                    "name": "Flag",
                                                    "color": "Attention",
                                                    "size": "xSmall",
                                                    "horizontalAlignment": "Center"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "color": "Attention",
                                                    "text": "Important",
                                                    "wrap": true,
                                                    "spacing": "Small",
                                                    "type": "TextBlock"
                                                }
                                            ],
                                            "spacing": "Small"
                                        }
                                    ],
                                    "spacing": "Small"
                                }
                            ],
                            "verticalContentAlignment": "Center"
                        }
                    ]
                }
            ],
            "firstRowAsHeaders": false,
            "showGridLines": false
        },
        {
            "actions": [
                {
                    "title": "View Resume",
                    "type": "Action.OpenUrl",
                    "url": "https://adaptivecards.io/"
                }
            ],
            "type": "ActionSet",
            "targetWidth": "AtLeast:Narrow",
            "spacing": "ExtraLarge"
        }
    ],
    "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5"
}
```

![](./images/3-JSON.png)

10. Similmente a quanto fatto in passato, occorre rimpiazzare alcuni campi nel JSON con valori dinamici. Aggiornare l'URL della proprietà `url` all'interno di `selectAction`. Evidenziare il valore corrente ed eliminarlo.

![](./images/3-SystemViewURL.png)

11. Aprire una nuova scheda nel browser e navigare su Power App. Entrare all'interno dell'applicazione **Hiring Hub**, selezionare la vista **Resumes** tramite il menu di sinistra e copiare l'URL del browser. 

>[!info] Come tornare nella model-driven app se è stata chiusa
>1. Navigare su [https://make.powerapps.com](https://make.powerapps.com/) assicurandosi di essere nello stesso environment, altrimenti cambiarlo
>![](./images/3-BrowseToURL-x.png)
>2. Selezionare **Apps** nel menu di sinistra, cercare l'applicazione **Hiring Hub** ed infine premere l'icona **Play** per caricarla nel browser
>![](./images/3-HiringHubApp-x.png)

![](./images/3-CopyResumesSystemViewURL.png)

12. Tornare nella configurazione dell'adaptive card ed incollare l'URL all'interno della proprietà `url` all'interno di `selectAction`. A questo punto dovrebbero essere presenti i seguenti valori, dove quelli in giallo sono dettagli dello specifico environment.

| Parameter            | Value | Explanation                                                                                  |
| -------------------- | ----- | -------------------------------------------------------------------------------------------- |
| **Organization URI** | GUID  | L'URL dell'ambiente Dataverse/Dynamics 365                                                   |
| **appid**            | GUID  | Viene utilizzato per aprire una specifica Model-Driven App (in questo caso, Hiring Hub)      |
| **viewid**           | GUID  | Il parametro della query è l'identificatore di una specifica vista (in questo caso, Resumes) |

![](./images/3-PasteURL.png)

13. A questo punto occorre inserire valori dinamici per altre proprietà direttamente dall'interno dell'agent flow. Selezionare l'icona di pannello nell'angolo destro dell'azione **Post card in a chat or channel**  

![](./images/3-SelectPannelIcon.png)

14. Scorrere la card fino a trovare la proprietà `text` con valore `RESUME NUMBER PLACEHOLDER`. Sottolineare il valore di placeholder ed eliminarlo.

![](./images/3-DeleteResumeNumberPlaceholder.png)

15. Selezionare l'icona con il fulmine, cercare **ResumeNumber** tra i parametri dinamici e premere **Add**.

![](./images/3-ResumeNumberDynamicContent.png)

16. Ripetere lo stesso procedimento per il valore `RESUME NAME PLACEHOLDER`. Evidenziare il valore, eliminarlo. Tramite la scheda dei parametri dinamici, cercare **ResumeTitle** e premere **Add**

![](./images/3-select-resume-title-parameter-alt.png)

17. Scorrere fino a trovare il valore **Due Date** che rappresenta la data entro la quale il recruiter deve visionare il CV. Evidenziare il valore `May 21, 2023` ed eliminarlo. 

![](./images/3-DeleteDueDatePlaceholder.png)

18. Premere l'icona **fx** ed all'interno della scheda **Function** inserire la seguente formula, da aggiungere alla proprietà `text`

```
addDays(utcNow(), 3, 'MMM dd, yyyy')
```

>[!note] Formula PowerFx utilizzata
>La funzione `addDays()` prende una data (`utcNow`), ci somma un certo numero di giorni (`3`) e restituisce la nuova data nel formato specificato (`MMM dd, yyyy`).

 ![](./images/3-ExpressionDueDate.png)

19. Rimane da aggiornare la proprietà `url` all'interno dell'array `actions` in fondo al JSON. Questo consentirà al recruiter di navigare nel relativo record direttamente dall'adaptive card.
20. Nella model-driven app **Hiring Hub**, aprire una riga qualsiasi nella vista **Resumes**. Questo aprirà la visualizzazione *form*. Copiare l'URL.

![](./images/3-CopyResumeURL.png)

21. Navigare indietro nell'agent flow, evidenziare il valore URL di placeholder e rimpiazzarlo con l'URL appena copiato

![](./images/3-PasteResumeRowURL.png)

22. All'interno dell'URL appena incollato, evidenziare ed eliminare il valore contenente il `GUID`

![](./images/3-DeleteViewResumePlaceholderURL.png)

23. Tramite l'icona del fulmine, cercare il parametro dinamico **ResumeId** e premere **Add**

![](./images/3-ResumeIdParameter-x.png)

24. La configurazione dell'azione **Post card in a chat or channel** è completata! Selezionare ora l'azione finale **Respond to the agent** e selezionare **+Add an output** 

![](./images/3-AddAnOutput.png)

25. Selezionare il tipo **Text** , scegliere come nome `EndConversation` e come valore di ritorno `Finished`

![](./images/3-EndConversationOutputValue.png)

26. Salvare il flusso tramite il bottone **Save draft** in alto a destra
27. Prima di pubblicarlo, occorre aggiornare alcuni dettagli. Selezionare la scheda di **Overview** e premere **Edit**
28. Come nome, inserire

```
Notify Teams Applicant channel
```

29. Come descrizione, inserire 

```
The flow starts when an agent manually triggers it and submits a resume. It posts a message card in a Microsoft Teams channel with candidate details retrieved from Hiring Hub (resume number, name, status, due date, priority), plus links to the resume and the Hiring Hub record for review and follow-up tracking.
```

![](./images/3-EditDetails.png)

30. Premere **Save** per salvare le modifiche. Tornare nella scheda **Designer** e premere il tasto **Publish** per pubblicare l'agent flow. Attendere il messaggio di conferma.

![](./images/3-PublishAgentFlow.png)

31. L'agent flow deve essere ora aggiunto come tool per il **Application Intake Agent**. Navigare all'interno dell'**Hiring Agent**, selezionare la scheda **Agents** e premere **Application Intake Agent**

![](./images/3-ApplicationIntakeAgent.png)

32. Nella sezione **Details** aggiornare la descrizione aggiungendo in fondo una nuova linea

```
and also notifies the Teams Applicant channel
```

![](./images/3-UpdateAgentDescription.png)

33. Scorrere nella sezione **tools** e premere **+ Add**

![](./images/3-AddTools.png)

34. Selezionare la scheda **Flow** e scegliere l'agent flow creato poco fa, **Notify Teams Applicant Channel**, poi premere **Add and configure**

![](./images/3-NotifyTeamsApplicantChannelAgentFlow.png)

35. All'interno della sezione **Inputs**, saranno visibili i tre valori configurati in precedenza nell'agent flow. Di base, la configurazione **Fill using** è impostata su **Dynamically fill with AI** per tutti e tre i valori. Siccome il prompt configurato all'inizio di questo laboratorio contiene tutti i parametri necessari, è possibile lasciare tutto inalterato.

![](./images/3-Inputs.png)

36. Una volta aggiunto il nuovo strumento, occorre aggiornare le istruzioni dell'agente. Navigare indietro alla lista degli agenti, e selezionare **Application Intake Agent**.

![](./images/3-SelectApplicationIntakeAgent.png)

37. All'interno del campo **Instructions**, inserire una nuova riga dopo `2.Post-Upload`. Copiare ed incollare le seguenti istruzioni

```
Process for Resume Upload via Email
1. When you receive a message, **Send [ResumeId (text)] = "1680265f-5793-f011-b41b-7c1e525be9f7" and [ResumeTitle (text_1)] = "TAYLOR TESTPERSON (FICTITIOUS).pdf" and [ResumeNumber (text_2)]= "R01026" to the Tool "Notify Teams Applicant channel"** in the child agent "Application Intake Agent", call [AGENT FLOW PLACEHOLDER]
```

![](./images/3-PasteCopiedInstructions.png)

38. Sottolineare il test `[AGENT FLOW PLACEHOLDER]` e sostituirlo con lo slash in avanti `/`, selezionando il tool **Notify Teams Applicant Channel**

![](./images/3-NotifyTeamsApplicatnChannelTool.png)

39. Premere **Save** per salvare le nuove istruzioni di **Application Intake Agent**
40. A questo punto non resta che pubblicare l'agente **Hiring Agent**. Selezionare il tasto **Publish** nell'angolo in alto a destra e premere nuovamente **Publish** nel menu pop-up

![](./images/3-PublishAgent.png)

41. Una volta pubblicato, apparirà un messaggio di conferma con la buona riuscita dell'operazione

### Testare l'event trigger

1. Per testare l'event trigger, sarà necessario inviare una mail contenente in allegato un CV in pdf. All'interno di Outlook, comporre una nuova mail come quella di esempio

| Email Component     | Details                                           |
| ------------------- | ------------------------------------------------- |
| **To recipient**    | Usare l'account che si possiede                   |
| **File attachment** | Caricare un CV demo presente tra i materiali demo |
| **Subject**         | Job Application                                   |
| **Body**            | Copiare il seguente corpo della mail              |
```
Dear Hiring Manager,

I am writing to express my interest in the Senior Power Platform Engineer position at your organization. With over nine years of experience delivering secure and scalable solutions on Microsoft cloud platforms, I am confident in my ability to contribute effectively to your team.

In my most recent role as Lead Power Platform Engineer, I developed an automated resume-intake pipeline, reducing manual triage and improving searchability. I have delivered HR case management applications, introduced solution-aware flows, and implemented PR checks to enhance deployment lead times. My expertise includes Power Apps, Power Automate, Power Pages, Dataverse, and a range of Microsoft 365 services, as well as integration with Graph/REST APIs and Azure Functions.

Previously, I developed Teams approvals with adaptive cards, cutting approval times to the same day, and created robust error-handling frameworks. My background also includes migrating legacy workflows to Power Automate and building self-service portals adopted by hundreds of employees.

I hold a B.Sc. in Computer Science and am certified as a Power Platform Developer (PL-400) and Solution Architect (PL-600). I am also passionate about mentoring and have volunteered with local maker groups.

Please find my CV attached for your consideration. I would welcome the opportunity to discuss how my skills and experience align with your needs.

Thank you for your time and consideration.

Kind regards,
Taylor Testperson
```

![](./images/3-ComposeEmailWithAttachment-x.png)

2. All'interno del portale Power Automate sotto il menu **My flows**, aprire il flusso di trigger e premere il tasto di **Refresh** per visualizzare se il flusso è stato lanciato

![](./images/3-FlowRun-x.png)

3. In Copilot Studio, all'interno di **Hiring Agent**, selezionare la scheda **Activity**. Dovrebbe esserci una nuova attività con il nome **Automated** e con status **Complete**. 

![](./images/3-StatusComplete.png)

4. Selezionare l'attività e premere sull'event trigger all'interno della mappa delle attività. Sul pannello di destra, prendere nota di come il prompt contenga i valori precedentemente configurati come `Resume Id`, `Resume Title` e `Resume Number`. 

![](./images/3-EventTrigger.png)

5. Navigare nell'app **Hiring Hub** e dentro la vista **Resumes** premere **Refresh** per visualizzare le ultime modifiche. Dovrebbe essere presente la riga creata in seguito alla ricezione della mail che ha scatenato l'event trigger

![](./images/3-ResumeRowCreated.png)

6. Navigare indietro su Copilot Studio e selezionare nella mappa attività l'agent flow **Notify Teams Applicant Channel** all'interno di **Application Intake Agent**. Prendere nota degli input derivanti dai valori della riga su Dataverse. Questo è come si possono passare valori da un event trigger ad un agent flow.

![](./images/3-NotifyTeamsApplicantChannel.png)

7. Infine, navigare su **Microsoft Teams** e prendere visione dell'adaptive card pubblicata nel canale scelto.  La carta conterrà le informazioni presenti nella riga di Dataverse, con un collegamento che riporterà all'applicazione **Hiring Hub**

![](./images/3-AdaptiveCardResumeTableURL.png)

8. Inoltre, premendo il tasto **View Resume** sarà possibile navigare direttamente allo specifico elemento per cui si è stati notificati.

![](./images/3-AdaptiveCardResumeRowURL.png)

![](./images/3-ResumeRow.png)

>[!success] Successo
>Con la realizzazione del primo agente autonomo in grado di processare email, aggiornare informazioni nel database e notificare il team, il laboratorio è terminato!

