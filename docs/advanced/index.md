# Advanced: l'Agente Demand IT del PMO di Zava

[Back to Home](../../README.md)

In questo percorso costruisci, con la harness che preferisci, il sistema di agenti che supporta l'**Ufficio Demand e PMO IT** di Zava S.p.A.: riceve i business case delle proposte di progetto IT, li registra, li valuta con i criteri pesati del programma di investimento, prepara il dossier per il Comitato e organizza la sessione di revisione.

Prima di iniziare leggi lo [scenario](./scenario.md) e guarda gli schemi in [Architettura e workflow](./architettura-e-workflow.md).

## Come procedere

1. Completa il laboratorio condiviso [00 - Setup dati](./standard-harness/00-setup-dati/README.md). Crea soluzione, tabelle, app e dati di esempio usati da entrambi i percorsi.
2. Scegli un percorso e svolgi i laboratori nell'ordine: ogni laboratorio estende il lavoro del precedente.
3. Se vuoi confrontare le harness, svolgi anche l'altro percorso nello stesso ambiente. Usa i nomi indicati nei laboratori (gli agenti GitHub Copilot hanno il suffisso ` - GH`) così i componenti non si confondono.

## Pagine di riferimento

| Pagina | Contenuto |
| --- | --- |
| [Scenario](./scenario.md) | L'azienda, il problema e il processo del PMO |
| [Architettura e workflow](./architettura-e-workflow.md) | Schemi dei componenti e dei flussi |

## Percorsi

| Percorso | Laboratori |
| --- | --- |
| [Standard Harness](./standard-harness/index.md) | Setup dati e laboratori S01-S07 (S08 in preparazione) |
| [GitHub Harness](./github-harness/index.md) | In preparazione |

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
