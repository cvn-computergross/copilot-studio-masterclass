# Lab 00 - Setup dati: il PMO Demand Hub

Previous: Start | [Back to Standard Harness](../index.md) | [Next: S01](../01-agente-orchestratore/README.md)

> [!NOTE]
> Laboratorio condiviso dai due percorsi. Tempo stimato: 90 minuti. Ruolo richiesto nell'ambiente: **System Customizer** o **System Administrator**.

## Contesto

Prima che un agente possa registrare e valutare proposte, il PMO ha bisogno di un posto dove i dati vivono in modo strutturato: il **PMO Demand Hub**. In questo laboratorio crei in Dataverse le cinque tabelle del processo (Programmi, Criteri di valutazione, Proponenti, Proposte, Valutazioni), un'app model-driven per consultarle e i dati di partenza: cinque programmi di investimento con i loro criteri pesati.

Agent Academy fornisce per l'Hiring Agent una soluzione già pronta da importare. Qui costruisci il modello a mano: richiede più tempo, ma ti fa capire ogni scelta che gli agenti useranno dopo (nomi logici, codici automatici, scelte, relazioni).

> [!TIP]
> **Percorso rapido.** Anche per questo corso c'è una soluzione pronta: [`PMODemandIT_1_0_0_0.zip`](../../../resources/advanced/solution/PMODemandIT_1_0_0_0.zip). Contiene le stesse tabelle, colonne e nomi logici in inglese descritti qui, più l'app PMO Demand Hub con home page, import CSV e Proposal Board. Se la importi (**Solutions**, **Import solution**), salta i passi da 1 a 9, abilita a mano **Enable attachments** sulla tabella **Proposal** e riprendi dal passo 10. Le istruzioni dettagliate sono nel [README della soluzione](../../../resources/advanced/solution/README.md).

## Perché queste scelte

- **Dataverse invece di una lista SharePoint o di un Excel.** Il processo ha relazioni (una proposta ha un proponente, un programma, una o più valutazioni), regole sui tipi di dato e codici univoci. Dataverse le gestisce in modo nativo, rispetta la sicurezza per ruolo ed è la fonte che entrambe le harness sanno leggere e scrivere (connettore e prompt nella standard harness, Dataverse MCP Server nella GitHub Copilot harness).
- **Codici con numerazione automatica.** Persone e agenti si scambiano codici leggibili (PP-1003), non GUID. Il codice lo genera Dataverse, così l'agente non ha mai motivo di inventarlo.
- **Criteri come righe di una tabella.** Pesi e descrizioni sono dati che il PMO può cambiare senza toccare gli agenti. Il grounding legge sempre la versione aggiornata.
- **Nomi logici decisi da te.** Prompt, skill e flow citano i nomi logici delle colonne (`csm_requestedbudget`, `csm_proposalstatus`...). Impostarli in modo esplicito evita sorprese e rende le istruzioni copiabili da questo laboratorio.
- **Due modi di conservare il documento.** Una colonna **File** per il percorso standard (il flow carica e riscarica il PDF per il prompt) e le **note** abilitate per il percorso GitHub Copilot (il contenuto della nota è leggibile con il Dataverse MCP Server). I dettagli sono in [docs/03-modello-dati.md](../../modello-dati.md).

## Obiettivi

1. Creare la soluzione **PMO Demand IT** come soluzione preferita.
2. Creare cinque tabelle con colonne, codici automatici, scelte e relazioni.
3. Preparare moduli e viste e creare l'app **PMO Demand Hub**.
4. Importare programmi e criteri da CSV.
5. Verificare nomi logici, valori delle scelte e impostazioni per il Dataverse MCP Server.
6. Preparare in SharePoint la cartella con i documenti di conoscenza del PMO.

## Prerequisiti

- Ambiente di laboratorio con Dataverse (lo stesso dei fondamenti va bene).
- Publisher **CSM Solutions** con prefisso `csm` e prefisso delle scelte `77000` (creato nel modulo 1 dei fondamenti; se non esiste, crealo al passo 1).
- File [`programs.csv`](../../../resources/advanced/data/programs.csv) e [`evaluation-criteria.csv`](../../../resources/advanced/data/evaluation-criteria.csv).
- Un sito SharePoint dove puoi creare cartelle e caricare file (per il passo 12), e i file [`Zava_PMO_Linee_Guida_Business_Case.docx`](../../../resources/advanced/conoscenza/Zava_PMO_Linee_Guida_Business_Case.docx) e [`Zava_Piano_Strategico_IT_2026-2028.pdf`](../../../resources/advanced/conoscenza/Zava_Piano_Strategico_IT_2026-2028.pdf).

> [!TIP]
> Lavora in [Power Apps](https://make.powerapps.com/) per le tabelle e l'app: il designer delle tabelle offre tutte le opzioni necessarie, inclusa la numerazione automatica. Prima di iniziare controlla in alto a destra che l'ambiente sia quello di laboratorio.

## Passo 1 - Creare la soluzione

Una soluzione è il contenitore che il PMO sposterà da un ambiente all'altro: sviluppo, collaudo, produzione. Se tabelle, app e agenti nascono fuori dalla soluzione, al momento del rilascio vanno cercati e aggiunti uno per uno, con il rischio di dimenticarne qualcuno. Impostarla come soluzione preferita fa sì che tutto ciò che crei da qui in poi ci finisca automaticamente.

1. In Power Apps seleziona **Solutions** e poi **New solution**.
2. Compila:

| Campo | Valore |
| --- | --- |
| Display name | `PMO Demand IT` |
| Name | `PMODemandIT` |
| Publisher | **CSM Solutions** (se manca, seleziona **New publisher** e crealo con i valori del modulo 1) |

3. Seleziona **Create**.
4. Nell'elenco delle soluzioni seleziona i tre puntini accanto a **PMO Demand IT** e scegli **Set preferred solution**, poi conferma. Da ora tabelle, app, agenti e flow finiranno in questa soluzione.

## Passo 2 - Tabella Programma

Il programma di investimento è il punto di partenza di ogni valutazione: decide quali criteri si applicano e quale budget è disponibile. Lo crei per primo perché criteri, proposte e valutazioni lo citeranno con un lookup. Il codice PG-### è inserito dal PMO (arriva dal piano degli investimenti), per questo è un testo obbligatorio e non un numero automatico.

1. Apri la soluzione **PMO Demand IT**, seleziona **New**, **Table** e poi **Table (advanced properties)** (in alcune versioni **Set advanced properties**).
2. Scheda **Properties**:
   - **Display name**: `Program`
   - **Plural name**: `Programs`
   - **Description**: `Programmi di investimento IT con budget e criteri di valutazione`
   - espandi **Advanced options** e verifica che **Schema name** sia `csm_Program` (il nome logico diventerà `csm_program`).
3. Scheda **Primary column**: **Display name** `Name`. Il nome logico diventerà `csm_name`.

   > [!IMPORTANT]
   > Il nome della colonna primaria non si può cambiare dopo il salvataggio della tabella. Per questo usiamo un nome semplice (`Name`) per tutte le tabelle anagrafiche.

4. Seleziona **Save** e attendi la creazione.
5. Nella tabella, area **Columns**, aggiungi le colonne con **New column**. Per ognuna espandi **Advanced options** e controlla lo **Schema name** prima di salvare:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Program Code | Text | Required: Business required; Maximum character count: 10 | `csm_programcode` |
| Description | Multiple lines of text (Plain text) | | `csm_description` |
| Available Budget (EUR) | Whole number | Minimum 0 | `csm_availablebudget` |

## Passo 3 - Tabella Criterio di valutazione

I criteri sono il cuore della valutazione e cambiano più spesso degli agenti: il PMO può modificare un peso o una descrizione senza toccare istruzioni, prompt o skill. Tenerli come righe collegate al programma permette agli agenti di leggere sempre la versione in vigore.

1. Nella soluzione: **New**, **Table**, **Table (advanced properties)**.
2. **Display name** `Evaluation Criterion`, **Plural name** `Evaluation Criteria`, **Description** `Criteri pesati di un programma`. In **Advanced options** imposta lo **Schema name** a `csm_Criterion` (il prefisso è già presente: scrivi solo `Criterion`).
3. **Primary column**: **Display name** `Name`. Seleziona **Save**.
4. Aggiungi le colonne:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Description | Multiple lines of text | | `csm_description` |
| Weight | Whole number | Minimum 0, Maximum 100 | `csm_weight` |
| Program | Lookup | Related table: **Program** | `csm_program` |

## Passo 4 - Tabella Proponente

Lo stesso dipendente può presentare più proposte nel corso dell'anno. Una tabella separata, con l'email come chiave di deduplica, evita di ricopiare nome, ruolo e funzione in ogni proposta e permette di vedere lo storico di chi propone. Il codice RQ-#### lo genera Dataverse, quindi nessun agente avrà motivo di inventarlo.

1. Crea la tabella **Requester** (plurale **Requesters**, schema `csm_Requester`, colonna primaria **Name**).
2. Aggiungi le colonne:

| Display name | Data type | Altre impostazioni | Schema name |
| --- | --- | --- | --- |
| Requester Code | Autonumber | Autonumber type: **String prefixed number**; Prefix `RQ`; Minimum number of digits `4`; Seed value `1000` | `csm_requestercode` |
| Email | Email | | `csm_email` |
| Role | Text | | `csm_role` |
| Department | Text | | `csm_department` |

## Passo 5 - Tabella Proposta

La proposta è la tabella su cui lavorano tutti: intake, valutazione, dossier, pianificazione. Contiene i dati estratti dal business case, i dati sul canale di arrivo (chat o email) e lo stato del processo. Due scelte meritano attenzione: lo **Proposal Status** è una colonna propria, distinta dallo stato di sistema, e il documento si conserva in due modi perché le due harness lo leggono in modo diverso.

1. Crea la tabella **Proposal** (plurale **Proposals**, schema `csm_Proposal`). Nella scheda **Properties** seleziona **Enable attachments (including notes and files)**. Nella scheda **Primary column** imposta **Display name** `Title`. Seleziona **Save**.
2. Aggiungi le colonne:

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
| Business Case Document | File | Maximum file size: lascia il valore predefinito | `csm_businesscasedocument` |

> [!NOTE]
> Per le colonne **Choice**, nel campo **Sync this choice with** scegli **New choice** (scelta locale) e inserisci le opzioni nell'ordine indicato. Con il prefisso del publisher `77000` i valori numerici saranno 770000000, 770000001 e 770000002: gli agenti li usano per scrivere lo stato.

## Passo 6 - Tabella Valutazione

La valutazione è separata dalla proposta perché è un atto preciso, con data, programma di riferimento, punteggio e motivazione: se il Comitato chiede una rivalutazione, la storia resta leggibile. Il **Criteria Detail** conserva la tabella riga per riga, così il dossier può riportare i livelli registrati senza rivalutare la proposta.

1. Crea la tabella **Assessment** (plurale **Assessments**, schema `csm_Assessment`, colonna primaria **Title**).
2. Aggiungi le colonne:

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

## Passo 7 - Verificare nomi logici e valori

Prompt, skill e flow dei laboratori citano nomi logici e valori numerici delle scelte. Se nel tuo ambiente un nome è diverso (ad esempio per un errore di battitura nello schema name), è molto più facile annotarlo ora che scoprirlo quando un agente fallisce una scrittura.

1. Per ogni tabella apri **Columns** e confronta il **Logical name** (o **Name**) con [docs/03-modello-dati.md](../../modello-dati.md).
2. Apri le colonne **Proposal Status**, **Channel** e **Recommendation** e annota i valori delle opzioni (attesi: 770000000, 770000001, 770000002).
3. Se un nome logico o un valore è diverso, **annotalo**: nei laboratori successivi sostituisci il valore del testo da copiare con quello reale. Non ricreare le colonne, a meno che tu non sia ancora all'inizio.

## Passo 8 - Moduli e viste

Le tabelle nuove mostrano nel modulo e nella vista solo poche colonne. Aggiungi le altre:

1. Da **Tables** apri **Proposal** e, nella pagina della tabella, seleziona **Update forms and views**.
2. Seleziona tutte le colonne create al passo 5, scegli il modulo principale (**Information**) e la vista **Active Proposals**, poi conferma.
3. Ripeti per **Program**, **Evaluation Criterion**, **Requester** e **Assessment**.
4. Seleziona **Publish all customizations** nella soluzione.

> [!TIP]
> Le colonne di codice automatico conviene renderle di sola lettura nel modulo: il valore viene assegnato al salvataggio. Se l'opzione **Update forms and views** non è disponibile nella tua versione, apri il modulo **Information** nel designer e trascina le colonne nella sezione **General**.

## Passo 9 - Creare l'app PMO Demand Hub

Gli agenti scrivono, ma sono le persone del PMO a controllare: per ogni prova dei laboratori aprirai l'app e verificherai i record. Un'app model-driven con le cinque tabelle è anche lo strumento con cui gli analisti correggeranno a mano ciò che un agente non deve modificare.

1. Nella soluzione seleziona **New**, **App**, **Model-driven app**.
2. **Name**: `PMO Demand Hub`; **Description**: `App del PMO per proposte, valutazioni e programmi`. Seleziona **Create**.
3. Nel designer seleziona **Add page**, **Dataverse table**, e seleziona **Program**, **Evaluation Criterion**, **Requester**, **Proposal** e **Assessment**. Seleziona **Add**.
4. Seleziona **Save** e poi **Publish**.
5. Seleziona **Play**: l'app si apre con le cinque tabelle nella navigazione. Annota l'indirizzo dell'app (servirà per i link nelle card di Teams).

## Passo 10 - Importare programmi e criteri

**Programs**

1. Nell'app seleziona **Programs**.
2. Nella barra dei comandi apri i tre puntini (**More**), seleziona la freccia accanto a **Import from Excel** e poi **Import from CSV**.
3. **Choose File**, seleziona `programs.csv`, **Next**. Lascia invariate le opzioni del delimitatore e seleziona **Review Mapping**.
4. Controlla che ogni colonna del CSV sia associata alla colonna con lo stesso nome visualizzato (`Name`, `Program Code`, `Description`, `Available Budget (EUR)`), poi **Finish Import** e **Done**.
5. Seleziona **Refresh** dopo qualche istante: devi vedere i cinque programmi PG-100 ... PG-500.

**Evaluation Criteria**

1. Seleziona **Evaluation Criteria** e ripeti l'importazione con `evaluation-criteria.csv`.
2. In **Review Mapping**, la colonna **Program** è un lookup: invece del segno di spunta mostra una lente. Selezionala e verifica che il riferimento usi la colonna **Name** della tabella **Program**, poi **OK**.
3. **Finish Import**, **Done** e **Refresh**: devi vedere 25 criteri, 5 per programma.

> [!NOTE]
> Il CSV usa i nomi visualizzati delle colonne come intestazioni: per questo la mappatura si risolve quasi da sola. Il lookup si risolve per nome del programma, che è univoco.

## Passo 11 - Impostazioni per il percorso GitHub Copilot

Se seguirai il percorso GitHub Copilot, verifica che Copilot Studio possa usare il Dataverse MCP Server:

1. Apri il [Power Platform admin center](https://admin.powerplatform.microsoft.com/), **Manage**, **Environments**, seleziona l'ambiente e poi **Settings**.
2. Espandi **Product** e seleziona **Features**.
3. Nella sezione **Dataverse Model Context Protocol** verifica che **Allow MCP clients to interact with Dataverse MCP server** sia attivo (è attivo per impostazione predefinita per Copilot Studio).

> [!IMPORTANT]
> L'uso del Dataverse MCP Server è soggetto a fatturazione. Usalo nell'ambiente di laboratorio e con i dati fittizi forniti.

## Passo 12 - Cartella SharePoint della conoscenza PMO

Le linee guida e il piano strategico sono documenti che il PMO aggiorna. Se li carichi direttamente nell'agente, l'agente ne usa una copia statica: quando il PMO cambia una regola, l'agente continua ad applicare quella vecchia finché qualcuno non ricarica il file a mano. Collegando invece una cartella SharePoint, l'agente legge sempre la versione corrente e risponde solo agli utenti che hanno il permesso di leggere quei documenti. Per questo i documenti di conoscenza vivono in SharePoint, come nel lavoro reale del PMO.

1. Apri il sito SharePoint del laboratorio. Se non ne hai uno, crea un sito del team chiamato `Zava PMO` (da [SharePoint](https://www.office.com/launch/sharepoint), **Create site**, **Team site**).
2. Apri la raccolta **Documents** e crea una cartella `PMO Knowledge`.
3. Carica nella cartella `Zava_PMO_Linee_Guida_Business_Case.docx` e `Zava_Piano_Strategico_IT_2026-2028.pdf`.
4. Apri la cartella e copia l'indirizzo dalla barra del browser. Annotalo: lo userai nel lab 01 come fonte di conoscenza. Deve avere una forma simile a `https://<tenant>.sharepoint.com/sites/ZavaPMO/Shared%20Documents/PMO%20Knowledge`.
5. Verifica che i partecipanti che proveranno l'agente abbiano almeno il permesso di **lettura** sul sito o sulla cartella. Chi non ce l'ha non riceverà risposte da questi documenti, ed è il comportamento corretto.

> [!NOTE]
> Se il docente prepara un solo sito per tutta la classe, basta una cartella condivisa in lettura. Gli utenti guest non ricevono risposte da SharePoint, e se il tenant usa **Restricted SharePoint Search** la fonte SharePoint è bloccata: in questi casi usa il caricamento diretto dei file descritto nel lab 01.

## Verifica

1. La soluzione **PMO Demand IT** contiene cinque tabelle e l'app **PMO Demand Hub**.
2. **Programs** contiene 5 righe con codici PG-100 ... PG-500 e budget.
3. **Evaluation Criteria** contiene 25 righe; per ogni programma la somma dei pesi è 100 (puoi verificarlo con un filtro sulla colonna **Program**).
4. Creando a mano una proposta di prova nell'app, il **Proposal Code** viene assegnato al salvataggio nel formato `PP-1000`. Elimina poi la riga di prova.
5. Hai annotato eventuali differenze di nomi logici o valori delle scelte.
6. La cartella SharePoint `PMO Knowledge` contiene i due documenti e hai annotato il suo indirizzo.

## Cosa hai imparato

- Come progettare un modello dati pensato per essere usato da agenti: codici leggibili, nomi logici espliciti, regole nei dati.
- Come creare tabelle, colonne a numerazione automatica, scelte e lookup in una soluzione.
- Come preparare un'app model-driven e importare dati con lookup da CSV.

## Riferimenti Microsoft Learn

- [Create and edit tables using Power Apps](https://learn.microsoft.com/power-apps/maker/data-platform/create-edit-entities-portal)
- [Autonumber columns](https://learn.microsoft.com/power-apps/maker/data-platform/autonumber-fields)
- [Create and edit columns](https://learn.microsoft.com/power-apps/maker/data-platform/create-edit-field-portal)
- [Configure the Dataverse MCP server for an environment](https://learn.microsoft.com/power-apps/maker/data-platform/data-platform-mcp-disable)
- [Manage feature settings](https://learn.microsoft.com/power-platform/admin/settings-features)
- [Add SharePoint as a knowledge source](https://learn.microsoft.com/microsoft-copilot-studio/knowledge-add-sharepoint)
