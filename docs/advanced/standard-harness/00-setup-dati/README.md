# Lab 00 - Setup dati: il PMO Demand Hub

Previous: Start | [Back to Standard Harness](../index.md) | [Next: S01](../01-agente-orchestratore/README.md)

## Scenario

Zava S.p.A. è una società tecnologica italiana con 420 dipendenti, sede a Milano e uffici a Torino, Bologna e Roma. Ogni anno le funzioni aziendali (Acquisti, Vendite, Risorse Umane, Servizio Clienti, IT Operations, Sicurezza) propongono nuovi progetti IT. Le proposte vengono finanziate attraverso cinque **programmi di investimento**, ciascuno con un budget e con criteri di valutazione propri.

Il processo è gestito dall'**Ufficio Demand e PMO IT** e oggi funziona così:

- le proposte arrivano in una casella email condivisa, in formati diversi, spesso senza tutte le informazioni richieste;
- un analista apre ogni documento, lo registra in un foglio Excel e lo assegna a un programma;
- la valutazione con i criteri pesati viene fatta a mano, con interpretazioni diverse da analista ad analista;
- per ogni proposta valutata si prepara un dossier per il Comitato (circa due ore di lavoro);
- la sessione di revisione con lo sponsor e l'architetto di riferimento si organizza con molti scambi di email.

I problemi sono noti: tempi di presa in carico lunghi, valutazioni poco confrontabili, dossier con strutture diverse, poco tempo per l'analisi vera e propria. Nei laboratori di questo percorso il PMO affida la parte ripetitiva a un sistema di agenti, guidato dall'**Agente Demand IT**, e lascia le decisioni alle persone coinvolte nel processo:

| Attore | Ruolo nel processo | Interagisce con |
| --- | --- | --- |
| Proponente | Responsabile di funzione che presenta il business case | Agente Demand IT (chat) oppure email |
| Analista PMO | Verifica, conferma il programma, conferma la registrazione della valutazione | Agente Demand IT, PMO Demand Hub, Teams |
| Sponsor interno | Dirigente che risponde della proposta | Sessione di revisione |
| Architetto di riferimento | Valuta gli aspetti tecnici per il programma | Agente Comitato, sessione di revisione |
| Comitato | Decide | Dossier di revisione |

Tutte le persone sono interne a Zava S.p.A. Non è un dettaglio: Work IQ e i connettori di calendario leggono disponibilità e profili solo all'interno del proprio tenant, per cui lo scenario non prevede di pianificare riunioni con persone esterne.

Il primo passo non riguarda ancora gli agenti. Oggi i dati del processo sono sparsi tra la casella email e un foglio Excel: serve prima un archivio comune e strutturato, che persone e agenti possano leggere e scrivere.

Prima che un agente possa registrare e valutare proposte, il PMO ha bisogno di un posto dove i dati vivono in modo strutturato: il **PMO Demand Hub**. In questo laboratorio vengono create in Dataverse le cinque tabelle del processo (Programmi, Criteri di valutazione, Proponenti, Proposte, Valutazioni), un'app model-driven per consultarle e i dati di partenza: cinque programmi di investimento con i loro criteri pesati. Infine viene preparata in SharePoint la cartella con i documenti di conoscenza del PMO.

Agent Academy fornisce per l'Hiring Agent una soluzione già pronta da importare. Qui il modello viene costruito a mano: richiede più tempo, ma permette di capire ogni scelta che gli agenti useranno dopo (nomi logici, codici automatici, scelte, relazioni).

> [!WARNING]
> **Prerequisito**
>
> Per svolgere questo lab occorre avere a disposizione:
>
> - Un ambiente di laboratorio con Dataverse (lo stesso dei fondamenti va bene) e il ruolo **System Customizer** o **System Administrator**.
> - Il publisher **CSM Solutions** con prefisso `csm` e prefisso delle scelte `77000` (creato nel modulo 1 dei fondamenti; se non esiste, crearlo durante la creazione della soluzione).
> - I file [`programs.csv`](../../../resources/advanced/data/programs.csv) e [`evaluation-criteria.csv`](../../../resources/advanced/data/evaluation-criteria.csv).
> - Un sito SharePoint dove poter creare cartelle e caricare file (per la cartella della conoscenza PMO), e i file [`Zava_PMO_Linee_Guida_Business_Case.docx`](../../../resources/advanced/conoscenza/Zava_PMO_Linee_Guida_Business_Case.docx) e [`Zava_Piano_Strategico_IT_2026-2028.pdf`](../../../resources/advanced/conoscenza/Zava_Piano_Strategico_IT_2026-2028.pdf).

> [!NOTE]
> **Laboratorio condiviso**
>
> Questo laboratorio è condiviso dai due percorsi. Tempo stimato: 90 minuti.

> [!TIP]
> **Percorso rapido**
>
> Anche per questo corso c'è una soluzione pronta: [`PMODemandIT_1_0_0_0.zip`](../../../resources/advanced/solution/PMODemandIT_1_0_0_0.zip). Contiene le stesse tabelle, colonne e nomi logici in inglese descritti qui, più l'app PMO Demand Hub con home page, import CSV e Proposal Board. Se la si importa (**Solutions**, **Import solution**), saltare le sezioni da *Creare la soluzione* a *Creare l'app PMO Demand Hub*, abilitare a mano **Enable attachments** sulla tabella **Proposal** e riprendere da *Importare programmi e criteri*. Le istruzioni dettagliate sono nel [README della soluzione](../../../resources/advanced/solution/README.md).

> [!NOTE]
> **Perché queste scelte**
>
> - **Dataverse invece di una lista SharePoint o di un Excel.** Il processo ha relazioni (una proposta ha un proponente, un programma, una o più valutazioni), regole sui tipi di dato e codici univoci. Dataverse le gestisce in modo nativo, rispetta la sicurezza per ruolo ed è la fonte che entrambe le harness sanno leggere e scrivere (connettore e prompt nella standard harness, Dataverse MCP Server nella GitHub Copilot harness).
> - **Codici con numerazione automatica.** Persone e agenti si scambiano codici leggibili (PP-1003), non GUID. Il codice lo genera Dataverse, così l'agente non ha mai motivo di inventarlo.
> - **Criteri come righe di una tabella.** Pesi e descrizioni sono dati che il PMO può cambiare senza toccare gli agenti. Il grounding legge sempre la versione aggiornata.
> - **Nomi logici decisi esplicitamente.** Prompt, skill e flow citano i nomi logici delle colonne (`csm_requestedbudget`, `csm_proposalstatus`...). Impostarli in modo esplicito evita sorprese e rende le istruzioni copiabili da questo laboratorio.
> - **Due modi di conservare il documento.** Una colonna **File** per il percorso standard (il flow carica e riscarica il PDF per il prompt) e le **note** abilitate per il percorso GitHub Copilot (il contenuto della nota è leggibile con il Dataverse MCP Server). Nel percorso che non si usa, la colonna o le note rimangono semplicemente vuote.

> [!TIP]
> **Dove lavorare**
>
> Lavorare in [Power Apps](https://make.powerapps.com/) per le tabelle e l'app: il designer delle tabelle offre tutte le opzioni necessarie, inclusa la numerazione automatica. Prima di iniziare controllare in alto a destra che l'ambiente sia quello di laboratorio.

## Soluzione

### Creare la soluzione

Una soluzione è il contenitore che il PMO sposterà da un ambiente all'altro: sviluppo, collaudo, produzione. Se tabelle, app e agenti nascono fuori dalla soluzione, al momento del rilascio vanno cercati e aggiunti uno per uno, con il rischio di dimenticarne qualcuno. Impostarla come soluzione preferita fa sì che tutto ciò che viene creato da qui in poi ci finisca automaticamente.

1. In Power Apps selezionare **Solutions** e poi **New solution**.
2. Compilare i campi:

| Campo | Valore |
| --- | --- |
| Display name | `PMO Demand IT` |
| Name | `PMODemandIT` |
| Publisher | **CSM Solutions** (se manca, selezionare **New publisher** e crearlo con i valori del modulo 1) |

3. Selezionare **Create**.
4. Nell'elenco delle soluzioni selezionare i tre puntini accanto a **PMO Demand IT**, scegliere **Set preferred solution** e confermare. Da ora tabelle, app, agenti e flow finiranno in questa soluzione.

## Tabelle Dataverse

### Tabella Programma

Il programma di investimento è il punto di partenza di ogni valutazione: decide quali criteri si applicano e quale budget è disponibile. Viene creato per primo perché criteri, proposte e valutazioni lo citeranno con un lookup. Il codice PG-### è inserito dal PMO (arriva dal piano degli investimenti), per questo è un testo obbligatorio e non un numero automatico.

1. Aprire la soluzione **PMO Demand IT**, selezionare **New**, **Table** e poi **Table (advanced properties)** (in alcune versioni **Set advanced properties**).
2. Nella scheda **Properties** inserire:
   - **Display name**: `Program`
   - **Plural name**: `Programs`
   - **Description**: `Programmi di investimento IT con budget e criteri di valutazione`
   - espandere **Advanced options** e verificare che **Schema name** sia `csm_Program` (il nome logico diventerà `csm_program`).
3. Nella scheda **Primary column** impostare **Display name** `Name`. Il nome logico diventerà `csm_name`.

> [!IMPORTANT]
> **Colonna primaria**
>
> Il nome della colonna primaria non si può cambiare dopo il salvataggio della tabella. Per questo viene usato un nome semplice (`Name`) per tutte le tabelle anagrafiche.

4. Selezionare **Save** e attendere la creazione.
5. Nella tabella, area **Columns**, aggiungere le colonne con **New column**. Per ognuna espandere **Advanced options** e controllare lo **Schema name** prima di salvare:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Program Code | Text | Required: Business required; Maximum character count: 10 | `csm_programcode` |
| Description | Multiple lines of text (Plain text) | | `csm_description` |
| Available Budget (EUR) | Whole number | Minimum 0 | `csm_availablebudget` |

### Tabella Criterio di valutazione

I criteri sono il cuore della valutazione e cambiano più spesso degli agenti: il PMO può modificare un peso o una descrizione senza toccare istruzioni, prompt o skill. Tenerli come righe collegate al programma permette agli agenti di leggere sempre la versione in vigore.

1. Nella soluzione selezionare **New**, **Table**, **Table (advanced properties)**.
2. Inserire **Display name** `Evaluation Criterion`, **Plural name** `Evaluation Criteria`, **Description** `Criteri pesati di un programma`. In **Advanced options** impostare lo **Schema name** a `csm_Criterion` (il prefisso è già presente: scrivere solo `Criterion`).
3. Nella scheda **Primary column** impostare **Display name** `Name`. Selezionare **Save**.
4. Aggiungere le colonne:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Description | Multiple lines of text | | `csm_description` |
| Weight | Whole number | Minimum 0, Maximum 100 | `csm_weight` |
| Program | Lookup | Related table: **Program** | `csm_program` |

### Tabella Proponente

Lo stesso dipendente può presentare più proposte nel corso dell'anno. Una tabella separata, con l'email come chiave di deduplica, evita di ricopiare nome, ruolo e funzione in ogni proposta e permette di vedere lo storico di chi propone. Il codice RQ-#### lo genera Dataverse, quindi nessun agente avrà motivo di inventarlo.

1. Creare la tabella **Requester** (plurale **Requesters**, schema `csm_Requester`, colonna primaria **Name**).
2. Aggiungere le colonne:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Requester Code | Autonumber | Autonumber type: **String prefixed number**; Prefix `RQ`; Minimum number of digits `4`; Seed value `1000` | `csm_requestercode` |
| Email | Email | | `csm_email` |
| Role | Text | | `csm_role` |
| Department | Text | | `csm_department` |

### Tabella Proposta

La proposta è la tabella su cui lavorano tutti: intake, valutazione, dossier, pianificazione. Contiene i dati estratti dal business case, i dati sul canale di arrivo (chat o email) e lo stato del processo. Due scelte meritano attenzione: lo **Proposal Status** è una colonna propria, distinta dallo stato di sistema, e il documento si conserva in due modi perché le due harness lo leggono in modo diverso.

1. Creare la tabella **Proposal** (plurale **Proposals**, schema `csm_Proposal`).
2. Nella scheda **Properties** selezionare **Enable attachments (including notes and files)**.
3. Nella scheda **Primary column** impostare **Display name** `Title`. Selezionare **Save**.
4. Aggiungere le colonne:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Proposal Code | Autonumber | String prefixed number; Prefix `PP`; Minimum digits `4`; Seed `1000` | `csm_proposalcode` |
| Summary | Multiple lines of text | Maximum character count 4000 | `csm_summary` |
| Cover Message | Multiple lines of text | Maximum character count 4000 | `csm_message` |
| Source Email | Email | | `csm_sourceemail` |
| Requested Budget (EUR) | Whole number | Minimum 0 | `csm_requestedbudget` |
| Duration (Months) | Whole number | Minimum 0 | `csm_durationmonths` |
| Channel | Choice | Nuova scelta locale con opzioni `Chat`, `Email` | `csm_channel` |
| Proposal Status | Choice | Nuova scelta locale con opzioni `Received`, `Assessed`, `Review Scheduled`; Default: `Received` | `csm_proposalstatus` |
| Submission Date | Date only | | `csm_submissiondate` |
| Requester | Lookup | Related table: **Requester** | `csm_requester` |
| Program | Lookup | Related table: **Program** | `csm_program` |
| Business Case Document | File | Maximum file size: lasciare il valore predefinito | `csm_businesscasedocument` |

> [!NOTE]
> **Colonne di tipo Choice**
>
> Per le colonne **Choice**, nel campo **Sync this choice with** scegliere **New choice** (scelta locale) e inserire le opzioni nell'ordine indicato. Con il prefisso del publisher `77000` i valori numerici saranno 770000000, 770000001 e 770000002: gli agenti li usano per scrivere lo stato.

### Tabella Valutazione

La valutazione è separata dalla proposta perché è un atto preciso, con data, programma di riferimento, punteggio e motivazione: se il Comitato chiede una rivalutazione, la storia resta leggibile. Il **Criteria Detail** conserva la tabella riga per riga, così il dossier può riportare i livelli registrati senza rivalutare la proposta.

1. Creare la tabella **Assessment** (plurale **Assessments**, schema `csm_Assessment`, colonna primaria **Title**).
2. Aggiungere le colonne:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Assessment Code | Autonumber | String prefixed number; Prefix `AS`; Minimum digits `4`; Seed `1000` | `csm_assessmentcode` |
| Proposal | Lookup | Related table: **Proposal** | `csm_proposal` |
| Program | Lookup | Related table: **Program** | `csm_program` |
| Score | Decimal number | Decimal places: 1; Minimum 0; Maximum 100 | `csm_score` |
| Criteria Detail | Multiple lines of text | Maximum character count 10000 | `csm_criteriadetail` |
| Rationale | Multiple lines of text | Maximum character count 4000 | `csm_rationale` |
| Recommendation | Choice | Nuova scelta locale: `Recommended`, `Needs Further Review`, `Not Recommended` | `csm_recommendation` |
| Assessment Date | Date only | | `csm_assessmentdate` |

### Verificare nomi logici e valori

Prompt, skill e flow dei laboratori citano nomi logici e valori numerici delle scelte. Se nel proprio ambiente un nome è diverso (ad esempio per un errore di battitura nello schema name), è molto più facile annotarlo ora che scoprirlo quando un agente fallisce una scrittura.

1. Per ogni tabella aprire **Columns** e confrontare il **Logical name** (o **Name**) con i valori attesi:

| Tabella | Nome logico | Colonne principali (nome logico) |
| --- | --- | --- |
| Program | `csm_program` | `csm_name`, `csm_programcode`, `csm_description`, `csm_availablebudget` |
| Evaluation Criterion | `csm_criterion` | `csm_name`, `csm_description`, `csm_weight`, `csm_program` |
| Requester | `csm_requester` | `csm_name`, `csm_requestercode`, `csm_email`, `csm_role`, `csm_department` |
| Proposal | `csm_proposal` | `csm_title`, `csm_proposalcode`, `csm_summary`, `csm_message`, `csm_sourceemail`, `csm_requestedbudget`, `csm_durationmonths`, `csm_channel`, `csm_proposalstatus`, `csm_submissiondate`, `csm_requester`, `csm_program`, `csm_businesscasedocument` |
| Assessment | `csm_assessment` | `csm_title`, `csm_assessmentcode`, `csm_proposal`, `csm_program`, `csm_score`, `csm_criteriadetail`, `csm_rationale`, `csm_recommendation`, `csm_assessmentdate` |

2. Aprire le colonne **Proposal Status**, **Channel** e **Recommendation** e annotare i valori delle opzioni. Valori attesi:

| Colonna | Opzioni e valori |
| --- | --- |
| Channel (`csm_channel`) | Chat (770000000), Email (770000001) |
| Proposal Status (`csm_proposalstatus`) | Received (770000000), Assessed (770000001), Review Scheduled (770000002) |
| Recommendation (`csm_recommendation`) | Recommended (770000000), Needs Further Review (770000001), Not Recommended (770000002) |

3. Se un nome logico o un valore è diverso, **annotarlo**: nei laboratori successivi sostituire il valore del testo da copiare con quello reale. Non ricreare le colonne, a meno di essere ancora all'inizio.

## App PMO Demand Hub

### Moduli e viste

Le tabelle nuove mostrano nel modulo e nella vista solo poche colonne. Occorre aggiungere le altre.

1. Da **Tables** aprire **Proposal** e, nella pagina della tabella, selezionare **Update forms and views**.
2. Selezionare tutte le colonne create per la tabella Proposta, scegliere il modulo principale (**Information**) e la vista **Active Proposals**, poi confermare.
3. Ripetere per **Program**, **Evaluation Criterion**, **Requester** e **Assessment**.
4. Selezionare **Publish all customizations** nella soluzione.

> [!TIP]
> **Colonne di codice automatico**
>
> Le colonne di codice automatico conviene renderle di sola lettura nel modulo: il valore viene assegnato al salvataggio. Se l'opzione **Update forms and views** non è disponibile nella propria versione, aprire il modulo **Information** nel designer e trascinare le colonne nella sezione **General**.

### Creare l'app PMO Demand Hub

Gli agenti scrivono, ma sono le persone del PMO a controllare: per ogni prova dei laboratori si aprirà l'app per verificare i record. Un'app model-driven con le cinque tabelle è anche lo strumento con cui gli analisti correggeranno a mano ciò che un agente non deve modificare.

1. Nella soluzione selezionare **New**, **App**, **Model-driven app**.
2. Inserire **Name** `PMO Demand Hub` e **Description** `App del PMO per proposte, valutazioni e programmi`. Selezionare **Create**.
3. Nel designer selezionare **Add page**, **Dataverse table**, e selezionare **Program**, **Evaluation Criterion**, **Requester**, **Proposal** e **Assessment**. Selezionare **Add**.
4. Selezionare **Save** e poi **Publish**.
5. Selezionare **Play**: l'app si apre con le cinque tabelle nella navigazione. Annotare l'indirizzo dell'app (servirà per i link nelle card di Teams).

### Importare programmi e criteri

**Programs**

1. Nell'app selezionare **Programs**.
2. Nella barra dei comandi aprire i tre puntini (**More**), selezionare la freccia accanto a **Import from Excel** e poi **Import from CSV**.
3. Selezionare **Choose File**, scegliere `programs.csv` e premere **Next**. Lasciare invariate le opzioni del delimitatore e selezionare **Review Mapping**.
4. Controllare che ogni colonna del CSV sia associata alla colonna con lo stesso nome visualizzato (`Name`, `Program Code`, `Description`, `Available Budget (EUR)`), poi selezionare **Finish Import** e **Done**.
5. Selezionare **Refresh** dopo qualche istante: devono comparire i cinque programmi PG-100 ... PG-500.

**Evaluation Criteria**

1. Selezionare **Evaluation Criteria** e ripetere l'importazione con `evaluation-criteria.csv`.
2. In **Review Mapping**, la colonna **Program** è un lookup: invece del segno di spunta mostra una lente. Selezionarla e verificare che il riferimento usi la colonna **Name** della tabella **Program**, poi premere **OK**.
3. Selezionare **Finish Import**, **Done** e **Refresh**: devono comparire 25 criteri, 5 per programma.

> [!NOTE]
> **Mappatura automatica**
>
> Il CSV usa i nomi visualizzati delle colonne come intestazioni: per questo la mappatura si risolve quasi da sola. Il lookup si risolve per nome del programma, che è univoco.

## Impostazioni per il percorso GitHub Copilot

### Abilitare il Dataverse MCP Server

Se si seguirà il percorso GitHub Copilot, verificare che Copilot Studio possa usare il Dataverse MCP Server.

1. Aprire il [Power Platform admin center](https://admin.powerplatform.microsoft.com/), **Manage**, **Environments**, selezionare l'ambiente e poi **Settings**.
2. Espandere **Product** e selezionare **Features**.
3. Nella sezione **Dataverse Model Context Protocol** verificare che **Allow MCP clients to interact with Dataverse MCP server** sia attivo (è attivo per impostazione predefinita per Copilot Studio).

> [!IMPORTANT]
> **Fatturazione**
>
> L'uso del Dataverse MCP Server è soggetto a fatturazione. Usarlo nell'ambiente di laboratorio e con i dati fittizi forniti.

## Conoscenza PMO in SharePoint

### Creare la cartella SharePoint della conoscenza PMO

Le linee guida e il piano strategico sono documenti che il PMO aggiorna. Se vengono caricati direttamente nell'agente, l'agente ne usa una copia statica: quando il PMO cambia una regola, l'agente continua ad applicare quella vecchia finché qualcuno non ricarica il file a mano. Collegando invece una cartella SharePoint, l'agente legge sempre la versione corrente e risponde solo agli utenti che hanno il permesso di leggere quei documenti. Per questo i documenti di conoscenza vivono in SharePoint, come nel lavoro reale del PMO.

1. Aprire il sito SharePoint del laboratorio. Se non se ne ha uno, creare un sito del team chiamato `Zava PMO` (da [SharePoint](https://www.office.com/launch/sharepoint), **Create site**, **Team site**).
2. Aprire la raccolta **Documents** e creare una cartella `PMO Knowledge`.
3. Caricare nella cartella `Zava_PMO_Linee_Guida_Business_Case.docx` e `Zava_Piano_Strategico_IT_2026-2028.pdf`.
4. Aprire la cartella e copiare l'indirizzo dalla barra del browser. Annotarlo: verrà usato nel lab 01 come fonte di conoscenza. Deve avere una forma simile a:

```
https://<tenant>.sharepoint.com/sites/ZavaPMO/Shared%20Documents/PMO%20Knowledge
```

5. Verificare che i partecipanti che proveranno l'agente abbiano almeno il permesso di **lettura** sul sito o sulla cartella. Chi non ce l'ha non riceverà risposte da questi documenti, ed è il comportamento corretto.

> [!NOTE]
> **Un solo sito per la classe**
>
> Se il docente prepara un solo sito per tutta la classe, basta una cartella condivisa in lettura. Gli utenti guest non ricevono risposte da SharePoint, e se il tenant usa **Restricted SharePoint Search** la fonte SharePoint è bloccata: in questi casi usare il caricamento diretto dei file descritto nel lab 01.

## Verificare il setup

1. La soluzione **PMO Demand IT** contiene cinque tabelle e l'app **PMO Demand Hub**.
2. **Programs** contiene 5 righe con codici PG-100 ... PG-500 e budget.
3. **Evaluation Criteria** contiene 25 righe; per ogni programma la somma dei pesi è 100 (verificabile con un filtro sulla colonna **Program**).
4. Creando a mano una proposta di prova nell'app, il **Proposal Code** viene assegnato al salvataggio nel formato `PP-1000`. Eliminare poi la riga di prova.
5. Eventuali differenze di nomi logici o valori delle scelte sono state annotate.
6. La cartella SharePoint `PMO Knowledge` contiene i due documenti e il suo indirizzo è stato annotato.

> [!IMPORTANT]
> **Lab Completato**
>
> Il PMO Demand Hub è pronto: soluzione, cinque tabelle, app model-driven, programmi e criteri importati e cartella della conoscenza PMO in SharePoint. In questo laboratorio si è visto:
>
> - come progettare un modello dati pensato per essere usato da agenti: codici leggibili, nomi logici espliciti, regole nei dati;
> - come creare tabelle, colonne a numerazione automatica, scelte e lookup in una soluzione;
> - come preparare un'app model-driven e importare dati con lookup da CSV.

## Riferimenti Microsoft Learn

- [Create and edit tables using Power Apps](https://learn.microsoft.com/power-apps/maker/data-platform/create-edit-entities-portal)
- [Autonumber columns](https://learn.microsoft.com/power-apps/maker/data-platform/autonumber-fields)
- [Create and edit columns](https://learn.microsoft.com/power-apps/maker/data-platform/create-edit-field-portal)
- [Configure the Dataverse MCP server for an environment](https://learn.microsoft.com/power-apps/maker/data-platform/data-platform-mcp-disable)
- [Manage feature settings](https://learn.microsoft.com/power-platform/admin/settings-features)
- [Add SharePoint as a knowledge source](https://learn.microsoft.com/microsoft-copilot-studio/knowledge-add-sharepoint)
