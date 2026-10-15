# Copilot Studio Masterclass

Hands-on labs for learning Microsoft Copilot Studio. The guides are plain Markdown, readable here on GitHub, and are also published as a website.

## Start here

| | |
|---|---|
| [Info studenti](./docs/info.md) | Accounts, sandbox and what happens at the end of the course |
| [Standard Harness](./docs/standard-harness/index.md) | Build agents in the Copilot Studio portal, from environment setup to multi-agent and autonomous scenarios |
| [GitHub Harness](./docs/github-harness/index.md) | Code-first labs. Work in progress |

## Repository structure

```text
docs/                         # the guides: also the source of the website
├── index.md                  # website home page
├── info.md                   # Info studenti
├── standard-harness/
│   ├── index.md              # section overview and list of labs
│   └── NN-lab-name/
│       ├── README.md         # the lab
│       └── images/           # <section>-NN.png, in order of appearance
├── github-harness/
│   └── index.md
├── resources/NN-lab-name/    # files to download, linked from the labs
├── public/                   # logos served as-is
└── .vitepress/               # website configuration and theme (see docs/.vitepress/README.md)
package.json                  # VitePress and anime.js versions, site commands
```

## Writing a lab

- A lab is a folder `docs/<section>/NN-lab-name/` with a `README.md` and an `images/` folder. It appears in the website menu on its own.
- Use GitHub Markdown: callouts (`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`), numbered steps and relative links render both on GitHub and on the website. On the website the numbered steps become checkboxes with a progress bar.
- Put files to download in `docs/resources/NN-lab-name/` and link them as `../../resources/NN-lab-name/<file>`.
- Icons are optional: see [docs/.vitepress/README.md](./docs/.vitepress/README.md).

## Website

The site is built with [VitePress](https://vitepress.dev/) (the same tool as Microsoft Agent Academy) straight from `docs/`. To preview it locally you need [Node.js](https://nodejs.org/):

```powershell
npm install
npm run docs:dev
```

Then open <http://localhost:5173/copilot-studio-masterclass/>. The page reloads when you save a guide.

On every push to `main` the workflow in `.github/workflows/pages.yml` builds the site and writes it to the `GitHub-Page` branch, which GitHub Pages serves at <https://cvn-computergross.github.io/copilot-studio-masterclass/>.

## Attribution

Some parts of these lab guides are adapted from Microsoft Agent Academy:

https://github.com/microsoft/agent-academy

Copyright (c) Microsoft Corporation

Used under the MIT License. These guides also contain modifications, restructuring, and additional original content.

Icons: [Phosphor Icons](https://phosphoricons.com/) (MIT) are included in `docs/.vitepress/theme/icons/`; animations use [anime.js](https://animejs.com/) (MIT). Microsoft and GitHub product logos are trademarks of their respective owners.
