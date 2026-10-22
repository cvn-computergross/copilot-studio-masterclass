# Advanced: l'Agente Demand IT del PMO di Zava

[Back to Home](../../README.md)

In questo percorso costruisci, con la harness che preferisci, il sistema di agenti che supporta l'**Ufficio Demand e PMO IT** di Zava S.p.A.: riceve i business case delle proposte di progetto IT, li registra, li valuta con i criteri pesati del programma di investimento, prepara il dossier per il Comitato e organizza la sessione di revisione.

## Il caso pratico

Zava S.p.A. è una società tecnologica italiana con 420 dipendenti. Ogni anno le sue funzioni aziendali propongono nuovi progetti IT, finanziati attraverso cinque programmi di investimento con budget e criteri di valutazione propri. Il processo è gestito dall'Ufficio Demand e PMO IT ed è quasi tutto manuale: proposte in una casella email condivisa, registrazione in un foglio Excel, valutazioni fatte a mano, dossier per il Comitato preparati da zero.

L'**Agente Demand IT** si occupa della parte ripetitiva e lascia le decisioni alle persone. Riceve i business case in chat e per email, registra proponente e proposta nel **PMO Demand Hub** (Dataverse), propone una valutazione con i criteri pesati del programma mostrando evidenze e calcoli, la registra solo dopo la conferma di una persona del PMO, genera il dossier di revisione in Word e prepara i revisori con briefing e domande mirate. In nessun punto approva o respinge una proposta: la decisione resta al **Comitato di Valutazione Investimenti IT**.

La storia di Zava viene raccontata passo dopo passo nei laboratori: ogni lab si apre con la sezione *Scenario* e mostra gli schemi dei componenti nel punto in cui vengono creati. Si parte dal [Lab 00 - Setup dati](./standard-harness/00-setup-dati/README.md).

## Come procedere

1. Completa il laboratorio condiviso [00 - Setup dati](./standard-harness/00-setup-dati/README.md). Crea soluzione, tabelle, app e dati di esempio usati da entrambi i percorsi.
2. Scegli un percorso e svolgi i laboratori nell'ordine: ogni laboratorio estende il lavoro del precedente.
3. Se vuoi confrontare le harness, svolgi anche l'altro percorso nello stesso ambiente. Usa i nomi indicati nei laboratori (gli agenti GitHub Copilot hanno il suffisso ` - GH`) così i componenti non si confondono.

## Percorsi

| Percorso | Laboratori |
| --- | --- |
| [Standard Harness](./standard-harness/index.md) | Setup dati e laboratori S01-S07 (S08 in preparazione) |
| [GitHub Harness](./github-harness/index.md) | In preparazione |

## I componenti nelle due harness

| Componente | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Orchestratore | Agente Demand IT con child agent Intake Proposte | Agente Demand IT con skill |
| Intake | Agent flow Carica business case + prompt Estrai dati business case | Skill proposal-intake + Dataverse MCP |
| Valutazione | Prompt Valuta proposta (grounding sui criteri) + agent flow Crea valutazione | Skill proposal-scoring + skill evaluation-recording |
| Specialista | Agente Comitato con Dataverse come knowledge | Agente Comitato con Dataverse MCP in sola lettura |
| Email in arrivo | Trigger **When a new email arrives (V3)** modificato in Power Automate | Workflow con Classify, Scope, Loop, agent node e Human review |
| Dossier | Prompt con output Document e template Word | Skill Python `review-dossier-document` |
| Pianificazione | Non inclusa nel percorso standard | Work IQ (Preview) |
| Qualità | Valutazioni, reazioni, CSAT, Application Insights | Evaluate, reazioni, Monitor |

## Corrispondenza con Agent Academy

| Aspetto di Copilot Studio | Operative (Hiring Agent) | Questo caso pratico |
| --- | --- | --- |
| Dati e soluzione | Job Role, Evaluation Criteria, Candidate, Resume, Job Application | Programma, Criterio di valutazione, Proponente, Proposta, Valutazione |
| Multi-agente | Interview Agent connesso | Agente Comitato connesso |
| Automazione su evento | Curriculum via email | Business case via email |
| Documento multimodale | Curriculum PDF | Business case PDF o DOCX |
| Grounding e punteggio | Criteri pesati per ruolo | Criteri pesati per programma con regola di budget |
| Generazione documenti | Interview prep pack | Dossier di revisione |
| MCP e calendario | Riunione di preparazione al colloquio | Sessione di revisione con sponsor e architetto |
| Sicurezza | Policy di selezione del personale | Policy di valutazione degli investimenti, prompt injection nei business case |

## Materiali usati

| Cartella | Contenuto | Usato in |
| --- | --- | --- |
| [`materials/data`](../resources/advanced/data/) | `programs.csv`, `evaluation-criteria.csv` | Setup |
| [`materiali/conoscenza`](../resources/advanced/conoscenza/) | Linee guida del PMO (DOCX), Piano Strategico IT (PDF) | S01, G01 |
| [`materiali/business-case`](../resources/advanced/business-case/) | Sei business case BC-01 ... BC-06 (BC-05 anche in DOCX) | Quasi tutti i laboratori |
| [`materiali/email`](../resources/advanced/email/) | Testi delle email di prova | S05, G07-G09 |
| [`materiali/template`](../resources/advanced/template/) | `Zava_Dossier_Revisione_Template.docx` | S06 |
| [`materiali/skill`](../resources/advanced/skill/) | Skill del percorso GitHub Copilot, incluso `review-dossier-document.zip` | G02, G05, G06 |

## Identificatori

Gli agenti leggono questi codici dai risultati degli strumenti e non devono mai inventarli: Proposta `PP-####`, Valutazione `AS-####`, Proponente `RQ-####`, Programma `PG-###`. I codici esatti nel tuo ambiente saranno diversi da quelli degli esempi: controlla sempre la forma, non il valore.

## Prerequisiti specifici

- Licenze per i connettori Office 365 Outlook, Office 365 Users, Microsoft Teams e OneDrive for Business nel tenant di laboratorio.
- Per G10: un secondo utente del tenant, con casella di posta, da usare come sponsor o architetto nei test di pianificazione. Tutti i partecipanti alle riunioni devono essere **interni** al tenant.
- Per il percorso GitHub Copilot: Microsoft Dataverse MCP Server disponibile nell'ambiente, Work IQ abilitato nel tenant (G10) e capacità di Copilot Credits.
