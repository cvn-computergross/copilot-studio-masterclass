# Lab 05 - Device Request Agent Flows

[Previous: Lab 04](../04-job-posting-tools/README.md) | [Back to README](../../README.md) | [Next: Lab 06](../06-hiring-solution-setup/README.md)

## Prerequisiti

### Lista SharePoint Devices

Per lo svolgimento di questo Lab è necessario avere il Sito SharePoint del [Lab 03 - Ticket Agent Topics](../03-ticket-agent-topics/README.md).
Usare la Lista chiamata Devices presente di default nel Sito generato con il Template e aggiungere le seguenti colonne:

- Title
- Status
- Manufacturer
- Model
- Asset Type
- Color
- Serial Number
- Purchase Date
- Purchase Price,
- Order #

Ricreare la lista basandosi su questa tabella:

|Title|Status|Manufacturer|Model|Asset Type|Color|Serial Number|Purchase Date|Purchase Price|Order #|
|---|---|---|---|---|---|---|---|---|---|
|Fabrikam Laptop X1|Reserved|Fabrikam Inc|FX1-2023|Laptop|Space Gray|FAB123456789|2023-04-10|1199.00|ORD101|
|Trey Monitor Pro|Available|Trey Research|TM-PRO27|Accessory|Black|TREY987654321|2022-09-05|899.00|ORD102|
|Trey Headset Max|Available|Trey Research|TH-MAX2023|Accessory|Dark Blue|TREY112233445|2024-01-10|299.00|ORD104|
|Microsoft JetPrint|In Repair|Microsoft|MJ-404X|Printer|White|MS6677889900|2021-07-15|349.00|ORD104|
|Contoso Phone Z|In Use|Contoso Ltd|CP-Z2022|Smartphone|Silver|CON556677889|2023-01-20|699.00|ORD103|
|Contoso SmartWatch|Reserved|Contoso Ltd|CSW-G2|Accessory|Black|CON998877665|2024-02-28|249.00|ORD106|


[Scarica il file Devices-CSM.csv](../02-knowledge-sources/files/Devices-CSM.csv)


## Creazione Agente

1. Navigare all'interno di [Copilot Studio](https://copilotstudio.microsoft.com/) e selezionare **Agents**  situato nel menù laterale a sinistra. 

2. Nella schermata **Agents** è possibile visualizzare la lista completa degli agenti creati nel' Environment, proseguire premendo **Create blank agent** .

![](./images/creazione2.png)

3. Copilot Studio procederà con la creazione dell' agente vuoto, per effettuare modifiche aspettare il seguente Messaggio:

![](./images/Creazione3.png)

4. Finito il provisioning dell'agente modificare **Nome** e **Descrizione**:

- **Nome**:

```
Device Booker
```

- **Descrizione**:

```
Automatically manages device reservations, availability, and assignments across the asset lifecycle.
```

5. Lasciare le istruzioni vuote per il momento e proseguire con la guida.

## Creazione Topic - Available Devices

1. Andare nella Sezione Topics , selezionare **Add a topic** e poi **From blank**.

![](./images/Flow1.png)


2. Cambiare il nome del topic con:

```
Available devices
```

3. Inserire la seguente Descrizione del Trigger :

```
This topic helps users find devices that are available from our SharePoint Devices list. User can ask to see available devices and it will return a list of devices that are available which can include laptops, smartphones, accessories and more.
```

![](./images/device-flow-step-01.png)

Successivamente, verrà aggiunta una **nuova variabile di input** che l’IA generativa utilizzerà durante il processo di orchestrazione per estrarre, dal messaggio dell’utente, il valore relativo al **tipo di dispositivo**.  
4. Selezionare i **tre puntini (… )** accanto al topic, quindi scegliere **Details** per visualizzare il pannello dei dettagli del topic.

![](./images/device-flow-step-02.png)

5. Il pannello **Topic details** è ora stato caricato. Selezionare la scheda **Input**.

![](./images/device-flow-step-03.png)

6. Selezionare **Create a new variable**.

![](./images/device-flow-step-04.png)

7. Inserire il nome della variabile:

```
VarDeviceType
```

8. Cambiare **Identify as** in **User's entire response**.

![](./images/device-flow-step-05.png)

9. Modificare la descrizione della variabile in:

```
List of possible values: Laptop, Desktop, Smartphone
```

![](./images/device-flow-step-06.png)

10. Andare nella sezione **Output** e creare una nuova variabile.

![](./images/device-flow-step-07.png)

11. Inserire i seguenti dati:

- **Variable name** 

```
VarAvailableDevices
```

- **Variable data type** :  **Table**

- **Variable description** :

```
List of available devices by device type
```

![](./images/device-flow-step-08.png)

12. Ora terminati i dettagli del Topic premere l'icona del + e aggiungere un nuovo nodo.

![](./images/device-flow-step-09.png)

13. Selezionare **Add a tool**, andare nella sezione **Connector** e cercare il connettore **Get items** di SharePoint.

![](./images/device-flow-step-10.png)

14. Selezionare la tab Input e inserire il sito SharePoint creato in precedenza, con la lista Devices.

15. Ora aprire il menù a tendina delle **Advanced Options** e in **filter Query** premere il simbolo (...).

![](./images/device-flow-step-11.png)

16. Recarsi nella sezione Formula e inserire la seguente espressione PowerFx :

```
Concatenate("Status eq 'Available' and AssetType eq '", Topic.VarDeviceType, "'")
```

>[!NOTE]
>La formula costruisce dinamicamente una stringa di filtro unendo testo fisso con il valore di `Topic.VarDeviceType`.  Il risultato è una query che seleziona solo i dispositivi con stato `"Available"` e tipo uguale al valore della variabile.

17. Premere Insert.

![](./images/device-flow-step-12.png)

18. Selezionare poi **All items** in **Limit Columns by View**.

![](./images/device-flow-step-13.png)

19. Ora modificare il nome della variabile di Output in:

```
VarDevices
```

20. Modificarla da variabile di Topic  a Global.

![](./images/device-flow-step-14.png)

21. Successivamente aggiungere un nuovo nodo **Variable Management** -> **Set a variable value**.

![](./images/device-flow-step-15.png)

22. Selezionare per il **Set a variable** la variabile **VarAvailableDevices**.

![](./images/device-flow-step-16.png)

23. Premere l'icona (...)  nella sezione **To value**.

![](./images/device-flow-step-17.png)

24. Selezionare la sezione Formula e inserire la seguente espressione:

```
Global.VarDevices.value
```

25. Premere Insert.

![](./images/device-flow-step-18.png)

## Creazione Topic - request device

Creare un nuovo Topic che guiderà l'utente nella prenotazione di un Device.

1. Andare nella Sezione Topics , selezionare **Add a topic** e poi **From blank**.

![](./images/Flow1.png)


2. Cambiare il nome del topic con:

```
Request device
```

3. Inserire la seguente Descrizione del Trigger :

```
This topic helps users request a device when they answer yes to the question that asks the user if they would like to request one of these devices.
```

![](./images/Flow2.png)

4. Successivamente premere il + e selezionare **Ask with adaptive card**

![](./images/Flow3.png)

5. Selezionare il nodo e nelle **Properties** premere **Edit adaptive card**.

![](./images/Flow4.png)

![](./images/Flow5.png)

All’interno dell’editor del **Card payload**, selezionare l’intero contenuto utilizzando la combinazione di tasti **Ctrl + A** su Windows oppure **Command + A** su Mac, quindi procedere con l’eliminazione delle righe selezionate. Successivamente, incollare il  **JSON**:

```
{
    "type": "AdaptiveCard",
    "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5",
    "backgroundImage": {
        "url": "https://adaptivecards.io/content/backgroundImage.png",
        "verticalAlignment": "Center"
    },
    "body": [
        {
            "type": "Container",
            "style": "emphasis",
            "bleed": true,
            "items": [
                {
                    "type": "TextBlock",
                    "text": "Device selection",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": true
                }
            ]
        },
        {
            "type": "Container",
            "style": "default",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "Please select which device you would like to request:",
                    "wrap": true,
                    "size": "Medium"
                }
            ],
            "spacing": "None"
        },
        {
            "type": "Container",
            "spacing": "None",
            "items": [
                {
                    "type": "Input.ChoiceSet",
                    "id": "deviceSelectionId",
                    "style": "expanded",
                    "choices": [
                        {
                            "title": "Laptop - Dell XPS 13",
                            "value": "1"
                        },
                        {
                            "title": "Desktop - HP EliteDesk 800",
                            "value": "2"
                        },
                        {
                            "title": "Tablet - Microsoft Surface Pro",
                            "value": "3"
                        },
                        {
                            "title": "Smartphone - iPhone 15 Pro",
                            "value": "4"
                        },
                        {
                            "title": "Smartphone - Samsung Galaxy S23",
                            "value": "5"
                        }
                    ]
                }
            ]
        },
        {
            "type": "Container",
            "spacing": "None",
            "style": "emphasis",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "Additional Information",
                    "wrap": true
                },
                {
                    "type": "Input.Text",
                    "id": "commentsId",
                    "placeholder": "Please provide any specific requirements or comments",
                    "isMultiline": true,
                    "spacing": "Small"
                }
            ]
        },
        {
            "type": "Container",
            "spacing": "Medium",
            "items": [
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "Request type:",
                            "value": "New Device"
                        },
                        {
                            "title": "Response time:",
                            "value": "3-5 Business Days"
                        }
                    ],
                    "spacing": "Small"
                }
            ]
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Submit Request"
        }
    ]
}
```


Questo **JSON** rappresenta attualmente un segnaposto e un’anteprima di quello che verrà utilizzato come base per la scheda, ma sotto forma di formula anziché di JSON, poiché verrà fatto riferimento alla variabile globale **Global.VarDevices.value**, che memorizza la risposta dell’azione del connettore SharePoint **Get items**.

6. Salvare e chiudere la card.

![](./images/device-flow-step-19.png)

Scorrendo fino in fondo al nodo, sono visibili le variabili di output. **commentsId** e **deviceSelectionId** sono due variabili che memorizzano i valori provenienti dagli elementi della scheda con cui gli utenti interagiscono. Tali valori verranno utilizzati nelle fasi successive del flow.

![](./images/device-flow-step-20.png)

7. Ora modificare la Card trasformandola in **Formula** card.

![](./images/device-flow-step-21.png)

8. Sostituire la Card premendo _Ctrl + A_ su Windows o _Command + A_ su Mac e incollare questo:

```
{
  type: "AdaptiveCard",
  '$schema': "https://adaptivecards.io/schemas/adaptive-card.json",
  version: "1.5",
  backgroundImage: {
    url: "https://adaptivecards.io/content/backgroundImage.png",
    verticalAlignment: "Center"
  },
  body: [
    {
      type: "Container",
      style: "emphasis",
      bleed: true,
      items: [
        {
          type: "TextBlock",
          text: "Device selection",
          weight: "Bolder",
          size: "Large",
          wrap: true
        }
      ]
    },
    {
      type: "Container",
      style: "default",
      items: [
        {
          type: "TextBlock",
          text: "Please select which device you would like to request:",
          wrap: true,
          size: "Medium"
        }
      ],
      spacing: "None"
    },
    {
      type: "Container",
      spacing: "None",
      items: [
        {
          type: "Input.ChoiceSet",
          id: "deviceSelectionId",
          style: "expanded",
          choices: ForAll(Global.VarDevices.value,
            {
              title: If(IsBlank(Model), "NA", Model),
              value: If(IsBlank(ID), "NA", ID)
            }
          )
        }
      ]
    },
    {
      type: "Container",
      spacing: "None",
      style: "emphasis",
      items: [
        {
          type: "TextBlock",
          text: "Additional Information",
          wrap: true
        },
        {
          type: "Input.Text",
          id: "commentsId",
          placeholder: "Please provide any specific requirements or comments",
          isMultiline: true,
          spacing: "Small"
        }
      ]
    },
    {
      type: "Container",
      spacing: "Medium",
      items: [
        {
          type: "FactSet",
          facts: [
            {
              title: "Request type:",
              value: "New Device"
            },
            {
              title: "Response time:",
              value: "3-5 Business Days"
            }
          ],
          spacing: "Small"
        }
      ]
    }
  ],
  actions: [
    {
      type: "Action.Submit",
      title: "Submit Request",
      id: "deviceSubmittedId"
    }
  ]
}
```

9. Salvare il Topic.
## Creazione Flow

Nel Topic **Request device**, andare sotto all'Adaptive card e premere il simbolo + per aggiungere un nuovo nodo.

1. Selezionare **Add a tool** -> **Basic tools** -> **New Agent Flow**.

![](./images/device-flow-step-22.png)

Il Designer degli Agent flow verrà caricato con un trigger e un’azione.

**Trigger – Quando un agente richiama il flow**  
Questo attiverà un flow da un agente di Copilot Studio.

**Azione – Rispondere all’agente**  
Questa operazione invia una risposta che può contenere valori di output all’agente di Copilot Studio.

2. Selezionare il trigger.

![](./images/device-flow-step-23.png)

3. Premere **Add an input** e selezionare **Text**.

![](./images/device-flow-step-24.png)

![](./images/device-flow-step-25.png)

4. Compilare il nome dell'input con:

```
DeviceSharePointId
```

![](./images/device-flow-step-26.png)

5. Ora aggiungere un secondo input sempre testuale. Impostare il nome con:

```
User
```


![](./images/device-flow-step-27.png)

6. Infine aggiungere un ultimo input testuale:

```
AdditionalComments
```

![](./images/device-flow-step-28.png)

Per **AdditionalCommnets** impostare il campo come facoltativo premendo il simbolo (...) e poi **Make the field optional**

![](./images/device-flow-step-29.png)

7. Aggiungere sotto al trigger un nuovo nodo, cercare **Get Item** di SharePoint.

![](./images/device-flow-step-30.png)

8. Selezionare il simbolo (...) e poi rinominare il tool con:

```
Get Device
```


![](./images/device-flow-step-31.png)

![](./images/device-flow-step-32.png)

9. Nel campo  **Site Address** e **List Name** inserire il sito e la lista SharePoint creata in precedenza. Nel campo Id inserire tramite il simbolo del fulmine il Dynamic Content  **DeviceSharePointId** relativo al trigger .

![](./images/device-flow-step-33.png)

10. Successivamente in **Advanced paramenters** premere **Show All**.

![](./images/device-flow-step-34.png)

11. In **Limit Columns by View** selezionare **All items**

![](./images/device-flow-step-35.png)

12. Successivamente premere l'icona del + sotto il Get Device tool e cercare **send an email**. Selezionare **Send an email (V2)** tool di **Office 365 Outlook connector**.

![](./images/device-flow-step-36.png)

13. Rinominare il Tool in :

```
Send an email to manager
```

14. Nella sezione **To** selezionare il proprio account.

15. Per la sezione **Subject** inserire:

```
Request type: new device
```

16. Per il **Body**:

```
Hi,

New device requested from [USER PLACEHOLDER]

Manufacturer: [MANUFACTURER PLACEHOLDER]
Model: [MODEL PLACEHOLDER]
Link to item in SharePoint 
Additional comments from [USER PLACEHOLDER]: 

This is an automated email from an Agent
```

![](./images/device-flow-step-37.png)

16. Come prossimo punto inserire nel Body tramite il simbolo del fulmine i Dynamic Content segnati in CAPS tra parentesi quadre.

![](./images/device-flow-step-38.png)

17. Per il link di SharePoint è necessario aprire l'editor Html con l'icona `</>` .

![](./images/device-flow-step-39.png)

Premere prima di "Link to item in SharePoint"  e aggiungere:

```
<a href="
```

![](./images/device-flow-step-40.png)

Premere dopo le " e inserire come Dynamic Content dal **Get Item** di SharePoint il **Link to Item**.

![](./images/device-flow-step-41.png)

Inserire questo dopo il Dynamic Content del Link:

```
">
```

![](./images/device-flow-step-42.png)

Successivamente inserire dopo la scritta "Link to item in SharePoint":

```
</a>
```

![](./images/device-flow-step-43.png)

Con questo è terminato l'inserimento del hyperlink per SharePoint, quindi premere l'icona `</>`  per uscire dall'editor.

![](./images/device-flow-step-44.png)

18. Infine non resta che inserire una funzione per la sezione di Additional Comments. Selezionare uno spazio vuoto dopo i : e premere il simbolo _fx_ .

![](./images/device-flow-step-45.png)

Inserire nel box funzione:

```
if(empty())
```

Dopo inserire come Dynamic Content l'input **AdditionalComments** dal trigger del Flow.

![](./images/device-flow-step-46.png)

Successivamente dopo la parentesi inserire:

```
, 'None',
```

![](./images/device-flow-step-47.png)

Come ultimo punto Inserire nuovamente dopo l'ultima virgola  il Dynamic Content **AdditionalComments** .

![](./images/device-flow-step-48.png)

>[!NOTE]
>La formula verifica se il campo `AdditionalComments` del trigger è vuoto.  Se è vuoto restituisce il valore `"None"`, altrimenti restituisce il contenuto.

19. Selezionare il nodo "Respond to the agent" e inserire come Output testuale:

```
ModelValue
```

![](./images/device-flow-step-49.png)

Come valore inserire il contenuto dinamico **Model** del nodo **Get item**.

![](./images/device-flow-step-50.png)

20. Il Flow è terminato, ora non resta che salvare, premere **Save draft**. Andare su **Overview** e selezionare **Edit**.

![](./images/device-flow-step-51.png)

Inserire nome e descrizione del Flow :

- Name:

```
Send device request email
```

- Description:

```
This flow starts when an agent manually triggers it and provides device and user details. It retrieves device information from a SharePoint list using the provided device ID. After successfully getting the device details, it sends an email to a manager with the request information, and sends a value back to the agent.
```

![](./images/device-flow-step-52.png)

21. Tornare sul Designer e premere **Publish**.

![](./images/device-flow-step-53.png)

![](./images/device-flow-step-54.png)

## Aggiungere il Flow al Topic

Per aggiungere il Flow appena creato al Topic "Request Devices" selezionare Agents nel menù presente a sinistra.

![](./images/device-flow-step-55.png)

1. Selezionare l'agente **Device Booker** , andare su Topic e selezionare "Request devices".

![](./images/device-flow-step-56.png)

2. Andare sotto al nodo **Ask with adaptive card** premere il + e selezionare **Add a tool** e successivamente il Flow appena creato.

![](./images/device-flow-step-57.png)

3. Premere il simbolo (...)  del primo campo e selezionare **deviceSelectionId**.

![](./images/device-flow-step-58.png)

4. Dopo nel campo user inserire **User.DisplayName**.

![](./images/device-flow-step-59.png)

5. Premere > per espandere la sezione **Advanced Inputs** selezionare il simbolo (...) e successivamente la sezione Formula.

![](./images/device-flow-step-60.png)

Inserire la seguente Formula _fx_ :

```
If(IsBlank(Topic.commentsId), "", Topic.commentsId)
```

>[!NOTE]
>La formula verifica se il campo `Topic.commentsId` è vuoto (`Blank()`).  Se lo è, restituisce una stringa vuota (`""`), altrimenti restituisce il valore di `commentsId`.  Serve a evitare valori NULL in output che potrebbero causare errori in controlli o funzioni.  In pratica, converte un valore vuoto in una stringa vuota utilizzabile.

![](./images/device-flow-step-61.png)

6. Premere il + dopo il nodo "Action" del Flow e inserire un nodo **Send a message**  con il seguente contenuto:

```
Thanks, [User.DisplayName]. 
Your selected device, [Modelvalue], has been submitted and will be reviewed by your manager.
```

Dove i contenuti fra parentesi quadre devono essere sostituiti con le variabili corrispondenti.

![](./images/device-flow-step-62.png)

7. Inserire sotto un nuovo nodo. Selezionare **Topic Management** poi **Go to another Topic** e infine **End of Conversation**.

![](./images/device-flow-step-63.png)

![](./images/device-flow-step-64.png)

8. Salvare il Topic.
## Istruzioni 

Prima di procedere con i test sull'agente è necessario inserire le istruzioni.
1. Andare su Overview, selezionare **edit** nel box **Instructions** e inserire le seguenti istruzioni:

```
# Context

Device Booker is an agent that allows users to see available devices and request devices from a SharePoint Device Inventory List. The agent interacts only with SharePoint Lists to retrieve device availability information and to submit device booking requests.

# Action

[Available device]  -> Used to view the list of devices that are currently marked as Available in the SharePoint Device Inventory List before making a booking request.  
[Request device]  -> Used to submit a request for a device that is currently available in the SharePoint Device Inventory List by specifying device details and booking dates.

# Rules

The agent can only read available devices and create device requests in the SharePoint Lists.  
The agent cannot approve requests, modify inventory manually, manage maintenance status, or process device returns.    
The agent must use a professional and concise tone when interacting with users.
```

2. Sostituire i Topic segnati fra parentesi quadre tramite il `/` e selezionando il Topic corrispondente.

![](./images/device-flow-step-65.png)

3. Premere Save per salvare le Istruzioni.
## Testing

Iniziare una nuova sessione nella finestra di Test, selezionare il simbolo (...) e spuntare **Track between topics**.

![](./images/device-flow-step-66.png)

Testare il funzionamento dell'agente richiedendo un dispositivo, qui sotto un esempio:

```
I need a laptop
```

Proseguire con il test a piacere.

>[!IMPORTANT]
>**Lab Completato**
>
>Con questo ultimo passaggio, il laboratorio per la creazione degli Agent Flows in Copilot Studio è completato.

