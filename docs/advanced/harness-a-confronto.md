# Standard harness e GitHub Copilot harness a confronto

[Back to Advanced](./index.md)

Questo documento spiega che cos'è una harness, come si accede a ciascuna in Copilot Studio e come si traducono i componenti da una harness all'altra. È il riferimento da tenere aperto mentre si svolgono i due percorsi.

## Modello, harness e orchestrazione

- Il **modello** è il motore linguistico: ragiona e genera testo.
- La **harness** è l'ambiente di esecuzione che circonda il modello: decide quali componenti sono disponibili, quale contesto arriva al modello, come vengono chiamati gli strumenti, come si gestiscono file, memoria, monitoraggio e sicurezza.
- L'**orchestrazione** è il modo in cui, dentro la harness, si decide il passo successivo.

Due agenti con lo stesso modello possono quindi comportarsi in modo molto diverso se girano su harness diverse. Copilot Studio ne offre tre: **Copilot chat** (estende Microsoft 365 Copilot Chat con conoscenza aziendale), **standard** e **GitHub Copilot**. Questi laboratori usano le ultime due.

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Pensata per | Conversazioni strutturate, componenti definiti dal maker, controllo prevedibile | Lavoro complesso e in più passaggi, dove il percorso non si può disegnare in anticipo |
| Orchestrazione | Configurabile: classica (trigger dei topic) o generativa | Orchestrazione orientata all'obiettivo: pianifica, agisce, verifica i risultati e corregge |
| Componenti tipici | Topic, nodi, adaptive card, prompt, agent flow, child agent, connected agent, knowledge | Istruzioni, skill, strumenti (connettori, MCP, workflow), connected agent, memoria, file creati |
| Superficie di authoring | Pagine separate: Overview, Knowledge, Tools, Agents, Topics, Activity, Analytics | Schede Build, Preview, Evaluate, Monitor su un'unica superficie |
| Fatturazione | Licenze Copilot Studio standard (Copilot Credits; condizioni specifiche per utenti con licenza Microsoft 365 Copilot in scenari interni autenticati) | A consumo in Copilot Credits, anche durante creazione in linguaggio naturale, Preview e valutazioni |

> [!IMPORTANT]
> Un agente creato con una harness non può essere trasferito nell'altra. La scelta si fa alla creazione: se cambi idea, devi ricostruire l'agente. Per questo i due percorsi del caso pratico sono due costruzioni separate dello stesso agente.

## Come si accede a ciascuna harness

**GitHub Copilot harness.** Nella home di Copilot Studio, con l'interruttore **New experience** attivo, le schede **Agent** e **Workflow** creano componenti GitHub Copilot. In alternativa: **Agents** nel menu di sinistra, poi **New agent**.

**Standard harness.** Ci sono tre strade documentate su Learn:

1. nella home seleziona **Other ways to build**;
2. dal menu con i tre puntini in fondo alla barra laterale seleziona **Open classic experience**;
3. disattiva l'interruttore **New experience** in alto a destra; la home e la pagina **Agents** tornano a quelle della standard harness.

Gli agenti standard esistenti si aprono normalmente dalla pagina **Agents**.

## Mappa dei componenti

La tabella mostra come ogni capacità usata nel percorso standard viene realizzata nel percorso GitHub Copilot. Non è una corrispondenza uno a uno: spesso cambia anche il modo di ragionare sul problema.

| Esigenza | Standard harness | GitHub Copilot harness | Perché cambia |
| --- | --- | --- | --- |
| Definire il comportamento generale | Istruzioni dell'agente | Istruzioni dell'agente | Nella GitHub Copilot harness le istruzioni sono il volante principale, perché non esistono topic a cui affidare i percorsi |
| Percorso di conversazione controllato | Topic con nodi, condizioni, variabili | Skill con passaggi, regole di decisione e criteri di completamento | La skill descrive la procedura in linguaggio naturale e viene caricata quando la richiesta corrisponde alla sua descrizione |
| Modulo strutturato in chat | Adaptive card nel nodo **Ask with adaptive card** | Raccolta guidata dei campi descritta in una skill | La GitHub Copilot harness non prevede l'authoring di adaptive card in chat; le card restano disponibili nei workflow (ad esempio verso Teams) |
| Estrarre dati da un documento | Prompt con input documento (PDF o immagine) dentro un agent flow | Lettura nativa del file allegato con le skill integrate | Il modello legge direttamente PDF e DOCX; la skill decide che cosa estrarre e dove scriverlo |
| Leggere e scrivere dati strutturati | Agent flow con il connettore Dataverse, oppure Dataverse come knowledge | Microsoft Dataverse MCP Server come strumento | Un solo server MCP espone ricerca, lettura, creazione e aggiornamento; si limitano gli strumenti invece di costruire un flow per operazione |
| Calcolo e formattazione deterministici | Espressioni nell'agent flow | Script Python in una skill (sandbox) | Il codice garantisce lo stesso risultato a ogni esecuzione |
| Generare un documento Word | Prompt con output **Document (preview)** e template con segnaposto | Skill con script `python-docx` | Il layout vive nel codice invece che in due posti (prompt e template) |
| Specialista riutilizzabile | Connected agent (impostazione **Let other agents connect to and use this one**) | Connected agent (impostazione **Allow other agents to connect** in **AI & behavior**) | Stesso concetto: agente completo con ciclo di vita proprio |
| Sotto-procedura interna all'agente | Child agent | Skill | La GitHub Copilot harness non ha child agent |
| Automazione su evento | Trigger dell'agente modificato in Power Automate | Workflow con trigger di connettore, nodi Classify, Scope, Loop, Agent, Human review | Il workflow vive in Copilot Studio, si testa nodo per nodo e si versiona |
| Revisione umana | Approvazioni e card in un flow | Nodo **Human review** e strumento **Request for information** dei nodi Agent | La richiesta può essere fissa (nodo) o decisa dall'agente (strumento) |
| Calendario e persone del tenant | Connettori Office 365 Outlook e Office 365 Users come strumenti | **Work IQ (Preview)** come strumento MCP | Learn indica Work IQ (Preview) per i nuovi progetti nella GitHub Copilot harness; gli strumenti MCP per singolo carico di lavoro restano solo per compatibilità |
| Collezioni di file versionati come conoscenza | **File groups** con istruzioni | File caricati singolarmente e regole nelle istruzioni | I file group sono una funzione della standard harness |
| Test interattivo | Pannello **Test** con mappa delle attività | Scheda **Preview** con traccia del ragionamento e delle chiamate | |
| Test di regressione | Valutazioni con set di test | Scheda **Evaluate** e area **AgentOps** | |
| Telemetria | Analytics, reazioni, CSAT, Application Insights | Scheda **Monitor**, reazioni | |

## Come scegliere

Scegli la **standard harness** quando:

- il processo è noto e va eseguito sempre allo stesso modo, con domande, risposte e rami definiti;
- servono adaptive card interattive nella conversazione o un controllo puntuale di ogni nodo;
- vuoi un costo prevedibile e gli utenti sono dipendenti con licenza Microsoft 365 Copilot in uno scenario interno autenticato.

Scegli la **GitHub Copilot harness** quando:

- le richieste sono varie e l'agente deve combinare documenti, dati e strumenti in modo diverso a seconda del caso;
- serve leggere file e produrre file (documenti, analisi) in più passaggi;
- vuoi procedure modulari (skill) riutilizzabili tra agenti e calcoli affidati al codice;
- ti servono Work IQ e la memoria dell'agente.

Nel caso pratico del PMO entrambe le scelte sono difendibili. La standard harness rende ogni passaggio esplicito e ispezionabile (utile in un processo di governance), al prezzo di più componenti da costruire e mantenere. La GitHub Copilot harness riduce i componenti e gestisce meglio la variabilità dei documenti, al prezzo di un comportamento meno deterministico che va presidiato con skill precise, permessi minimi e valutazioni.

## Limiti da conoscere prima di iniziare

| Tema | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| File caricati dall'utente in chat | Con **File uploads** attivo: DOCX, CSV, PDF, TXT, immagini; 15 MB per file; PDF fino a 40 pagine | Allegati in conversazione con limiti di dimensione documentati su Learn; nei laboratori usiamo un limite prudente di 15 MB |
| Input documento dei prompt | Solo PDF e immagini (PNG, JPG, JPEG), meno di 50 pagine | Non si usano prompt tool: il modello legge il file |
| Documenti scansionati | Da evitare: nei laboratori usiamo solo PDF e DOCX con testo selezionabile | Da evitare per la stessa ragione |
| Work IQ e calendari | Solo persone e calendari del proprio tenant | Solo persone e calendari del proprio tenant; scritture solo se abilitate dall'amministratore |

Riferimenti: [Harnesses in Copilot Studio](https://learn.microsoft.com/microsoft-copilot-studio/harnesses-overview), [Access standard harness agents and agent flows](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/switch-experiences), [Agents powered by the GitHub Copilot harness overview](https://learn.microsoft.com/microsoft-copilot-studio/agents-experience/overview).
