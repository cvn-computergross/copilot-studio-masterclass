# Lab 01 - Environment Setup

Previous: Start | [Back to Standard Harness](../index.md) | [Next: Lab 02](../02-knowledge-sources/README.md)

<!-- icon: clock-countdown --> **Tempo stimato:** ~45 minuti · <!-- icon: toolbox f-standard --> **Harness:** standard

## Scenario

Il reparto IT di Zava vuole sperimentare Copilot Studio per offrire ai colleghi un assistente di supporto di primo livello, disponibile in chat e capace di rispondere con un linguaggio semplice. Prima di costruire qualsiasi agente serve però un posto in cui lavorare: un tenant Microsoft 365, l'accesso a Copilot Studio e un ambiente di sviluppo separato da quello predefinito.

In questo lab si prepara l'ambiente di lavoro (tenant, trial, developer environment, permesso di pubblicazione, publisher e solution) e si crea il primo agente, **IT Support**, descritto in linguaggio naturale e basato sulle sue istruzioni e su un sito pubblico di supporto Microsoft.

## Percorso di setup

A sinistra i sei passi del lab, nell'ordine; a destra, con lo stesso numero, dove si trova ciò che ogni passo crea: è l'ambiente in cui si lavorerà in tutti i lab successivi.

![Percorso del Lab 01: dall'account Microsoft 365 al primo agente IT Support, e dove si trovano account, trial, gruppo AgentCreators, developer environment, solution CSMFirstAgent e agente](../../images/lab01-percorso-setup.svg)

## Prerequisiti

1. Un indirizzo email aziendale o scolastico (gli indirizzi personali, come @outlook.com o @gmail.com, non sono supportati).
2. Accesso a internet e un browser (consigliati Edge, Chrome o Firefox).
3. Familiarità con `Microsoft 365`.
4. (Opzionale) Una carta di credito o un altro metodo di pagamento, in caso di acquisto di licenze a pagamento.

## Ottenere un Microsoft 365 Account

Per accedere a Copilot Studio e usufruire della piattaforma è possibile usare un account esistente o seguire questi step per procurarsi la licenza appropriata:

1. Acquistare una `Microsoft 365 Business Subscription`
2. Andare su [Microsoft 365 Business Plans and Pricing Page](https://www.microsoft.com/microsoft-365/business/microsoft-365-plans-and-pricing)
3. Selezionare l'opzione meno costosa per iniziare, Microsoft 365 Business Basic, premere su `Try for free` e compilare il form guidato con le informazioni per l'account e metodo di pagamento.

![](./images/ottenere-microsoft-365-account-01.png)

4. Una volta ottenuto l'account eseguire il `login`.

> [!NOTE]
> **Licenza Microsoft 365 Copilot**
>
> Per pubblicare agenti in **Microsoft 365 Copilot Chat** o collegarli ai dati aziendali (come **SharePoint, OneDrive o Dataverse**) è indispensabile una licenza **Microsoft 365 Copilot**. È un componente aggiuntivo (_add-on_): per i dettagli consultare il [sito](https://www.microsoft.com/microsoft-365/copilot#plans) dedicato alle opzioni di licenza.

## Iniziare la Copilot Studio Trial

Una volta ottenuto un `Microsoft 365 Tenant`, è necessario l'accesso a `Copilot Studio`. È possibile riscattare gratuitamente una Trial di 30 giorni seguendo questi step:

1. Navigare su [aka.ms/TryCopilotStudio](https://aka.ms/TryCopilotStudio).

![](./images/iniziare-copilot-studio-trial-01.png)

2. Inserire le informazioni dell'account creato negli step precedenti e premere `Next`.

![](./images/iniziare-copilot-studio-trial-02.png)

3. Una volta riconosciuto l'account, selezionare `Sign In`.

![](./images/iniziare-copilot-studio-trial-03.png)

4. Premere su `Start Free Trial`.

> [!NOTE]
> **Durata della prova**
>
> La versione di prova gratuita offre tutte le funzionalità di Copilot Studio. Verranno inviate notifiche via email relative alla scadenza della prova. È possibile estendere la prova a incrementi di 30 giorni (fino a un massimo di 90 giorni di runtime dell'agente).
>
> Se l'amministratore del tenant ha disattivato la registrazione self-service, verrà visualizzato un errore: in tal caso, contattare l'amministratore Microsoft 365 per riattivarla.

## Creare un nuovo Developer Environment

Una best practice nello sviluppo di Agenti è lavorare su un Environment diverso da quello Default, quindi per proseguire con questo lab seguire questi step per la creazione del nuovo ambiente.

1. Andare su [Power Apps Developer Plan website](https://aka.ms/PowerAppsDevPlan).

![](./images/creare-nuovo-developer-environment-01.png)

2. Inserire l'`email address` -> Spuntare la `checkbox` -> Selezionare `Start free`.

3. Dopo aver eseguito il login per il Developer Plan, verrà aperto [Power Apps](https://make.powerapps.com/). 

4. Utilizzare questo nuovo `Environment` per il Lab su `Copilot Studio`.

> [!NOTE]
> **Account dell'organizzazione**
>
> Se si utilizza un account Microsoft 365 esistente e non ne è stato creato uno nello Step 1, ad esempio utilizzando il proprio account nell'organizzazione di lavoro, è possibile che l'amministratore IT (o il team equivalente) che gestisce il tenant/ambiente abbia disattivato il processo di registrazione. In tal caso, contattare l'amministratore oppure creare un tenant di test come indicato nello Step 1.

## Abilitare la Pubblicazione con la Copilot Studio Trial

La trial di **Copilot Studio** è stata aggiornata e, attualmente, la pubblicazione degli agenti non è consentita per impostazione predefinita. Per abilitare tale funzionalità, è necessario assegnare il ruolo **Copilot Studio Authors** tramite il **Power Platform Admin Center**.

Come primo passaggio, è richiesta la creazione di un **gruppo di sicurezza** che includa tutti gli utenti autorizzati alla pubblicazione; tale gruppo dovrà successivamente essere associato al ruolo **Copilot Studio Authors**.

1. Andare sull' [Admin Center](https://admin.cloud.microsoft/)

2. Nella sezione **Teams & groups** selezionare **Active teams & groups**

![](./images/abilitare-pubblicazione-copilot-studio-01.png)

3. Andare su **Security groups** e premere **Add a security group** e chiamarlo `AgentCreators`, successivamente premere **Next**.

![](./images/abilitare-pubblicazione-copilot-studio-02.png)

4. Verificare i dati inseriti e premere **Create group**. Dopo ciò cercare il security group appena creato.

![](./images/abilitare-pubblicazione-copilot-studio-03.png)

5. Andare nella sezione **Members**, premere **view all and manage members**

![](./images/abilitare-pubblicazione-copilot-studio-04.png)

6. Premere **Add members**, cercare il proprio account e aggiungersi come membro.
7. Terminata la creazione del Security group recarsi su [Power Platform admin center](https://admin.powerplatform.microsoft.com/)
8. Dalla schermata **Home** andare su **Manage** e poi **Tenant Settings**.

![](./images/abilitare-pubblicazione-copilot-studio-05.png)

![](./images/abilitare-pubblicazione-copilot-studio-06.png)

9. Selezionare **Copilot Studio Authors** e cambiare da **All Users** al security group creato in precedenza, poi premere **Done** e successivamente **Save**.

![](./images/abilitare-pubblicazione-copilot-studio-07.png)

![](./images/abilitare-pubblicazione-copilot-studio-08.png)

## Solution e Publisher

Una volta aperto [Copilot Studio](https://copilotstudio.microsoft.com/), essere sicuri di lavorare sul nuovo `developer environment`,  
per cambiare `Environment` in alto a destra selezionare il box `Environment` e cambiare il `default Environment` con quello nuovo. 
Il prossimo passo è creare una Solution, un contenitore logico utilizzato per organizzare, gestire e distribuire in modo strutturato i componenti di una soluzione applicativa.

> [!TIP]
> **Una solution per ogni agente**
>
> È considerata una best practice creare ogni agente all’interno di una **solution specifica**, al fine di mantenere una chiara separazione logica tra i diversi componenti della piattaforma.
> Le solution permettono di organizzare e versionare gli elementi dell’agente, facilitando il ciclo di vita applicativo e le attività di aggiornamento e rilascio.


1. Dopo aver selezionato il giusto `Copilot Studio environment`, premere sull'`ellipsis icon (. . .)` nel menù a sinistra, successivamente `Solutions` sotto `Explore`.

![](./images/solution-publisher-01.png)

2. Verrà aperto il `Solution Explorer`: premere `+ New solution`.

![](./images/solution-publisher-02.png)

3. Il pannello `New solution` apparirà e sarà possibile definire i dettagli della `Solution`. Prima di fare ciò è necessario creare un nuovo `Publisher`: selezionare `+ New publisher`.

![](./images/solution-publisher-03.png)

4. Apparirà la scheda `Properties` del nuovo `Publisher`, con i campi da compilare.

Qui è possibile delineare i dettagli del `Publisher` che verranno utilizzati come etichetta o marchio per identificare chi ha creato o possiede la `Solution`.

5. Compilare come in figura i dettagli del Publisher 

	- Display Name: `CSM Solutions`
	- Name: `CSMSolutions`
	- Description: `Copilot Studio Masterclass`
	- Prefix: `csm`
	- Prefix value: `77000`

![](./images/solution-publisher-04.png)

6. Premere `Save` per creare il `Publisher`.

7. La pagina `New publisher` verrà chiusa e il riquadro `New solution` si aprirà con il Publisher appena creato selezionato.

8. Compilare i dati mancanti nella Solution con i seguenti dati:

Display Name:

```
CSMFirstAgent
```

Name:

```
CSMFirstAgent
```

9. Visto che è stata creata una nuova `Solution` il  [**Version** number](https://learn.microsoft.com/power-apps/maker/data-platform/update-solutions#understanding-version-numbers-for-updates/?WT.mc_id=power-172615-ebenitez) di default sarà `1.0.0.0`.

10. Selezionare la casella `Set as your preferred solution`.

11. Espandere `More Options` per vedere dettagli aggiuntivi della `Solution`, lasciare i campi vuoti per questo lab.

12. Premere `Create`.

La soluzione `CSMFirstAgent` è stata creata. 
Non saranno presenti `components` finché non verrà creato un agente in Copilot Studio. Selezionare l’icona della `Back Arrow` per tornare al Solution Explorer.
La `Current preferred Solution` risulta essere `CSMFirstAgent` in quanto in precedenza è stata selezionata la casella di controllo **Set as your preferred solution**.

## Creazione del primo Agente

Questo laboratorio ha l’obiettivo di guidare alla creazione del primo agente utilizzando Copilot Studio. L’attività è pensata come un primo approccio pratico alla piattaforma.

Nel corso del laboratorio viene creato un agente minimale, privo di connettori, azioni o fonti esterne. L’agente si basa unicamente sulle istruzioni fornite, che ne definiscono lo scopo, il tono e le modalità di interazione con l’utente.

1. Dalla home page di [Copilot Studio](https://copilotstudio.microsoft.com/) premere **Agents**.

![](./images/creazione-primo-agente-01.png)

2. Nella schermata **Agents** è possibile visualizzare la lista completa degli agenti creati nell'environment; proseguire inserendo la descrizione del primo agente:

```
Crea un agente chiamato IT Support con descrizione "Assistente di supporto IT di primo livello per l’azienda Zava". Deve fornire supporto tecnico di base usando un linguaggio semplice e porre domande solo se strettamente necessario. Non può recuperare password, bypassare MFA, sbloccare account o fornire codici. Il tono deve essere sempre professionale, calmo e neutro.
```

![](./images/creazione-primo-agente-02.png)

3. Aspettare che Copilot Studio termini il setup dell'agente ed esplorare la schermata di personalizzazione dell'agente.

4. Come ultima aggiunta premere **Add knowledge** nel box Knowledge e inserire come fonte di conoscenza il seguente Url selezionando **Public website** all'apertura del wizard:

```
https://support.microsoft.com
```

5. Salvare la fonte di conoscenza.

Terminato quest'ultimo passaggio premere in alto a destra il tasto **Test** che aprirà una schermata intitolata "Test your Agent" dove è possibile interagire con l'agente prima di pubblicarlo.
Testare a piacere il funzionamento dell'agente appena creato.

> [!IMPORTANT]
> **Lab Completato**
>
> L'ambiente di lavoro è pronto e il primo agente risponde nel pannello di test. In questo lab si è visto:
>
> - come ottenere un tenant Microsoft 365 e la trial di Copilot Studio;
> - perché lavorare in un developer environment separato da quello predefinito;
> - come abilitare la pubblicazione con il ruolo **Copilot Studio Authors**;
> - come creare publisher e solution e impostare la preferred solution;
> - come creare un agente descrivendolo in linguaggio naturale e aggiungergli un sito pubblico come fonte di conoscenza.


