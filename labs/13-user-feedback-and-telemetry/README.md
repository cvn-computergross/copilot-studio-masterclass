# Lab 13 - User Feedback and Telemetry

[Previous: Lab 12](../12-mcp-server-integration/README.md) | [Back to README](../../README.md) | Next: Complete

Il seguente laboratorio mostrerà come un utente può dare feedback in due modi:

1. Interazioni **built-in** e analisi tramite la pagina *Analytics* dell'agente
2. **Adaptive Card personalizzata** che consente di collezionare il feedback quando l'utente ha risposto con 1 o 2 stelle al *sondaggio CSAT* (Customer Satisfaction Score). Come bonus, verrà loggato l'evento tramite il servizio **Azure Application Insight**

>[!WARNING]
>**Prerequisito**
>Per completare questo lab è necessario avere pubblicato l'agente *Interview Agent* (le funzioni specifiche non verranno utilizzate)

## Ottenere user feedback attraverso interazioni standard

1. Una volta che **Interview Agent** è stato pubblicato, aprirlo da una delle interfacce utente come la Copilot App (m365.cloud.microsoft) o Microsoft Teams, ed iniziare a fare domande
2. Rispetto al box contenente la risposta dell'agente in chat, selezionare l'icona **pollice in su** per fornire feedback positivo con commento, o selezionare **pollice in giù** per fornire feedback negativo con un commento. 

Esempi di feedback positivo:

```
Clear and Concise: The response was easy to understand and well-structured.
```

```
Accurate and Relevant: The information provided was correct and directly addressed the question.
```

```
Helpful and Actionable: The response included practical steps or examples that I could apply.
```

Esempi di feedback negativo:

```
Incomplete or Vague: The response lacked detail or didn’t fully answer the question.
```

```
Inaccurate or Misleading: The information provided was incorrect or not relevant to the query.
```

```
Overly Complex or Hard to Follow: The explanation was confusing or used unnecessary jargon.
```

![](./images/8-SubmitPositiveFeedback.png)

3. Ripetere questa operazione un certo numero di volte fino ad avere inserito diverse reazioni accompagnate da feedback scritto

### Consultare le analitiche standard

>[!NOTE]
>**Nota**
>Il feedback potrebbe impiegare qualche minuto prima di essere disponibile nella scheda Analytics. Se non è subito presente, controllare occasionalmente. 

1. In Copilot Studio, all'interno di **Interview Agent** navigare nella scheda **Analytics** e scorrere fino alla sezione **Satisfaction**. All'interno della scheda **Reactions**, premere il tasto **See details**. Questo caricherà un pannello contenente tutte le recensioni inserite.

![](./images/8-Reactions.png)

## Costruire un adaptive card per raccogliere feedback

All'interno di questo laboratorio verrà implementato un processo all'interno di **Hiring Agent** per raccogliere feedback personalizzato a seguito di un questionario CSAT. Quando l'utente risponde con 1 o 2 stelle al sondaggio, verrà raccolto addizionale feedback per capire il motivo della insoddisfazione. 

All'interno di questo esempio verranno utilizzati (e modificati) alcuni utili topic di sistema.

### Creazione di un nuovo topic

1. All'interno di **Hiring Agent**, navigare nella scheda **Topics**, selezionare **+ Add a topic** e scegliere **From blank**

![](./images/8-AddTopicFromBlank.png)

2. Rinominare il topic in `Capture CSAT dissatisfied feedback`
3. All'interno del nodo trigger, selezionare l'icona con le frecce di **Change trigger** e selezionare **It's redirected to**. Questo farà si che il topic sarà attivato solo quando espressamente chiamato da un altro topic attraverso il nodo **Go to another topic**.

![](./images/8-RenameTopicAndConfigureTrigger.png)

4. Selezionare l'icona **+** sotto il trigger e selezionare il nodo **Ask with adaptive card**

![](./images/8-AskWithAdaptiveCardNode.png)

5. Selezionare il nodo, e premere **Edit adaptive card** nel menu che apparirà a destra

![](./images/8-EditAdaptiveCard.png)

6. All'interno dell'**Adaptive Card Designer**, espandere in basso il **Card payload editor**, selezionare tutto il contenuto presente (*Ctrl + A*) e sostituirlo con il JSON presente di seguito

![](./images/8-UpdateJSON.png)

```
{
    "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
    "body": [
        {
            "backgroundImage": {
                "url": "https://msftstories.thesourcemediaassets.com/2022/02/surface-pro-8-with-type-cover_-768x432.jpg",
                "verticalAlignment": "Bottom"
            },
            "items": [
                {
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch"
                        },
                        {
                            "items": [
                                {
                                    "items": [
                                        {
                                            "maxLines": 0,
                                            "size": "ExtraLarge",
                                            "text": "We'd love to hear from you",
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "wrap": true
                                        }
                                    ],
                                    "roundedCorners": true,
                                    "style": "default",
                                    "type": "Container"
                                }
                            ],
                            "type": "Column",
                            "width": "190px"
                        }
                    ],
                    "targetWidth": "AtLeast:Standard",
                    "type": "ColumnSet"
                }
            ],
            "minHeight": "200px",
            "roundedCorners": true,
            "style": "emphasis",
            "targetWidth": "AtLeast:Standard",
            "type": "Container",
            "verticalContentAlignment": "Bottom"
        },
        {
            "backgroundImage": {
                "verticalAlignment": "Bottom",
                "url": "https://msftstories.thesourcemediaassets.com/2022/02/surface-pro-8-with-type-cover_-768x432.jpg"
            },
            "items": [
                {
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch"
                        },
                        {
                            "type": "Column",
                            "width": "150px"
                        }
                    ],
                    "type": "ColumnSet"
                }
            ],
            "minHeight": "140px",
            "roundedCorners": true,
            "style": "emphasis",
            "targetWidth": "Narrow",
            "type": "Container",
            "verticalContentAlignment": "Bottom"
        },
        {
            "style": "RoundedCorners",
            "targetWidth": "VeryNarrow",
            "type": "Image",
            "url": "https://msftstories.thesourcemediaassets.com/2022/02/surface-pro-8-with-type-cover_-768x432.jpg"
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Give us your feedback",
                            "wrap": true,
                            "weight": "Bolder",
                            "color": "Accent"
                        },
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "auto"
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "spacing": "ExtraSmall"
                                }
                            ],
                            "spacing": "ExtraSmall"
                        }
                    ]
                }
            ],
            "spacing": "Medium",
            "targetWidth": "AtMost:Narrow"
        },
        {
            "columns": [
                {
                    "items": [
                        {
                            "color": "Accent",
                            "text": "Give us your feedback",
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "wrap": true,
                            "size": "Large"
                        }
                    ],
                    "type": "Column",
                    "verticalContentAlignment": "Center",
                    "width": "auto"
                },
                {
                    "spacing": "Small",
                    "targetWidth": "AtLeast:Narrow",
                    "type": "Column",
                    "width": "auto",
                    "verticalContentAlignment": "Center"
                },
                {
                    "spacing": "Small",
                    "targetWidth": "AtLeast:Narrow",
                    "type": "Column",
                    "verticalContentAlignment": "Center",
                    "width": "auto"
                },
                {
                    "spacing": "Small",
                    "targetWidth": "AtLeast:Narrow",
                    "type": "Column",
                    "verticalContentAlignment": "Center",
                    "width": "stretch"
                }
            ],
            "spacing": "Medium",
            "type": "ColumnSet",
            "targetWidth": "AtLeast:Standard"
        },
        {
            "type": "Input.ChoiceSet",
            "label": "We want to understand your dissatisfaction of your interaction with the Interview Agent ",
            "choices": [
                {
                    "title": "The agent didn't understand my responses or questions accurately",
                    "value": "Difficulty in understanding"
                },
                {
                    "title": "The process was confusing or difficult to navigate",
                    "value": "Process is difficult"
                },
                {
                    "title": "I had technical issues during the interaction (e.g., errors, delays)",
                    "value": "Technical issues"
                },
                {
                    "title": "All of the above",
                    "value": "Encountered all of the issues"
                }
            ],
            "placeholder": "Placeholder text",
            "style": "expanded",
            "id": "ratingId"
        },
        {
            "columns": [
                {
                    "items": [
                        {
                            "inlines": [
                                {
                                    "selectAction": {
                                        "targetElements": [
                                            "notesId",
                                            "chevronUp",
                                            "chevronDown"
                                        ],
                                        "type": "Action.ToggleVisibility"
                                    },
                                    "text": "Add comment",
                                    "type": "TextRun"
                                }
                            ],
                            "targetWidth": "AtLeast:Narrow",
                            "type": "RichTextBlock"
                        },
                        {
                            "inlines": [
                                {
                                    "selectAction": {
                                        "targetElements": [
                                            "notesId",
                                            "chevronUp",
                                            "chevronDown"
                                        ],
                                        "type": "Action.ToggleVisibility"
                                    },
                                    "text": "Add comment",
                                    "type": "TextRun"
                                }
                            ],
                            "spacing": "None",
                            "targetWidth": "VeryNarrow",
                            "type": "RichTextBlock"
                        }
                    ],
                    "type": "Column",
                    "verticalContentAlignment": "Center",
                    "width": "auto"
                },
                {
                    "items": [
                        {
                            "color": "Accent",
                            "id": "chevronDown",
                            "name": "ChevronDown",
                            "size": "xxSmall",
                            "type": "Icon"
                        },
                        {
                            "color": "Accent",
                            "id": "chevronUp",
                            "isVisible": false,
                            "name": "ChevronUp",
                            "size": "xxSmall",
                            "spacing": "None",
                            "type": "Icon"
                        }
                    ],
                    "selectAction": {
                        "targetElements": [
                            "notesId",
                            "chevronUp",
                            "chevronDown"
                        ],
                        "type": "Action.ToggleVisibility"
                    },
                    "spacing": "Small",
                    "type": "Column",
                    "verticalContentAlignment": "Center",
                    "width": "auto"
                }
            ],
            "spacing": "Medium",
            "type": "ColumnSet"
        },
        {
            "id": "notesId",
            "isMultiline": true,
            "isVisible": false,
            "placeholder": "Enter any additional comments you'd like to share",
            "spacing": "Small",
            "type": "Input.Text"
        },
        {
            "actions": [
                {
                    "style": "positive",
                    "title": "Submit",
                    "type": "Action.Submit"
                }
            ],
            "separator": true,
            "spacing": "Medium",
            "type": "ActionSet"
        }
    ],
    "type": "AdaptiveCard",
    "version": "1.5"
}
```

7. Notare adesso come il **Card Preview** contenga una nuova card con del testo ed alcuni dispositivi. Premere **Save** in alto a destra e poi uscire dal designer tramite **X Close**

![](./images/8-CardUpdated.png)

8. All'interno del canvas del topic, dovrebbe essere visualizzabile la nuova adaptive card. Scorrere in fondo e notare gli output. I campi `notesId` e `ratingId` sono stati definiti nelle proprietà della carta. Questi valori verranno utilizzati nel laboratorio bonus.

![](./images/8-CardOutputs.png)

### Modify End of Conversation system topic

Il prossimo passaggio consiste nel modificare il topic di sistema **End of Conversation** per ridirigere al topic precedentemente creato **Capture CSAT dissatisfied feedback**.

1. Navigare all'interno della sezione **Topics**, filtrare per **System** e selezionare il topic di sistema **End of Conversation**

![](./images/8-SelectEndOfConversationTopic.png)

2. Scorrere al nodo **Condition** che controlla la variabile `SurveyResponse`. Selezionare l'icona **+** sotto il nodo e premere **Add node**

![](./images/8-AddNode.png)

3. Selezionare **Variable management** e premere **Set a variable value**

![](./images/8-SelectSetAVariableValue.png)

4. Selezionare **Create a new variable**. Questo nodo consente di dichiarare una variabile per contenere la risposta dell'utente al survey CSAT.

![](./images/8-SelectCreateANewVariable.png)

5. Selezionare la variabile e tramite il pannello **Variable properties** cambiare i seguenti valori:

- **Variable name**: `VarCSATRating`
- **To value**: `0` (valore iniziale)

![](./images/8-ConfigureVariableProperties.png)

6. Selezionando il nodo già esistente **CSAT Question**, ci sarà un campo nel quale inserire il riferimento ad una variabile nella quale salvare il risultato della risposta data dall'utente. Inserire al suo interno la seguente espressione che fa riferimento alla variabile appena configurata:

```
Topic.VarCSATRating
```

![](./images/8-CSATQuestionProperties.png)

7. Selezionare l'icona **+** sotto il nodo **CSAT Question** e selezionare **Add a condition**

![](./images/8-AddAConditionNode.png)

>[!NOTE]
>**Logica da implementare**
>- Se il rating CSAT dato dall'utente è `3`, `4` o `5`, il flusso continuerà lungo il topic **End of Conversation** e farà parte dei feedback positivi
>- Se il rating CSAT dato dall'utente è `1` o `2`, la conversazione verrà instradata all'interno del ramo **All other condition** che gestirà i feedback negativi

8. Nel nodo **Condition** selezionare l'icona *maggiore* (**>**)

![](./images/8-SelectAVariable.png)

9. Selezionare la variabile **VarCSATRating**

![](./images/8-SelectVarCSATRating.png)

10. Come **operator**, selezionare `is greater or equal to`
11. Come **Value**, inserire il valore `3`

![](./images/8-AddIntegerValue.png)

12. Completare la logica relativa al caso in cui il valore del feedback è inferiore a `3`. All'interno del ramo **All other conditions**, selezionare l'icona **+**, selezionare **Topic management** e premere **Go to another topic >**

![](./images/8-AddNodeInOtherConditions.png)

13. All'interno del menu selezionare il topic precedentemente creato **Capture CSAT dissatisfied feedback** 

![](./images/8-SelectCaptureCSATDissatisfiedFeedbackTopic.png)

14. Selezionare **Save** per salvare il topic

![](./images/8-RedirectNodeAdded.png)

15. Testare l'agente tramite **Test** e **new test session**. Qualsiasi domanda va bene, l'obiettivo è quello di inserire un feedback CSAT con punteggio inferiore a 3. Per forzare l'attivazione del system topic, inserire un prompt con scritto:

```
end conversation
```

![](./images/8-EndConversation.png)

16. All'attivazione del topic **End of Conversation**, occorre rispondere **Yes** alle due domande seguenti

![](./images/8-YesToAnsweringQuestion.png)

17. A questo punto verrà inserita in chat la domanda CSAT. Selezionare 1 o 2 stelle come risposta

![](./images/8-CSATSurvey.png)

18. Siccome il rating è sotto 3, tramite l'activity map sarà possibile notare come il topic **End of Conversation** andrà a redirigere il flusso della conversazione all'interno del topic **Capture CSAT dissatisfied feedback**. Selezionare qualsiasi opzione

![](./images/8-RedirectToTopicForCustomFeedback.png)

19. Selezionare l'icona **Add comment** per inserire feedback testuale, utilizzando uno dei seguenti esempi

```
I tried to explain my situation clearly, but the agent kept giving irrelevant answers. It felt like it wasn’t interpreting my input correctly.
```

```
I wasn’t sure what to do next during the interaction. The conversation flow wasn’t intuitive, and I had to guess how to proceed.
```

```
The agent froze midway and didn’t respond for a while. I also experienced delays and had to refresh the page to continue.
```

20. Selezionare quindi **Submit**

![](./images/8-WrittenFeedbackAndSubmit.png)

21. L'agente riprenderà il topic **End of Conversation** siccome l'attività precedente è stata completata. Chiederà infine all'utente se c'è bisogno di assistenza addizionale. Selezionare **No**

![](./images/8-EndOfConversationTopicCompleted.png)

22. Questo completerà il topic **End of Conversation**

## BONUS: analisi telemetrica con Azure Application Insight

>[!WARNING]
>**Prerequisiti**
>Occorre avere a disposizione una **sottoscrizione Azure** e fare il setup della risorsa [Application Insight](https://learn.microsoft.com/en-us/azure/azure-monitor/app/create-workspace-resource?tabs=portal#create-an-application-insights-resource) 

1. Navigare nel custom topic **Capture CSAT dissatisfied** e selezionare l'icona **+** sotto il nodo **Ask with adaptive card**. Selezionare **Advanced** e premere **Log a custom telemetry event**

![](./images/8-AddLogACustomTelemetryEvent.png)

2. Selezionare l'icona con i tre puntini (**...**) e premere **Properties** 

![](./images/8-SelecProperties.png)

3. Nel box **Event name**, inserire `CSAT Dissatisfied`

![](./images/8-EnterEventName.png)

>[!TIP]
>**Approfondimento: Event name e Properties**
>**Event name**
>- Questo è l'**identificativo** dell'evento di telemetria che si vuole loggare
>- La funzione è di permettere la ricerca ed il filtraggio in un secondo momento tramite gli strumenti di analitiche e monitoraggio
>
>**Properties**
>- Le effettive proprietà da tracciare relative all'evento, ad esempio valori di variabili, input utente o dettagli di errore
>- Ad esempio, in questo caso potrebbe essere una combinazione dei valori inseriti nell'adaptive card

4. Nel box **Properties**, premere i tre punti **...** e selezionare la scheda **Formula**. Inserire la seguente espressione

```
"Feedback: " & Text(Topic.ratingId) & ", " & "Comment: " & If(IsBlank(Topic.notesId), "NA", Topic.notesId)
```

![](./images/8-EnterFormula.png)

>[!TIP]
>**Approfondimento: formula PowerFx utilizzata**
>- `"Feedback: "` → aggiunge il testo `Feedback: ` all'inizio
>- `& Text(Topic.ratingId):` → aggiunge alla stringa precedente il valore di `Topic.ratingId` (in questo caso, il numero da 1 a 5) convertito in testo 
>- `& ", "` → aggiunge alla stringa precedente una virgola e uno spazio per chiarezza
>- `& "Comment: "` → aggiunge alla stringa precedente il testo `Comment: `
>- `If(IsBlank(Topic.notesId), "NA", Topic.notesId)` → controlla se il campo `Topic.notesId` (in questo caso, il commento dell'utente) è vuoto. Se è vero, aggiunge alla stringa `NA`, altrimenti aggiunge il contenuto del commento
>
>**Esempio**
>- Se l'utente inserisce una recensione di 2 stelle e scrive "Too slow", il risultato sarebbe `Feedback: 2, Comment: Too slow`

5. Premere **Save** per salvare il topic
6. Per collegare l'agente alla risorsa **Application Insight**, selezionare **Settings** in alto a destra

![](./images/8-AgentSettings.png)

7. Su **Advanced**, selezionare **Application Insights**

![](./images/8-ApplicationInsightSettings.png)

8. In un'altra scheda, navigare sul [portale Azure](https://portal.azure.com/) e aprire la risorsa precedentemente creata **Application Insight** (che avrà il nome deciso in fase di setup). All'interno della pagina di **Overview**, identificare il campo **Connection string** e copiarne il contenuto

![](./images/8-CopyConnectionStringValue.png)

9. Navigare indietro su Copilot Studio ed incollare il contenuto all'interno del campo **Connection string**. Salvare i cambiamenti con **Save**.

![](./images/8-PasteConnectionStringAndSave.png)

10. A questo punto è possibile testare il log dell'evento di telemetria nel quale il rating CSAT è di 1 o 2 stelle. Ripetere gli stessi step di test fatti in precedenza andando a scrivere in chat `end conversation`, dando due volte `Yes` e compilando il form con un numero inferiore a 3

![](./images/8-CSATSurvey1.png)

11. Scrivere un commento generico e premere **Submit**

![](./images/8-SubmitFeedback.png)

12. Terminare il flusso assicurandosi che l'agent torni nel topic **End of Conversation** e premere **No**

![](./images/8-EndOfConversationTopicCompleted1.png)

13. Ora va controllato il log generato da Application Insight. Navigare nuovamente sulla risorsa Azure **Application Insight** e selezionare **Events** nel menu di sinistra. Nel menu a tendina relativo a **Who used**, selezionare **Any Custom Event** e nel menu a tendina **Events** selezionare l'evento personalizzato **CSAT Dissatisfied**. Questo filtro mostrerà solo gli eventi custom con il nome **CSAT Dissatisfied**

![](./images/8-Events.png)

14. Scorrere in basso e selezionare **View More Insights**

![](./images/8-ViewMoreInsights.png)

15. In questa sezione è possibile avere maggiori informazioni su gli eventi custom loggati dall'agente. Scorrere alla sezione **Event Statistics** e selezionare **CSAT Dissatisfied**

![](./images/8-ViewEventInsights.png)

16. La sezione **end-to-end transaction details** contiene una serie di segnali molto precisi relativi alla telemetria dell'evento

- Il pannello **Event Summary** mostra orario, tipo ed dettagli dell'evento. 
- Il pannello **Event Properties** mostra ulteriori informazioni, come le **Custom properties** che sono state inviate con l'evento
	- La proprietà `SerializedData` contiene il messaggio di feedback, includendo problemi tecnici e commenti dell'utente
	- Le altre proprietà come `DesignMode`, `channelId` e `conversationId` offrono contesto sul dove e come l'evento sia stato generato

![](./images/8-CustomEventInformation.png)

17. Per situazioni in cui nel corso del tempo si accumulano moltissimi eventi all'interno di Application Insight, c'è un secondo metodo per ricercarli, tramite l'uso di query *Kusto* (un linguaggio di query). Nel menu di sinistra, selezionare **Logs** per fare caricare la scheda **Queries hub**. Chiuderla premendo la **X**

![](./images/8-QueryLogs.png)

17. Di base, saranno visualizzate una serie di Queries eseguite in precedenza. Per effettuare una query, premere su **Select a table**

![](./images/8-SelectATable.png)

18. Selezionare la tabella `customEvents` e premere **Run**. Questo lancerà una query sulla tabella `customEvents`

![](./images/8-RunCustomEvents.png)

19. Verranno quindi mostrati i risultati della query. Di base, mostrerà gli ultimi *1000 risultati* delle ultime *24 ore*

![](./images/8-customEventsResults.png)

20. La vista mostrata è nella **Simple mode**. Per effettuare query specifiche è possibile cambiarla in **KQL mode** 

![](./images/8-SelectKQLmode.png)

21. Inserire la seguente Kusto query e premere **Run**

```
customEvents
| extend FeedbackData = customDimensions['SerializedData']
| where name == "CSAT Dissatisfied"
```

![](./images/8-KustoQuery.png)

>[!TIP]
>**Approfondimento: Kusto query utilizzata**
>- `customEvents` → si riferisce alla tabella di Application Insight che contiene tutte gli eventi telemetrici relativi agli eventi custom
>- `| extend FeedbackData = customDimensions['SerializedData']` → aggiunge una nuova colonna chiamata `FeedbackData`, che va ad estrarre il valore dal campo `SerializedData` all'interno della proprietà `customDimension` (un dizionario di dati collegati all'evento)
>- `| where name == "CSAT Dissatisfied"` → filtra i risultati ai soli eventi il cui nome è esattamente "CSAT Dissatisfied"
>
>In sintesi, la query ricerca tutti gli eventi custom chiamati "CSAT Dissatisfied" ed estrapola i dati di feedback per ulteriore analisi. Serve ad analizzare i feedback negativi inseriti dagli utenti

22. Espandere uno dei risultati mostrati

![](./images/8-Results.png)

23. Scorrere in basso per trovare la nuova colonna `FeedbackData` definita nella query Kusto

![](./images/8-ExtendSerializedData.png)

>[!IMPORTANT]
>**Successo**
>Con l'uso della prima query Kusto, la sezione bonus de laboratorio è terminata!

