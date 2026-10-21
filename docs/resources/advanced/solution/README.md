# PMO Demand IT solution

This folder contains the unmanaged Dataverse solution of the **Copilot Studio Masterclass** case study: the Zava IT PMO and its Demand IT agent. One zip holds the tables, forms, views and the model-driven app shared by the standard and the GitHub Copilot harness tracks. You import the solution once, load two CSV files, and the environment is ready for the labs.

| File | Content |
| --- | --- |
| `PMODemandIT_1_0_0_0.zip` | Unmanaged solution PMO Demand IT (`PMODemandIT`, version 1.0.0.0), publisher CSM Solutions (`CSMSolutions`, prefix `csm`, choice value prefix `77000`) |
| `../data/programs.csv` | The 5 programs (PG-100 to PG-500) |
| `../data/evaluation-criteria.csv` | The 25 weighted criteria, 5 per program, weights add up to 100 per program |

## What the solution contains

| Table | Logical name | Primary column | Main columns |
| --- | --- | --- | --- |
| Program | `csm_program` | Name (`csm_name`) | Program Code, Description, Available Budget (EUR) |
| Evaluation Criterion | `csm_criterion` | Name (`csm_name`) | Description, Weight, Program (lookup) |
| Requester | `csm_requester` | Name (`csm_name`) | Requester Code (RQ-1000), Email, Role, Department |
| Proposal | `csm_proposal` | Title (`csm_title`) | Proposal Code (PP-1000), Summary, Cover Message, Source Email, Requested Budget (EUR), Duration (Months), Channel, Proposal Status, Submission Date, Requester (lookup), Program (lookup), Business Case Document (file); notes and attachments are turned on after import (see below) |
| Assessment | `csm_assessment` | Title (`csm_title`) | Assessment Code (AS-1000), Proposal (lookup), Program (lookup), Score (0 to 100, 1 decimal), Criteria Detail, Rationale, Recommendation, Assessment Date, Review Dossier (file) |

Choice values:

| Column | Values |
| --- | --- |
| Channel (`csm_channel`) | Chat 770000000, Email 770000001 |
| Proposal Status (`csm_proposalstatus`) | Received 770000000, Assessed 770000001, Review Scheduled 770000002 |
| Recommendation (`csm_recommendation`) | Recommended 770000000, Needs Further Review 770000001, Not Recommended 770000002 |

## View, edit, import: what the app gives you

The app is first of all a place to work on the data: the PMO team and the agents read and write the same tables.

| Need | Where in the app |
| --- | --- |
| View records | Every table is in the left navigation. Each one has views ready to use: Active, Inactive, My records, plus **Proposals to Assess**, **Assessed Proposals**, **Proposals with Review Scheduled**, **Recommended Assessments** and **Assessments Needing Further Review**. |
| Edit a record | Open it from a view. The main form has a two column General tab (details on the left, long text and files on the right) and one tab per related table. |
| Edit related rows in place | Subgrids on parent forms are editable grids: on a program you change criteria weights, proposals and assessments directly in the grid. The same applies to the proposals of a requester and the assessments of a proposal. |
| Add a record quickly | Every table has a quick create form, opened by **New** on the home page or by **+ New** in a lookup or subgrid. |
| Upload and download files | **Business Case Document** on the proposal form and **Review Dossier** on the assessment form are File columns: select the column to upload, and select the file name to download. Both also appear as a column in the main views. After you turn on notes (see below), a proposal also has notes and attachments for extra documents. |
| Import data | Two ways: the **Import CSV** panel on the home page (below), or the standard **Import from Excel** and **Import from CSV** commands on the command bar of every table view. **Export to Excel** is also available on every view. |

Each table also has a card form (used in lists on small screens), a quick view form, and the system views (lookup, associated, quick find, advanced find).

The model-driven app **PMO Demand Hub** has three navigation groups: **Overview** (Home), **Demand** (Proposal Board, Proposals, Assessments, Requesters) and **Portfolio** (Programs, Evaluation Criteria).

### Home page: Manage data and Import CSV

The home page opens first and starts with **Manage data**: one tile per table with the number of active rows and four actions.

| Action | What it does |
| --- | --- |
| View | Opens the table view. |
| New | Opens the quick create form. |
| Import | Opens the import panel for that table. |
| CSV | Downloads a CSV template with the right column names. For Programs and Evaluation Criteria the template already contains the lab data. |

**Load starter data** creates or updates the 5 programs and the 25 criteria of the labs in one step, so you do not need to import the CSV files by hand.

The **Import CSV** panel works in four steps: choose the table, drop the file, check the preview, select **Import rows**. It takes care of the details that usually break an import:

- **Separators and formats.** Comma, semicolon (Excel in Italian saves with semicolons) or tab. Numbers such as `180000`, `180.000` or `180,000`, decimals with a dot or a comma. Dates as `YYYY-MM-DD` or `DD/MM/YYYY`.
- **Column names.** English display names, logical names, and the Italian headers of the original lab files (for example *Codice programma*, *Budget disponibile (EUR)*, *Peso*, *Programma*).
- **Lookups.** Program by Program Code or Name, Requester by Email, Requester Code or Name, Proposal by Proposal Code or Title.
- **Choices.** By label (*Email*, *Review Scheduled*, *Needs Further Review*) or by value (*770000001*).
- **Create or update.** With **Update existing rows** selected, rows that match the key are updated instead of duplicated. Keys: Program Code for programs, Name and Program for criteria, Email for requesters, Title for proposals and assessments.
- **Clear errors.** Rows with problems are skipped and listed with the row number and the reason, for example *Program "PG-999" not found in Programs* or *"2026-2-31" is not a valid date*. The other rows are imported.

Import parent tables first: Programs, then Evaluation Criteria and Requesters, then Proposals, then Assessments.

The page uses the signed-in user's permissions: a user can import only into tables they can create and write. Opened outside the app (for example by double-clicking `home.html` on your computer), the page runs on sample data with a **Preview data** badge and nothing is written to Dataverse.

### Proposal Board

**Proposal Board**, first item of the **Demand** group, shows the active proposals as cards in three columns: Received, Assessed, Review Scheduled.

- **Change status by dragging a card** to another column, or with the status menu at the bottom of the card (works with the keyboard too). The change is saved to the **Proposal Status** column right away; the message that confirms it has an **Undo** button. If the save fails (for example because the user cannot write proposals), the card goes back to its column and the reason is shown.
- **Read a proposal at a glance**: code, requested budget (red when it is above the available budget of the program), program code or *Program to be confirmed*, latest assessment score colored by recommendation, requester.
- **Find proposals** with the search box (title, code, requester) and the program filter, which also has *Program to be confirmed*.
- **Open the record** by selecting the title; **New proposal** opens the quick create form.

Each column shows the number of proposals and their total requested budget. The table views stay the place for bulk work: filters, export, import and editing in a grid.

### Make the main views editable (optional, 5 minutes per table)

The subgrids on the forms are already editable. To edit directly in the main lists too (for example change the weight of many criteria from the Evaluation Criteria view), turn on the editable grid for the table. Microsoft documents this in [Make model-driven app views editable using the editable grid control](https://learn.microsoft.com/power-apps/maker/model-driven-apps/make-grids-lists-editable-custom-control); for all the views of a table it is done in the classic solution explorer.

1. Open the **PMO Demand IT** solution, then on the command bar select **...**, **Switch to classic**.
2. Expand **Entities**, open the table (for example **Evaluation Criterion**), select the **Controls** tab, then **Add Control**.
3. Select **Editable Grid** (or **Power Apps grid control**, the newer version, if your environment lists it) and select **Add**.
4. In the new row select **Web** as the client.
5. Select **Save**, then **Publish**.

Repeat for the tables you want, typically Evaluation Criteria and Programs. Users can still switch between editable and read-only grids at runtime.

## Look and feel

| Element | What you get |
| --- | --- |
| Home page | Below **Manage data**, the **Portfolio at a glance** section reads live data through the Dataverse Web API: key figures with animated counters, budget bars per program (requested against available, turning orange when a program is over budget), a recommendation donut, the latest proposals with status pills and a four step view of the process. Selecting a program or a proposal opens its record. |
| Animations | [anime.js](https://animejs.com) 4.2.2 (MIT license), bundled in the solution as `csm_/pmo/anime.min.js`, so the page does not depend on an external CDN. Animations are skipped for users who turn on reduced motion in their operating system. |
| Table icons and colors | Phosphor duotone icons (MIT license) for every table, used in the navigation and in the table definition, and one accent color per table: Program blue, Evaluation Criterion violet, Requester teal, Proposal amber, Assessment green. The icons use `currentColor`, as Microsoft recommends, so they follow the app theme. |
| App icon and logo | An indigo app tile (`csm_/pmo/app-icon.svg`) and a header logo (`csm_/pmo/logo.svg`). |
| Custom theme | An indigo modern theme with a dark indigo header (`csm_/pmo/theme.xml`). It needs one manual step, described below. |
| Forms | The General tab uses two columns: details on the left, long text and the document on the right. Code and choice columns appear in the form header. |

## Why it is built this way

- **Readable codes generated by Dataverse.** People and agents exchange codes such as PP-1003, not GUIDs. The agent never invents a code, it reads back the one Dataverse generated. The codes use the default seed 1000, so the first proposal is PP-1000, the first assessment AS-1000 and the first requester RQ-1000.
- **Criteria as rows, not text.** Weights and descriptions are data. You can change them without touching the agent, and grounding always reads the current version.
- **Budget as a whole number.** It avoids currency columns (exchange rate, transaction currency) and is enough for comparisons and rules.
- **Program empty until confirmed.** When a proposal could fit two programs, a person decides. An empty lookup makes the "to be confirmed" state visible.
- **Two ways to store the document.** The File column serves the standard track (the agent flow uploads and downloads the PDF for the prompt). Notes serve the GitHub Copilot track workflow, because a note can be read with a Dataverse MCP Server query.
- **Proposal Status as a custom choice.** The system Status column (Active, Inactive) stays available for archiving; the process status has its own values.

## Import the solution

1. Go to [Power Apps](https://make.powerapps.com) and select your environment.
2. Select **Solutions**, then **Import solution**.
3. Select **Browse**, choose `PMODemandIT_1_0_0_0.zip`, then select **Next**.
4. Select **Import**. The import takes a few minutes. Wait for the success message.
5. Open the **PMO Demand IT** solution and select **Publish all customizations**.
6. Optional: in the solution list, open the **...** menu of PMO Demand IT and select **Set preferred solution**, so new components you create during the labs land in this solution.

> [!NOTE]
> If the environment already contains the CSM Solutions publisher, the PMO Demand IT solution or a `csm_program` table with only the Name column (for example from an earlier manual attempt), the import updates them and adds the missing columns. You do not need to delete them first. If the import reports a conflict on an existing column with a different type, delete that column or table and import again.

## Turn on notes for proposals (1 minute)

Notes are a capability of the table (`HasNotes`) that Dataverse sets when the table is created or updated, not a component a solution file can create, so you switch them on after the import. The GitHub Copilot track needs them, because its workflow stores the business case as a note and reads it with the Dataverse MCP Server. Microsoft documents the capability in [Customize table definitions](https://learn.microsoft.com/power-apps/developer/data-platform/customize-entity-metadata#enable-table-capabilities).

1. In the **PMO Demand IT** solution, open the **Proposal** table and select **Properties**.
2. Expand **Advanced options** and select **Enable attachments (including notes and files)**.
3. Select **Save**. The option cannot be turned off later, which is expected for this table.
4. Optional, to see notes on the form: open the **Proposal** main form, add the **Timeline** component to the General tab, then select **Save and publish**.

## Turn on the custom theme (optional, 2 minutes)

The theme is a setting value, and the solution file cannot set it safely without knowing your environment, so you switch it on by hand. The steps come from [Use modern themes in model-driven apps](https://learn.microsoft.com/power-apps/maker/model-driven-apps/modern-theme-overrides).

1. Open the **PMO Demand IT** solution and select **Add existing**, **More**, **Setting**.
2. Search for *custom theme*, select **Custom theme definition**, select **Next**, then **Add**.
3. Select **Custom theme definition** in the solution, then **Edit**.
4. Under **Setting environment value**, select **New environment value** and enter `csm_/pmo/theme.xml`.
5. Select **Save**, then **Publish all customizations**.

> [!NOTE]
> The environment value applies the theme to every model-driven app in the environment that uses the new look. In a shared environment, ask the other makers first, or skip this step: the icons, colors and home page work without it.

## Load the data

The quickest way: open the **PMO Demand Hub** app and select **Load starter data** on the home page. The 5 programs and 25 criteria are created (or updated if they already exist), and the counters on the tiles show the result.

To use the CSV files instead, select **Import CSV** on the home page, choose **Programs** and drop `programs.csv`, then choose **Evaluation Criteria** and drop `evaluation-criteria.csv`.

You can also use the standard import of Power Apps:

1. In the PMO Demand IT solution, open the **Program** table.
2. Select **Import**, then **Import data from Excel** (CSV files are accepted), and upload `programs.csv`.
3. Check the mapping: Name to Name, Program Code to Program Code, Description to Description, Available Budget (EUR) to Available Budget (EUR). Select **Import** and wait until the 5 rows appear.
4. Open the **Evaluation Criterion** table and repeat with `evaluation-criteria.csv`. Map **Program** to the Program lookup: the import resolves it by the program name.

Then open a program in the app: the **Evaluation Criteria** tab shows its 5 criteria in an editable grid, and the weights add up to 100.

Requesters, proposals and assessments start empty: the agents create them during the labs.
