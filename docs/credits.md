# Riferimenti e licenze

[← Home del corso](../README.md)

Questo corso riusa materiali e strumenti open source. In questa pagina trovi da dove vengono, a cosa servono nel sito e con quale licenza sono distribuiti.

## Contenuti dei lab

### Microsoft Agent Academy <!-- icon: student f-instructions -->

Alcune parti delle guide dei lab sono adattate da [Microsoft Agent Academy](https://github.com/microsoft/agent-academy), il percorso gratuito di Microsoft per imparare a creare agenti con Copilot Studio. Il caso pratico dell'Advanced (l'Agente Demand IT di Zava S.p.A.) è modellato sul percorso Operative di Agent Academy, quello dell'Hiring Agent. La corrispondenza tra i due:

| Aspetto di Copilot Studio | Operative (Hiring Agent) | Caso pratico dell'Advanced |
| --- | --- | --- |
| Dati e soluzione | Job Role, Evaluation Criteria, Candidate, Resume, Job Application | Programma, Criterio di valutazione, Proponente, Proposta, Valutazione |
| Multi-agente | Interview Agent connesso | Agente Comitato connesso |
| Automazione su evento | Curriculum via email | Business case via email |
| Documento multimodale | Curriculum PDF | Business case PDF o DOCX |
| Grounding e punteggio | Criteri pesati per ruolo | Criteri pesati per programma con regola di budget |
| Generazione documenti | Interview prep pack | Dossier di revisione |
| MCP e calendario | Riunione di preparazione al colloquio | Sessione di revisione con sponsor e architetto |
| Sicurezza | Policy di selezione del personale | Policy di valutazione degli investimenti, prompt injection nei business case |

- **Uso nel corso:** struttura e parti dei testi delle guide dei lab
- **Licenza:** MIT
- **Titolare:** Copyright (c) Microsoft Corporation
- **Sorgente:** <https://github.com/microsoft/agent-academy>

> [!NOTE]
> Le guide non sono una copia di Agent Academy: contengono modifiche, una struttura diversa e contenuti originali, scritti per questo corso.

Il testo completo della licenza di Agent Academy, come pubblicato nel [file LICENSE](https://github.com/microsoft/agent-academy/blob/main/LICENSE) della repo:

```text
MIT License

Copyright (c) Microsoft Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
```

## Sito e grafica

| Nome | Uso nel sito | Licenza | Titolare |
|---|---|---|---|
| [VitePress](https://vitepress.dev/) | Genera il sito dalle guide: menu, ricerca, tema chiaro/scuro | MIT | Copyright (c) 2019-present, Yuxi (Evan) You |
| [Vue](https://vuejs.org/) | Componenti del tema (header, fondo pagina, avanzamento) | MIT | Copyright (c) 2018-present, Yuxi (Evan) You |
| [anime.js](https://animejs.com/) | Tutte le animazioni del sito | MIT | Copyright (c) 2019 Julian Garnier |
| [Phosphor Icons](https://phosphoricons.com/) | Glifi delle guide, della home e degli schemi dell'Advanced | MIT | Copyright (c) 2023 Phosphor Icons |
| [Inter](https://github.com/rsms/inter) | Carattere del testo, incluso nel tema di VitePress | SIL Open Font License 1.1 | Copyright (c) 2016 The Inter Project Authors |

Il testo della licenza di Phosphor Icons è incluso nella repo, in `docs/.vitepress/theme/icons/LICENSE.txt`; quelli di VitePress, Vue e anime.js sono nei rispettivi pacchetti npm.

## Loghi dei prodotti <!-- icon: info -->

I loghi dei prodotti che compaiono nelle guide e negli schemi (Copilot Studio, SharePoint, Dataverse, Power Automate, Power Fx, AI Builder, Outlook, Teams, Word, OneDrive, Application Insights e GitHub) sono marchi dei rispettivi proprietari: Microsoft Corporation e GitHub, Inc. Sono usati solo per indicare il prodotto di cui si parla, senza modifiche, e non implicano alcuna approvazione da parte dei titolari.

Come riferimento per le versioni aggiornate dei loghi si è usata la raccolta comunitaria [Microsoft Cloud Product Logos](https://www.mscloudlogos.com/), che non ha una licenza propria: il suo autore precisa di non rivendicare alcun diritto sui file e che tutti i loghi sono di proprietà di Microsoft Corporation.
