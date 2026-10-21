# Architettura e workflow

[Back to Advanced](./index.md)

Schemi del sistema di agenti del caso pratico: come sono collegati orchestratore, specialista, strumenti e dati nelle due harness, e come scorrono i quattro workflow principali. I diagrammi sono in Mermaid e GitHub li mostra come immagini. Nei codici, `xxxxx` sta per le cifre generate da Dataverse (ad esempio PP-1003).

| Schema | Harness | Laboratori |
| --- | --- | --- |
| [Panoramica del sistema](#panoramica-del-sistema) | Entrambe | Lab 00, S01-S08, G01-G11 |
| [Architettura multi-agente: standard harness](#architettura-multi-agente-standard-harness) | Standard | S01-S06 |
| [Architettura multi-agente: GitHub Copilot harness](#architettura-multi-agente-github-copilot-harness) | GitHub Copilot | G01-G10 |
| [Workflow 1: intake, valutazione e registrazione in chat](#workflow-1-intake-valutazione-e-registrazione-in-chat) | Entrambe | S02-S04, G02, G05 |
| [Workflow 2a: intake via email, standard harness](#workflow-2a-intake-via-email-standard-harness) | Standard | S05 |
| [Workflow 2b: intake via email, GitHub Copilot harness](#workflow-2b-intake-via-email-github-copilot-harness) | GitHub Copilot | G07-G09 |
| [Workflow 3: dossier di revisione](#workflow-3-dossier-di-revisione) | Entrambe | S06, G06 |
| [Workflow 4: preparazione e pianificazione della revisione](#workflow-4-preparazione-e-pianificazione-della-revisione) | Entrambe | G03, G10 |

## Panoramica del sistema

Harness: **Entrambe**. Laboratori: Lab 00, S01-S08, G01-G11.

Due canali di ingresso (chat e casella email del PMO), un orchestratore, uno specialista connesso e un unico archivio dati in Dataverse. Le persone del PMO restano il punto di decisione: confermano programma, valutazione e invito.

```mermaid
flowchart LR
  U["Proponenti e analisti<br/>Teams e Microsoft 365 Copilot"] --> DA
  MAIL["Casella del PMO<br/>oggetto Proposta progetto"] --> AUTO["Automazione email<br/>flow o workflow"]
  AUTO --> DA
  DA["Agente Demand IT<br/>orchestratore"] --> INT["Intake e valutazione<br/>child agent o skill"]
  DA --> DOC["Dossier di revisione<br/>Word"]
  DA -->|delega| AC["Agente Comitato<br/>agente connesso"]
  AC --> CAL["Calendari interni<br/>Outlook o Work IQ"]
  INT --> DV[("PMO Demand Hub<br/>Dataverse")]
  AC --> DV
  AUTO --> DV
  AUTO --> T["Scheda Teams<br/>per il PMO"]
  P["Analista PMO"] -. conferma .-> DA
  P -. revisione umana .-> AUTO
```

## Architettura multi-agente: standard harness

Harness: **Standard**. Laboratori: S01-S06.

L'orchestratore delega l'intake a un child agent che lavora con prompt e agent flow, e la preparazione della revisione a un agente connesso con Dataverse come conoscenza. Il dossier passa da un topic e da un flow; le email arrivano da un trigger dell'agente gestito in Power Automate.

```mermaid
flowchart TB
  subgraph ORCH["Agente Demand IT (csm_agentedemand_std)"]
    direction TB
    K1["Conoscenza<br/>Linee guida PMO, Piano strategico"]
    TOP["Topic Genera dossier di revisione"]
    TRG["Trigger Nuova proposta via email"]
    subgraph CHILD["Child agent Intake Proposte"]
      direction TB
      F1["Flow Carica business case"]
      F2["Flow Analizza business case<br/>prompt Estrai dati business case"]
      F3["Flow Crea valutazione<br/>prompt Valuta proposta<br/>conferma utente"]
      F4["Flow Notifica PMO in Teams"]
    end
  end
  subgraph COM["Agente Comitato (csm_agentecomitato_std)"]
    direction TB
    K2["Conoscenza Dataverse<br/>5 tabelle csm_"]
  end
  ORCH -->|agente connesso| COM
  TOP --> FD["Flow Genera dossier<br/>prompt Dossier di revisione<br/>OneDrive e link"]
  TRG --> PA["Power Automate<br/>Classifica email PMO, ciclo PDF"]
  F1 --> DV[("Dataverse")]
  F2 --> DV
  F3 --> DV
  PA --> DV
  K2 -.-> DV
```

## Architettura multi-agente: GitHub Copilot harness

Harness: **GitHub Copilot**. Laboratori: G01-G10.

Al posto di child agent, topic e flow per ogni operazione: skill caricate su richiesta e il Dataverse MCP Server con strumenti limitati. Lo specialista connesso legge in sola lettura con autenticazione Maker e pianifica con Work IQ. Il workflow email chiama sia un agente inline sia l'orchestratore pubblicato.

```mermaid
flowchart TB
  subgraph ORCH["Agente Demand IT - GH (csm_agentedemand_gh)"]
    direction TB
    K1["Conoscenza<br/>Linee guida PMO, Piano strategico"]
    S1["skill proposal-intake"]
    S2["skill proposal-scoring<br/>sola lettura, rubrica"]
    S3["skill evaluation-recording<br/>dopo conferma"]
    S4["skill review-dossier-document<br/>Python, python-docx"]
    MCP1["Dataverse MCP Server, modalità User<br/>search, describe, read_query,<br/>create_record, update_record"]
  end
  subgraph COM["Agente Comitato - GH (csm_agentecomitato_gh)"]
    direction TB
    MCP2["Dataverse MCP Server, modalità Maker<br/>search, describe, read_query"]
    WIQ["Work IQ (Preview)<br/>persone e calendari interni"]
  end
  subgraph WF["Workflow Intake proposte via email"]
    direction TB
    CL["Classify"] --> AI["Agente inline<br/>Conferma programma"]
    AI --> AP["Nodo Agent<br/>orchestratore pubblicato"]
  end
  ORCH -->|agente connesso| COM
  AP --> ORCH
  MCP1 --> DV[("Dataverse<br/>tabelle e note")]
  MCP2 --> DV
  WF --> DV
```

## Workflow 1: intake, valutazione e registrazione in chat

Harness: **Entrambe**. Laboratori: S02-S04, G02, G05.

Il percorso più frequente. La registrazione della proposta è automatica, la scelta del programma (se ambigua) e la registrazione della valutazione richiedono sempre una persona. Il punteggio segue una rubrica fissa: il modello assegna i livelli, i numeri sono calcolati.

```mermaid
sequenceDiagram
  autonumber
  actor A as Analista o proponente
  participant DA as Agente Demand IT
  participant IN as Intake<br/>child agent o skill
  participant DV as Dataverse
  A->>DA: Allega il business case PDF o DOCX
  DA->>IN: Delega o carica la skill
  IN->>IN: Controlli sul file<br/>formato, dimensione, testo
  IN->>DV: Cerca proponente per email
  IN->>DV: Crea o riusa proponente, crea proposta
  DV-->>IN: Codici SP-xxxx e PP-xxxx
  IN-->>A: Riepilogo e programma da confermare se ambiguo
  A->>DA: Valuta la proposta
  DA->>DV: Legge programma e criteri pesati
  DA-->>A: Tabella criteri, punteggio, indicazione
  A->>DA: Conferma la registrazione
  DA->>DV: Crea valutazione AS-xxxx, stato Assessed
  DA-->>A: Codice valutazione
```

## Workflow 2a: intake via email, standard harness

Harness: **Standard**. Laboratori: S05.

Il trigger dell'agente genera un flusso Power Automate. Qui si classifica l'email con un prompt, si registra ogni PDF e solo allora si chiama l'agente, che analizza la proposta e avvisa il PMO senza creare valutazioni.

```mermaid
flowchart TB
  T["When a new email arrives V3<br/>oggetto Proposta progetto, con allegati"] --> H["Html to text"]
  H --> C["Run a prompt<br/>Classifica email PMO"]
  C --> D{"Proposta rilevata?"}
  D -->|No, RispostaAutomatica o NonPertinente| X["Fine senza azioni"]
  D -->|Incerta| M["Email al PMO<br/>da verificare manualmente"]
  D -->|Si| L["Per ogni allegato PDF"]
  L --> R["Crea proposta in Dataverse<br/>e carica il documento"]
  R --> AG["Sends a prompt to the specified copilot<br/>Agente Demand IT"]
  AG --> AN["Analizza business case"]
  AN --> N["Notifica PMO in Teams"]
```

## Workflow 2b: intake via email, GitHub Copilot harness

Harness: **GitHub Copilot**. Laboratori: G07-G09.

Tutto nel workflow di Copilot Studio. Classify smista, uno Scope raccoglie l'elaborazione, gli agenti leggono i documenti dalle note e una persona interviene in due punti: quando l'email non è classificabile e quando il programma è ambiguo. Un blocco di catch avvisa il PMO se qualcosa fallisce.

```mermaid
flowchart TB
  T["When a new email arrives<br/>Proposta progetto, solo con allegati"] --> V["Avvia elenco proposte<br/>variabile ProposteRegistrate"]
  V --> CL{"Classifica email<br/>Classify"}
  CL -->|RispostaAutomatica| E1["Fine, Succeeded"]
  CL -->|NonPertinente| E2["Fine, Succeeded"]
  CL -->|Other| HR["Human review<br/>Verifica email non chiara"]
  HR --> IF{"Revisore conferma<br/>Yes?"}
  IF -->|No| E3["Fine, Succeeded"]
  IF -->|Yes| SC
  CL -->|Proposta| SC
  subgraph SC["Scope Elabora proposta"]
    direction TB
    LP["Per ogni allegato<br/>Formato ammesso: PDF o DOCX"] --> RP["Registra proposta<br/>Allega documento come nota<br/>Ricorda questa proposta"]
    RP --> AI["Agente inline Conferma programma<br/>Request for information se ambiguo"]
    AI --> AP["Completa con Agente Demand IT<br/>proposal-intake e proposal-scoring"]
    AP --> NT["Notifica PMO in Teams<br/>scheda adattiva"]
  end
  SC -->|Failed o TimedOut| GE["Scope Gestisci errore<br/>Avviso in Teams, End Failed<br/>IntakeProposteFallito"]
```

## Workflow 3: dossier di revisione

Harness: **Entrambe**. Laboratori: S06, G06.

Le due harness producono lo stesso documento in modi diversi. Nella standard harness il layout è un modello Word con segnaposto; nella GitHub Copilot harness è scritto in codice Python, che ricalcola anche i punti e segnala incoerenze.

```mermaid
flowchart LR
  R["Richiesta: dossier per AS-xxxx"] --> S{"Harness"}
  S -->|Standard| T1["Topic Genera dossier di revisione"]
  T1 --> F["Agent flow"]
  F --> P["Prompt Dossier di revisione<br/>output Document, modello Word"]
  P --> O["OneDrive /PMO Dossier<br/>link di condivisione"]
  S -->|GitHub Copilot| K["Skill review-dossier-document"]
  K --> M["Dataverse MCP<br/>legge valutazione e criteri"]
  M --> J["dossier_input.json"]
  J --> PY["generate_dossier.py<br/>validazione e punteggio"]
  PY --> W["dossier_revisione.docx<br/>allegato in chat"]
```

## Workflow 4: preparazione e pianificazione della revisione

Harness: **Entrambe** per la preparazione, **GitHub Copilot** per la pianificazione. Laboratori: S02, G03, G10.

Nel percorso standard l'Agente Comitato prepara briefing e domande (S02) ma non pianifica la sessione: la parte con calendari e inviti è trattata solo in G10.

L'orchestratore delega allo specialista, che prepara briefing e domande sui criteri più pesati e propone fino a tre orari con persone interne. L'invito parte solo dopo la conferma di un orario preciso.

```mermaid
sequenceDiagram
  autonumber
  actor A as Analista PMO
  participant DA as Agente Demand IT
  participant AC as Agente Comitato
  participant DV as Dataverse
  participant CAL as Calendari interni
  A->>DA: Preparami alla revisione di PP-xxxx
  DA->>AC: Delega come agente connesso
  AC->>DV: Legge proposta, criteri, valutazione
  AC-->>A: Briefing e domande per sponsor e architetto
  AC-->>A: Offre di prenotare 30 minuti
  A->>AC: Si, con il collega, la prossima settimana
  AC->>CAL: Risolve la persona e cerca orari liberi
  AC-->>A: Massimo tre opzioni
  A->>AC: Confermo l'orario scelto
  AC->>CAL: Crea l'evento e invia l'invito
  AC-->>A: Evento riletto e confermato
```
