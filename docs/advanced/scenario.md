# Lo scenario: il PMO di Zava S.p.A.

[Back to Advanced](./index.md)

## L'azienda e il problema

Zava S.p.A. è una società tecnologica italiana con 420 dipendenti, sede a Milano e uffici a Torino, Bologna e Roma. Ogni anno le funzioni aziendali (Acquisti, Vendite, Risorse Umane, Servizio Clienti, IT Operations, Sicurezza) propongono nuovi progetti IT. Le proposte vengono finanziate attraverso cinque **programmi di investimento**, ciascuno con un budget e con criteri di valutazione propri.

Il processo è gestito dall'**Ufficio Demand e PMO IT**. Oggi funziona così:

1. le proposte arrivano in una casella email condivisa, in formati diversi, spesso senza tutte le informazioni richieste;
2. un analista apre ogni documento, lo registra in un foglio Excel e lo assegna a un programma;
3. la valutazione con i criteri pesati viene fatta a mano, con interpretazioni diverse da analista ad analista;
4. per ogni proposta valutata si prepara un dossier per il Comitato (circa due ore di lavoro);
5. la sessione di revisione con lo sponsor e l'architetto di riferimento si organizza con molti scambi di email.

I problemi sono noti: tempi di presa in carico lunghi, valutazioni poco confrontabili, dossier con strutture diverse, poco tempo per l'analisi vera e propria.

## L'obiettivo

Costruire un sistema di agenti che si occupi della parte ripetitiva e lasci alle persone le decisioni:

- ricevere i business case in chat (Teams, Microsoft 365 Copilot) e per email;
- registrare proponente e proposta nel **PMO Demand Hub** (Dataverse);
- proporre una valutazione con i criteri pesati del programma, mostrando evidenze e calcoli;
- registrare la valutazione solo dopo la conferma di una persona del PMO;
- generare il **dossier di revisione** in Word con una struttura sempre uguale;
- preparare i revisori con briefing e domande mirate;
- trovare uno slot libero per la sessione di revisione tra persone interne e creare l'invito dopo conferma;
- notificare il PMO in Teams quando arriva una proposta per email.

> [!IMPORTANT]
> In nessun punto l'agente approva o respinge una proposta. La decisione resta al **Comitato di Valutazione Investimenti IT**. È una scelta di progetto (responsabilità e trasparenza), ripresa nelle istruzioni, nei documenti generati e nelle valutazioni di sicurezza.

## Attori

| Attore | Ruolo nel processo | Interagisce con |
| --- | --- | --- |
| Proponente | Responsabile di funzione che presenta il business case | Agente Demand IT (chat) oppure email |
| Analista PMO | Verifica, conferma il programma, conferma la registrazione della valutazione | Agente Demand IT, PMO Demand Hub, Teams |
| Sponsor interno | Dirigente che risponde della proposta | Sessione di revisione |
| Architetto di riferimento | Valuta gli aspetti tecnici per il programma | Agente Comitato, sessione di revisione |
| Comitato | Decide | Dossier di revisione |

Tutte le persone sono interne a Zava S.p.A. Non è un dettaglio: Work IQ e i connettori di calendario leggono disponibilità e profili solo all'interno del proprio tenant, per cui lo scenario non prevede di pianificare riunioni con persone esterne.

## Perché i documenti sono solo PDF testuali e DOCX

Copilot Studio legge in modo affidabile il **testo** dei documenti. Il prompt tool della standard harness accetta come documento solo PDF e immagini, e nei laboratori evitiamo volutamente le immagini e le scansioni: il contenuto di un business case deve essere testo selezionabile. Le linee guida del PMO (materiale di conoscenza del caso pratico) lo rendono una regola del processo, così l'agente può rifiutare in modo motivato i file non conformi.

## I componenti del sistema

![Panoramica del sistema: canali di ingresso, Agente Demand IT, Intake Proposte, Agente Comitato, dossier e PMO Demand Hub](./images/panoramica-sistema.svg)

Gli schemi di dettaglio sono in [Architettura e workflow](./architettura-e-workflow.md).

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

## I business case di prova

I documenti sono in `materiali/business-case`. Sono costruiti per esercitare situazioni diverse.

| File | Proposta | Programma | Che cosa mette alla prova |
| --- | --- | --- | --- |
| BC-01 (PDF) | Portale fornitori self-service | PG-100 | Caso felice: evidenze forti e quantificate |
| BC-02 (PDF) | Segmentazione di rete e accessi privilegiati | PG-200 | Proposta solida con costi ricorrenti dichiarati |
| BC-03 (PDF) | Assistente AI per il servizio clienti | Ambiguo tra PG-100 e PG-300 | Programma da confermare, evidenze deboli su dati e privacy |
| BC-04 (PDF) | Migrazione del data center di Bologna in cloud | PG-500 | Budget richiesto superiore al budget del programma |
| BC-05 (DOCX e PDF) | Nuova intranet e hub dei dipendenti | PG-400 | Formato Word; nella standard harness serve il PDF per la valutazione |
| BC-06 (PDF) | Dashboard vendite in tempo reale | PG-300 | Testo di prompt injection dentro il documento |

## Principi di progettazione

1. **La persona decide.** L'agente propone, mostra le evidenze e chiede conferma prima di ogni scrittura che ha conseguenze.
2. **Il calcolo non lo fa il modello.** Pesi e regole stanno in Dataverse; somma, soglie e layout dei documenti sono affidati a espressioni o codice.
3. **Minimo privilegio.** Ogni agente riceve solo gli strumenti che gli servono: lo specialista legge, non scrive.
4. **I documenti sono dati, non istruzioni.** Qualsiasi testo dentro un business case che provi a cambiare le regole viene ignorato e segnalato.
5. **Solo persone interne.** Nessun contatto automatico con soggetti esterni.
6. **Tutto è verificabile.** Ogni record riporta un codice leggibile (PP-####, AS-####, RQ-####, PG-###) che l'agente legge dai risultati degli strumenti e non inventa mai.

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

Gli schemi completi dell'architettura multi-agente nelle due harness e dei workflow principali sono in [05-architettura-e-workflow.md](./architettura-e-workflow.md).
