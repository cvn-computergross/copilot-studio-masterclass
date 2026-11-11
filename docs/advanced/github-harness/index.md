# Advanced · GitHub Harness

[← Home del corso](../../../README.md)

Il caso pratico costruito con la **GitHub Copilot harness**: l'Agente Demand IT, con istruzioni, skill, Dataverse MCP Server e workflow, riceve, valuta e prepara per il Comitato le proposte di progetto IT di Zava. La storia del caso e gli schemi dei componenti si trovano nei laboratori, a partire dal [Lab 00](./00-setup-dati/README.md).

## Lab <!-- icon: flask f-instructions -->

| Lab | Titolo | Che cosa impari | Tempo |
| --- | --- | --- | --- |
| [00](./00-setup-dati/README.md) | Setup dati | Import della soluzione pronta, modello dati Dataverse, app PMO Demand Hub e dati di partenza | 45 min |
| [G01](./01-agente-orchestratore/README.md) | Agente orchestratore | Identità bloccata al primo salvataggio, istruzioni come contratto | 30 min |
| [G02](./02-istruzioni-skill-e-dataverse-mcp/README.md) | Istruzioni, skill e Dataverse MCP | Skill da zero, server MCP con privilegi minimi, Preview, valutazione di base | 75 min |
| [G03](./03-agente-connesso/README.md) | Agente connesso | Specialista in sola lettura, autenticazione Maker, delega | 60 min |
| [G04](./04-modello-risposta-e-sicurezza/README.md) | Modello, risposta e sicurezza | Disclosure, guardrail, valutazione di sicurezza da CSV, injection | 35 min |
| [G05](./05-intake-valutazione-registrazione/README.md) | Intake, valutazione e registrazione | Lettura nativa di PDF e DOCX, rubrica, scritture dopo conferma | 90 min |
| [G06](./06-dossier-skill-python/README.md) | Dossier di revisione con una skill Python | Skill importata da zip, script `python-docx`, layout definito nel codice, validazione | 45 min |
| [G07](./07-workflow-trigger-email/README.md) | Workflow di intake con trigger email | Trigger agente provato e rimosso, workflow con Classify, Scope, loop sugli allegati, registrazione in Dataverse | 105 min |
| [G08](./08-agenti-nel-workflow/README.md) | Agenti nel workflow | Agente inline e agente pubblicato come nodi, scheda adattiva nel canale Proposte | 90 min |
| [G09](./09-supervisione-umana/README.md) | Supervisione umana ed errori | Human review, rami chiusi con End, try/catch con avviso in Teams, errore provocato | 75 min |
| [G10](./10-pianificazione-revisione/README.md) | Fissare la revisione: via libera e agente di pianificazione | Workflow come strumento con soglia e Approvals, agente connesso con Office 365 Users e Outlook, conferma prima dell'invito | 90 min |
| [G11](./11-evaluate-pubblicazione-monitor/README.md) | Rilascio: memoria, Teams e monitoraggio | Memory, pubblicazione in Teams, condivisione, Monitor e reazioni | 40 min |

## Prerequisiti specifici

Oltre ai prerequisiti del [Lab 00](./00-setup-dati/README.md), questo percorso richiede:

- licenze per i connettori Office 365 Outlook, Office 365 Users, Microsoft Teams e OneDrive for Business nel tenant di laboratorio;
- per il Lab G10, un secondo utente del tenant, con casella di posta, da usare come sponsor o architetto nei test di pianificazione: tutti i partecipanti alle riunioni devono essere **interni** al tenant;
- Microsoft Dataverse MCP Server disponibile nell'ambiente, licenza Microsoft 365 con Exchange Online per i calendari (Lab G10) e capacità di Copilot Credits.
