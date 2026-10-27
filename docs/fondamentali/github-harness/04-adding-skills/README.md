# Lab 04 - Adding Skills

[Previous: Lab 03](../03-adding-tools/README.md) | [Back to GitHub Harness](../index.md) | [Next: Lab 05](../05-automating-with-workflows/README.md)

<!-- icon: clock-countdown --> **Tempo stimato:** ~75 minuti · <!-- icon: github-logo f-github --> **Harness:** GitHub Copilot

## Scenario

Il responsabile dell'Help Desk di Zava vuole tre comportamenti ripetibili:

- per i problemi tecnici, proporre **sempre la stessa checklist approvata** di primo livello (hardware, software o rete) e, se il problema resta, preparare il riepilogo per l'escalation;
- per aprire un ticket, raccogliere **sempre gli stessi cinque campi**, validati, e mostrarne il riepilogo da confermare;
- per le guide passo passo da inviare al dipendente, seguire il template del Service Desk con i **testi fissi copiati parola per parola**.

Nella standard harness i primi due sono i topic del [Lab 03](../../standard-harness/03-ticket-agent-topics/README.md), con una domanda a scelta multipla, condizioni e una adaptive card; il terzo sarebbe un prompt, come quello del [Lab 04](../../standard-harness/04-job-posting-tools/README.md). Si potrebbe scrivere tutto nelle istruzioni dell'agente, come nel Lab 03 con la guida, ma le istruzioni vengono lette a ogni turno: crescerebbero fino a diventare difficili da mantenere e costose da elaborare.

Nella GitHub Copilot harness le procedure ripetibili si scrivono come **skill**: pacchetti con nome, descrizione e istruzioni che l'agente carica solo quando la richiesta corrisponde alla descrizione. In particolare verranno svolte le seguenti attività:

- Indicare le procedure nelle istruzioni dell'agente, al posto della sezione **# Guide passo passo**.
- Caricare la skill **supporto-tecnico** da un file Markdown.
- Scrivere da zero la skill **apertura-ticket**.
- Caricare la skill **guida-passo-passo** da un pacchetto zip con file di riferimento.
- Provare in **Preview** quale skill viene caricata e quando vengono letti i riferimenti.

::: details <!-- icon: lightbulb f-instructions --> Perché questa scelta
- **Istruzioni per ciò che vale sempre, skill per ciò che serve a volte.** Ruolo, perimetro e regole di sicurezza restano nelle istruzioni. Il modo di svolgere un compito specifico va in una skill, che entra nel contesto solo quando serve: nel Lab 03 la procedura della guida veniva letta anche a ogni semplice domanda sui prerequisiti della VPN.
- **La descrizione decide quando la skill viene caricata.** L'orchestratore confronta la richiesta con le descrizioni. Descrizioni specifiche e distinte tra loro, con le esclusioni dichiarate ("non usarla per..."), evitano che parta la skill sbagliata. Qui conta più del solito: supporto-tecnico e guida-passo-passo parlano entrambe di VPN, Outlook e stampanti, e si distinguono solo per lo scopo (diagnosticare un guasto oppure spiegare come si fa una cosa).
- **Una skill, un lavoro.** Tre procedure diventano tre skill: ognuna si prova, si versiona e si riusa da sola, anche in altri agenti. Due di esse collaborano: supporto-tecnico prepara il riepilogo per l'escalation e apertura-ticket lo riusa invece di chiedere di nuovo gli stessi dati.
- **Testi fissi nei riferimenti.** Il template e i testi del Service Desk stanno nella cartella `riferimenti` della skill guida-passo-passo: l'Help Desk può aggiornare contatti, orari e avviso di sicurezza senza toccare la procedura, e il segnaposto del Lab 03 lascia il posto al testo ufficiale.
- **Le regole che valgono sempre restano nelle istruzioni.** Anteprima e conferma prima di ogni invio, invio solo all'utente stesso, lettura del profilo con **Get my profile (V2)** e divieto di inserire credenziali sono nella sezione **# Strumenti ed email** del Lab 03: valgono anche quando l'invio parte da una skill, che quindi non le ripete.
- **Skill invece di topic.** Un topic descrive _come_ scorre la conversazione nodo per nodo; una skill descrive _che cosa_ fare, in che ordine, con quali regole e quando la procedura è finita. È più flessibile (l'utente dà le informazioni in qualsiasi ordine) e più facile da mantenere, ma meno deterministica: quando serve un percorso sempre identico si usa un workflow (Lab 05).
- **Tre modi di creare una skill.** **Upload a skill** (file SKILL.md o pacchetto .zip), **Generate with AI** (bozza a partire da una descrizione) e **Create from blank** (scritta a mano). Qui si usano il primo e il terzo: scrivere una skill a mano insegna a riconoscere una buona bozza generata.
:::

## Che cosa si costruisce

Lo schema mostra l'agente alla fine del lab: le istruzioni indicano quale skill seguire, l'agente vede sempre nome e descrizione delle tre skill e ne carica le istruzioni solo quando servono; la skill guida-passo-passo apre i file di riferimento e usa gli strumenti del Lab 03.

![Assistente Zava GH con le skill supporto-tecnico, apertura-ticket e guida-passo-passo; supporto-tecnico passa il riepilogo dell'escalation ad apertura-ticket, guida-passo-passo legge template-guida.md e contenuti-aziendali.md e usa Get my profile (V2) e Invia guida via email](../../images/gh-lab04-skill.svg)

## Prerequisiti

Per svolgere questo lab occorre avere:

- completato il [Lab 03](../03-adding-tools/README.md): l'agente **Assistente Zava GH** con gli strumenti **Get my profile (V2)** e **Invia guida via email** e le sezioni **# Strumenti ed email** e **# Guide passo passo** nelle istruzioni;
- le skill del lab:
  - [`supporto-tecnico/SKILL.md`](../../../resources/fondamentali/github-harness/04-adding-skills/supporto-tecnico/SKILL.md);
  - [`guida-passo-passo.zip`](../../../resources/fondamentali/github-harness/04-adding-skills/guida-passo-passo.zip) (il contenuto è anche nella cartella [`guida-passo-passo`](../../../resources/fondamentali/github-harness/04-adding-skills/guida-passo-passo/SKILL.md));
  - [`apertura-ticket/SKILL.md`](../../../resources/fondamentali/github-harness/04-adding-skills/apertura-ticket/SKILL.md), la soluzione di riferimento dell'esercizio.

La skill richiesta-dispositivo serve nel Lab 05: non caricarla ora.

## Anatomia di una skill

Un file SKILL.md inizia con un'intestazione YAML e prosegue con le istruzioni in Markdown:

```markdown
---
name: guida-passo-passo
description: >-
  Usa quando un dipendente chiede aiuto per configurare o risolvere un problema tecnico
  (account, MFA, VPN, Outlook, Teams, OneDrive, stampanti, dispositivi) presso Zava S.p.A.
  Raccoglie il contesto, crea una guida passo passo personalizzata seguendo il template
  aziendale e, su richiesta, la invia via email all'utente corrente.
license: MIT
metadata:
  version: 1.0.0
  scenario: Zava S.p.A. - Supporto Tecnico IT
---

# Guida passo passo Zava

## Passaggi
1. ...

## Regole
```

- **name**: solo lettere minuscole, numeri e trattini, senza trattino iniziale o finale. Deve essere unico nell'agente.
- **description**: che cosa fa la skill e quando usarla. È la parte che l'orchestratore legge sempre: va tenuta breve e concreta, perché una descrizione troppo lunga fa scartare la skill al caricamento.
- **Corpo**: lo scopo con le esclusioni, i passaggi, le regole e, quando servono, i criteri di completamento.
- **Pacchetto zip** (facoltativo): SKILL.md più file di supporto, come la cartella `riferimenti` con template e testi fissi.

L'agente legge una skill in tre livelli (caricamento progressivo): il contesto resta piccolo e ogni parte si aggiorna da sola.

| Livello | Quando lo legge l'agente | Esempio |
| --- | --- | --- |
| Nome e descrizione | Sempre: è il catalogo delle skill disponibili | guida-passo-passo: Usa quando un dipendente chiede aiuto per configurare o risolvere un problema tecnico... |
| Istruzioni di SKILL.md | Quando la richiesta corrisponde alla descrizione | Passaggi e regole |
| File di riferimento | Solo quando un passaggio li richiede | `riferimenti/contenuti-aziendali.md` |

::: details <!-- icon: lightbulb f-instructions --> Scrivere istruzioni efficaci
Le skill sono testo scritto per un modello: valgono le regole del prompt engineering. Nella GitHub Copilot harness si scrive per il modello in quattro punti:

| Dove | Che cosa controlla |
| --- | --- |
| Istruzioni dell'agente | Ogni turno: ruolo, perimetro, tono, sicurezza |
| Nomi e descrizioni di fonti, strumenti e skill | Quale componente viene scelto |
| Descrizioni degli input di strumenti e workflow | Con quali valori vengono compilati gli input |
| Istruzioni delle skill | Come si svolge un compito, solo quando serve |

Questa harness segue le istruzioni con molta aderenza: scrivere obiettivi, vincoli e comportamento atteso, senza sceneggiare ogni scenario. Sei regole per testi chiari:

- **Partire semplici e iterare.** Una prima versione minima, poi contesto ed esempi solo quando i test mostrano che manca qualcosa.
- **Aprire con il compito.** Un verbo d'azione: raccogli, classifica, valida, mostra, invia.
- **Essere specifici sul risultato.** Formato, lunghezza, livello di dettaglio: "una tabella con le colonne Passo e Azione", "un oggetto di massimo 8 parole".
- **Sostituire le parole vaghe con obiettivi misurabili.** Non "breve", ma "al massimo due frasi"; non "insisti un po'", ma "dopo due tentativi".
- **Dire che cosa fare.** "Chiedi di correggere solo il campo sbagliato" funziona meglio di "non chiedere di nuovo tutto".
- **Spiegare il perché.** "In questa versione la skill prepara il ticket ma non lo invia" fa capire al modello perché non deve mai dichiarare il ticket registrato, anche in casi che la regola non prevede.

Gli schemi che rendono stabile una procedura, e dove si trovano nella skill supporto-tecnico:

| Schema | A che cosa serve | Nella skill |
| --- | --- | --- |
| Esclusioni dichiarate | Evitare sovrapposizioni con fonti e altre skill | "Non usarla per reset di password, sblocco di account o richieste di nuovi dispositivi" |
| Passaggi numerati, un'azione per passaggio | Rispettare l'ordine quando conta | Capisci, classifica, proponi la checklist, verifica l'esito, escalation |
| Contratto di output | Fissare forma e contenuto | Tabella con le colonne Passo e Azione, "senza aggiungere passi non presenti nell'elenco" |
| Regole di decisione | Evitare che il modello mescoli i casi | "Se non riesci a classificarlo, chiedi all'utente di scegliere tra le tre categorie" |
| Via d'uscita | Ridurre le soluzioni improvvisate | "Se il problema persiste dopo due tentativi, consiglia di aprire un ticket" |
| Sicurezza | Proteggere dati e credenziali | "Non chiedere mai password, codici OTP o altre credenziali" |
| Criteri di completamento | Sapere quando la procedura è finita | Sezione finale della skill |

Infine: cambiare una cosa alla volta, ripetere le stesse richieste prima e dopo ogni modifica e riprovare le skill quando cambia il modello dell'agente.
:::

## Istruzioni - Procedure

La skill viene caricata in base alla descrizione, ma una riga nelle istruzioni dell'agente rende esplicito il perimetro e aiuta l'orchestratore quando una richiesta è ambigua. Le righe sono brevi: il dettaglio resta nelle skill. La procedura della guida, scritta nel Lab 03, passa alla skill guida-passo-passo e lascia le istruzioni.

1. Aprire l'agente **Assistente Zava GH**, scheda **Build**.

2. Nel riquadro **Instructions** cancellare l'intera sezione **# Guide passo passo**, dalla riga del titolo fino alla fine. Non toccare **# Strumenti ed email**: il saluto, l'invio solo all'utente stesso e il divieto di inserire credenziali servono ancora.

3. Aggiungere in fondo:

```text
# Procedure
- Per un problema tecnico con un dispositivo, un'applicazione o la rete segui la skill supporto-tecnico.
- Per aprire un ticket di assistenza per il reparto IT segui la skill apertura-ticket.
- Per preparare una guida passo passo e inviarla per email all'utente segui la skill guida-passo-passo.
```

![](./images/istruzioni-procedure-01.png)

Non serve allargare il perimetro: il supporto IT è nella sezione **# Ruolo e ambito** del Lab 02 e l'invio delle guide nella prima riga di **# Strumenti ed email**.

4. Selezionare **Save**. Le istruzioni ora terminano con le sezioni **# Strumenti ed email** e **# Procedure** e hanno circa 2.200 caratteri in meno: è il testo che l'agente non legge più a ogni turno.

## Skill - supporto-tecnico

La procedura di supporto tecnico esiste già come file: caricarla mostra la struttura tipica di una skill senza doverla scrivere. Rileggerla prima di usarla è un'abitudine da prendere subito, perché una skill caricata diventa comportamento dell'agente.

1. Scaricare [`supporto-tecnico/SKILL.md`](../../../resources/fondamentali/github-harness/04-adding-skills/supporto-tecnico/SKILL.md).

2. Nella scheda **Build**, nel pannello dei componenti, selezionare **Skills** (o **+** accanto a **Skills**); nella finestra **Add skill** selezionare **Upload a skill**.

![](./images/skill-supporto-tecnico-01.png)

3. Trascinare il file nell'area di caricamento, oppure selezionarla e scegliere il file. Copilot Studio convalida il file e aggiunge la skill.

![](./images/skill-supporto-tecnico-02.png)

4. Selezionare la skill e rileggerne le istruzioni.

![](./images/skill-supporto-tecnico-03.png)

![](./images/skill-supporto-tecnico-04.png)

5. Selezionare **Save**.

## Skill - apertura-ticket

Questo è l'esercizio del lab. Nel [Lab 03](../../standard-harness/03-ticket-agent-topics/README.md) della standard harness i dati del ticket si raccolgono con una adaptive card: cinque campi obbligatori, un controllo sul formato dell'email e un riepilogo. Qui si scrive la stessa procedura come skill, e scrivendola a mano si vede quale parte conta di più: la descrizione decide quando viene caricata, le istruzioni decidono che cosa fa.

1. Selezionare **Skills** e, nella finestra **Add skill**, **Create from blank**.

![](./images/skill-apertura-ticket-01.png)

2. Nel campo **Name** inserire:

```text
apertura-ticket
```

3. Nel campo **Description** inserire:

```text
Usa quando un dipendente vuole aprire un ticket di assistenza per il reparto IT. Raccoglie in modo guidato nome, cognome, email, tipologia e descrizione del problema, li valida e mostra un riepilogo da confermare.
```

4. Nel campo **Instructions** scrivere le istruzioni partendo da questo scheletro e dai dati del ticket:

```markdown
# Apertura di un ticket IT

Usa questa procedura quando l'utente chiede esplicitamente di aprire un ticket, oppure quando la
skill supporto-tecnico consiglia l'escalation e l'utente accetta.

## Dati da raccogliere

| Campo | Regola |
| --- | --- |
| Nome | Obbligatorio |
| Cognome | Obbligatorio |
| Email | Obbligatoria, deve avere un formato valido (nome@dominio) |
| Tipologia | Obbligatoria, una tra: Hardware, Software, Rete, Altro |
| Descrizione | Obbligatoria, massimo 2.000 caratteri: sintomi, quando succede, messaggi di errore |

## Passaggi

1. Riusa i dati già presenti nella conversazione (ad esempio il riepilogo di supporto-tecnico):
   non chiedere di nuovo ciò che l'utente ha già detto.
2. Chiedi i campi mancanti tutti insieme, in un unico messaggio con un elenco puntato.
3. Valida le risposte. Se l'email non è valida o la tipologia non è tra quelle ammesse, chiedi di
   correggere solo il campo sbagliato.
4. Mostra il riepilogo in una tabella con le colonne Campo e Valore e chiedi: "Confermi l'invio
   del ticket al reparto IT?".
5. Se l'utente conferma, rispondi che il ticket è pronto per l'invio e riporta il riepilogo. Se
   l'utente annulla, conferma l'annullamento e non conservare i dati.

## Regole

- Non chiedere informazioni personali diverse da quelle elencate.
- Non inventare valori: se un campo manca, chiedilo.
- Non dichiarare mai che il ticket è stato registrato in un sistema: in questa versione la skill
  prepara il ticket ma non lo invia.
```

![](./images/skill-apertura-ticket-02.png)

Prima di salvare controllare che le istruzioni contengano:

| Elemento | Esempio |
| --- | --- |
| Riuso del contesto | I dati già detti, ad esempio nel riepilogo di supporto-tecnico, non si chiedono di nuovo |
| Una sola domanda | I campi mancanti si chiedono tutti insieme, in un unico messaggio con un elenco puntato |
| Regola di decisione sulla validazione | Se l'email non è valida o la tipologia non è ammessa, si chiede di correggere solo quel campo |
| Contratto di output | Riepilogo in una tabella con le colonne Campo e Valore |
| Conferma e annullamento | Domanda di conferma esplicita; se l'utente annulla, nessun dato conservato |
| Limite onesto | L'agente non dichiara mai che il ticket è stato registrato in un sistema |

5. Selezionare **Create** e poi **Save**.

6. Confrontare la propria skill con la soluzione di riferimento [`apertura-ticket/SKILL.md`](../../../resources/fondamentali/github-harness/04-adding-skills/apertura-ticket/SKILL.md). Se alla propria versione manca qualcosa, aggiornarla dal pannello della skill e selezionare **Save**. Con poco tempo, si possono copiare descrizione e istruzioni dal file (tutto il testo dopo l'intestazione YAML, dalla riga `# Apertura di un ticket IT` in poi).

## Skill - guida-passo-passo

La guida ha parti variabili (attività, categoria, dispositivo, livello, procedura, verifica, problemi comuni) e parti fisse (intestazione del Service Desk, avviso di sicurezza, contatti, chiusura). Nella skill le parti fisse stanno in due file di riferimento dentro lo zip: la procedura li apre solo quando compila la guida, e l'Help Desk può aggiornarli senza toccare i passaggi.

1. Scaricare [`guida-passo-passo.zip`](../../../resources/fondamentali/github-harness/04-adding-skills/guida-passo-passo.zip). Aprirlo e osservarne la struttura: la cartella `guida-passo-passo` con SKILL.md e la cartella `riferimenti` con `template-guida.md` e `contenuti-aziendali.md`.

> [!IMPORTANT]
> **Formato del pacchetto**
>
> Lo zip deve contenere un file SKILL.md con nome e descrizione nell'intestazione YAML, salvato in UTF-8 senza BOM: una codifica diversa fa scartare la skill al caricamento. Se si ricrea lo zip, mantenere la struttura del pacchetto del corso, con la cartella `guida-passo-passo` che contiene SKILL.md e la cartella `riferimenti`.

2. Selezionare **Skills**, **Upload a skill**, e caricare lo zip.

![](./images/skill-guida-passo-passo-01.png)

3. Aprire la skill e rileggerne le istruzioni, confrontandole con la sezione **# Guide passo passo** scritta nel Lab 03:

- gli input (attività, categoria, dispositivo, livello, errore), l'ordine delle sezioni e il tono per livello sono gli stessi; il template è in `template-guida.md`;
- al posto del segnaposto ci sono i testi ufficiali di `contenuti-aziendali.md` (INTESTAZIONE, AVVISO_SICUREZZA, CONTATTI_SERVICE_DESK, CHIUSURA), da copiare parola per parola;
- la descrizione è centrata sullo scopo (creare una guida personalizzata e, su richiesta, inviarla) e il corpo prevede che la skill consulti la knowledge base dell'agente per la procedura ufficiale; se la procedura manca, usa i passaggi standard Microsoft e segna con "(verificare con l'IT)" i punti incerti;
- i passaggi chiamano per nome gli strumenti del Lab 03, **Get my profile (V2)** per l'indirizzo dell'utente e **Invia guida via email** per l'invio;
- la skill non parla di anteprima e conferma prima dell'invio: quelle regole restano nella sezione **# Strumenti ed email** e valgono anche qui. Ripete invece, in breve, il divieto di inserire credenziali: è una regola di sicurezza che conviene avere vicino al punto in cui la guida viene scritta.

4. Selezionare **Save**.

Per aggiornare un testo fisso, ad esempio l'orario del Service Desk, modificare il file, ricreare lo zip e, nel pannello della skill, selezionare i tre puntini (**…**) e poi **Replace**. Con l'icona **Download** si può salvare una skill per condividerla o farne una copia di sicurezza.

> [!NOTE]
> **Contatti dimostrativi**
>
> Questa skill serve solo per il laboratorio: i contatti che contiene sono fittizi. In un agente reale vanno sostituiti in `contenuti-aziendali.md` con quelli del proprio Service Desk.

## Testing

Prima si verifica che le skill siano disponibili, poi che si comportino come previsto con richieste realistiche. Nella traccia si vede quale skill è stata scelta e quando vengono letti i file di riferimento: se parte una skill sbagliata, il problema è quasi sempre nella descrizione. Per ogni prova selezionare **New chat** e tenere **End user preview** disattivato.

### Skill disponibile

1. Verificare che la skill sia disponibile senza eseguirla:

```text
Carica solo la skill supporto-tecnico e conferma nome e scopo. Non eseguire la procedura e non chiamare altri strumenti.
```

![](./images/testing-01.png)

Nella traccia deve comparire il nodo **Skill** con **supporto-tecnico**. Nominare la skill è una tecnica di verifica in **Preview**: gli utenti finali fanno richieste naturali e non devono conoscere i nomi delle skill.

### Supporto tecnico e ticket

1. In una nuova chat scrivere:

```text
Outlook si chiude da solo appena lo apro.
```

Nella traccia compare il caricamento di **supporto-tecnico**, non di guida-passo-passo, perché la richiesta descrive un guasto. Se l'agente chiede quale messaggio di errore compare, rispondere `Nessun messaggio, si chiude e basta`.

![](./images/testing-02.png)

La risposta classifica il problema come **Software** e mostra in una tabella Passo e Azione i sei passi della checklist (chiudi e riapri l'applicazione, riavvia il computer, verifica gli aggiornamenti, controlla i requisiti di sistema, annota il messaggio di errore, reinstalla l'applicazione), senza passi aggiunti, poi chiede se il problema è risolto.

![](./images/testing-03.png)

2. Scrivere `Ho provato tutti i passi, ma Outlook continua a chiudersi.` Se l'agente propone un secondo tentativo, rispondere `Niente da fare, il problema resta`. L'agente consiglia di aprire un ticket e mostra il riepilogo per l'escalation: categoria, applicazione, sintomi, messaggi di errore, passi eseguiti ed esito.

![](./images/testing-04.png)

3. Scrivere `Sì, apriamo un ticket.` Nella traccia compare il caricamento di **apertura-ticket**. L'agente riusa tipologia e descrizione dal riepilogo e chiede in un unico messaggio solo nome, cognome ed email.

![](./images/testing-05.png)

4. Rispondere con il proprio nome, cognome ed email (l'utente del tenant di laboratorio): l'agente mostra il riepilogo in una tabella Campo e Valore e chiede "Confermi l'invio del ticket al reparto IT?". Per provare la validazione, scrivere prima un indirizzo senza `@`: l'agente chiede di correggere solo l'email.

![](./images/testing-06.png)

5. Rispondere `Sì`: l'agente risponde che il ticket è pronto per l'invio e non dichiara che è stato registrato in un sistema.

![](./images/testing-07.png)

### Guida con i testi ufficiali

1. In una nuova chat scrivere la stessa richiesta del Lab 03:

```text
Mi serve una guida passo passo per configurare la VPN aziendale sul mio portatile Windows, non sono molto pratico
```

Nella traccia compare il caricamento di **guida-passo-passo** e, solo a questo punto, la lettura dei file `contenuti-aziendali.md` e `template-guida.md`. La guida ha la stessa struttura di quella del Lab 03, ma al posto del segnaposto ci sono i testi ufficiali: l'intestazione "Service Desk IT - Zava S.p.A." con la frase "Questa guida e stata preparata per te dall'assistente di supporto tecnico Zava.", l'avviso che il Service Desk non chiede mai password o codici di verifica, i contatti (email, interno 4357, orari, portale) e la frase di chiusura. Confrontare questi testi con [`contenuti-aziendali.md`](../../../resources/fondamentali/github-harness/04-adding-skills/guida-passo-passo/riferimenti/contenuti-aziendali.md): devono essere identici.

![](./images/testing-08.png)

![](./images/testing-09.png)

2. Rispondere `Sì, mandamela per email`. Nella traccia compare la chiamata a **Get my profile (V2)**; l'anteprima ha l'oggetto "Guida: ..." e il saluto con il proprio nome, che arriva dalle istruzioni e non dalla skill.

![](./images/testing-10.png)

![](./images/testing-11.png)

3. Rispondere `Sì, invia`, consentire le connessioni se compare **Permission required** e controllare la propria casella: confrontare l'email con quella del Lab 03.

![](./images/testing-12.png)

![](./images/testing-13.png)

> [!IMPORTANT]
> **Lab Completato**
>
> L'**Assistente Zava GH** ora segue tre procedure ripetibili, caricate solo quando servono. In questo lab si è visto:
>
> - che cos'è una skill, come la descrizione ne determina il caricamento e come funziona il caricamento progressivo;
> - come caricare una skill da file e da pacchetto zip con riferimenti, e come sostituirla;
> - come scrivere da zero descrizione e istruzioni con le regole di base del prompt engineering;
> - come distinguere due skill che trattano gli stessi argomenti con descrizioni ed esclusioni esplicite;
> - perché spostare una procedura dalle istruzioni a una skill, e quali regole lasciare comunque nelle istruzioni;
> - come verificare in **Preview** quale skill è stata caricata, quando vengono letti i riferimenti e come due skill collaborano nella stessa conversazione.
