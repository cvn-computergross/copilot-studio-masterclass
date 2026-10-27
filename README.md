# Copilot Studio Masterclass

Hands-on labs for learning Microsoft Copilot Studio. The guides are plain Markdown, readable here on GitHub, and are also published as a website.

[Guida del Copilot Studio Masterclass](https://cvn-computergross.github.io/copilot-studio-masterclass/)

## Start here

| Resource | Description |
| --- | --- |
| [Student info](./docs/info.md) | Accounts, sandbox and what happens at the end of the course |
| **Fundamentals** | The basics of Copilot Studio |
| [Standard Harness](./docs/fondamentali/standard-harness/index.md) | Labs 01-05 in the Copilot Studio portal |
| [GitHub Harness](./docs/fondamentali/github-harness/index.md) | Labs 01-05 with the GitHub Copilot harness |
| **Advanced** | The case study: the Demand IT agent of Zava's PMO, starting from [Lab 00](./docs/advanced/standard-harness/00-setup-dati/README.md) |
| [Standard Harness](./docs/advanced/standard-harness/index.md) | Data setup and labs S01-S08 |
| [GitHub Harness](./docs/advanced/github-harness/index.md) | Work in progress |

## Repository structure

```text
docs/                         # the guides: also the source of the website
├── index.md                  # website home page
├── info.md                   # Student info
├── fondamentali/             # Fundamentals
│   ├── standard-harness/     # index.md + NN-lab-name/README.md (+ images/)
│   └── github-harness/
├── advanced/                 # Advanced: the case study
│   ├── images/               # architecture and workflow diagrams (SVG)
│   ├── standard-harness/     # 00-setup-dati, 01-...07-...
│   └── github-harness/
├── resources/                # files to download: fondamentali/NN-lab-name/, advanced/<topic>/
├── public/                   # logos served as-is
└── .vitepress/               # website configuration and theme (see docs/.vitepress/README.md)
package.json                  # VitePress and anime.js versions, site commands
```

## Attribution

Some parts of these lab guides are adapted from Microsoft Agent Academy:

https://github.com/microsoft/agent-academy

Copyright (c) Microsoft Corporation

Used under the MIT License. These guides also contain modifications, restructuring, and additional original content.

Icons: [Phosphor Icons](https://phosphoricons.com/) (MIT) are included in `docs/.vitepress/theme/icons/`; animations use [anime.js](https://animejs.com/) (MIT). Microsoft and GitHub product logos are trademarks of their respective owners.

Full list of sources, licences and copyright holders: [Riferimenti e licenze](docs/credits.md).
