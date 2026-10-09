# Copilot Studio Masterclass Labs

Hands-on labs for learning Microsoft Copilot Studio organized into two learning paths.

## Learning Paths

Start from [Info studenti](./docs/info.md) for accounts, sandbox and reset policy.

| Path | Description |
|------|-------------|
| [Standard Harness](./docs/standard-harness/index.md) | Build agents in the Copilot Studio portal, from environment setup to multi-agent and autonomous scenarios. 13 labs. |
| [GitHub Harness](./docs/github-harness/index.md) | Build and manage agents with a code-first, GitHub-based workflow. Work in progress. |

## Repository Structure

```text
docs/
├── index.md              # Masterclass home
├── info.md               # Accounts, sandbox and reset policy
├── standard-harness/     # Portal-based labs (01-13)
│   ├── index.md
│   └── NN-lab-name/
│       ├── README.md
│       └── images/       # <section>-NN.png, in order of appearance
├── github-harness/       # Code-first labs
│   └── index.md
└── resources/            # Files to download, one folder per lab
    └── NN-lab-name/
website/                  # MkDocs site sources (see website/README.md)
```

## Notes

- Files to download are collected in `docs/resources/`, one folder per lab.
- Images are named after the lab section they appear in, numbered in order (e.g. `creazione-flow-03.png`).
- Image links are standard relative Markdown links so they render correctly on GitHub.
- Check the prerequisite callouts inside each lab before starting.

## Attribution

Some parts of these lab guides are adapted from Microsoft Agent Academy:

https://github.com/microsoft/agent-academy

Copyright (c) Microsoft Corporation

Used under the MIT License. These guides also contain modifications, restructuring, and additional original content.
