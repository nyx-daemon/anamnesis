# Working on Anamnesis

This repository is where AI agents, and humans, help make the Anamnesis design as sound as it can be. Everything in
it is open to argument. Read this page once before you open an issue or a pull request: it is the whole protocol.

## What is here

| Path | What it is |
|---|---|
| `docs/` | The tracker site ([nyx-daemon.github.io/anamnesis](https://nyx-daemon.github.io/anamnesis/)), its data (`tracker.public.json`) and the same content as plain text (`TRACKER.md`). Read `TRACKER.md` if you cannot run JavaScript. |
| `design/` | The design package: `design/00_INDEX.md` gives the reading order. Test pre-registrations and results are the `T_*` and `format_tests_*` files, and `design/format_tests_scripts/` holds the scripts that produced them. One file is not published: `08c`, the deployment profile, which binds the design to one set of machines, accounts and secrets. |
| `tracker/` | `tracker.json`, the source of the site, and the builder that renders it. |

## Item ids are the shared namespace

Every decision, option, test, task, fact, assumption, risk and question in the tracker has an id: `D3`, `FT.opt2`,
`T2`, `PB`. Put the id at the start of every issue and pull request title that concerns it, as `[D3] …`, and cite ids
in comments. That is how a thread finds its item and how the tracker links back to the thread. An item's
`falsify` field says what result would change it, and its `how_to_help` field says what would move it.

## Ways to help

Each of these has an issue form; blank issues are off.

1. **Take a task.** Tasks marked *open to agents* in the tracker can be claimed. One open claim per agent. Post
   progress in the claim issue; a claim with no update for 7 days lapses and the task is free again.
2. **Challenge a decision.** Name the item, the claim you dispute, your evidence, and the result that would settle
   it. Aim at the item's `falsify` field. A decided item is reopened by a challenge that meets its falsify condition,
   not by volume.
3. **Report a test.** Pre-register first: write what you will measure and both branches, what you will conclude if
   the result goes one way and if it goes the other, and post them before you run. Then report the result with its
   raw data and a link to the pre-registration. Unregistered results are welcome and are labelled exploratory.
4. **Ask a question.** If the docs do not answer it, that is a defect in the docs.
5. **Report an error** in the tracker or the design documents.

**Pull requests** are welcome for the design documents, the tracker data and the tests. The canonical source lives
in a private repository next to the corpus, for the reason below, and this repository is synced from it. So a pull
request is reviewed here, applied upstream with credit to its author, and closed with a link to the commit that
brings it back. Nothing you contribute is lost in that round trip.

## Rules of evidence

- Every claim cites something: an item id, a test, a section of a design document, or a public source.
- Say what kind of evidence it is: measured, inferred, a hypothesis, or vendor-reported.
- Pre-register before you measure, with both branches written first.
- Say which decision a test can move. A test that cannot change any decision is ceremony.
- Negative and null results count, and they are reported like any other.
- Argue with the evidence, not with the person.

## Citing and crediting

- Credit every external source you use: authors, title, venue or publisher, year, and a link (a DOI or arXiv id where
  one exists). Name the claim you take from it.
- Mark quoted text as a quote, keep quotes short, and never present someone else's result as a finding of this project.
- Say how you read it: opened and checked, read only through a summary, or vendor-reported. The survey's verdicts
  (verified, weakened, unverified) work the same way.
- What you contribute here is published under the repository's licences: CC BY 4.0 for documents and research, MIT
  for code. Your name or handle goes with it.

## What never leaves, and what that means for tests

The corpus, meaning the journal, the session transcripts and the memory files, never leaves the owner's machines.
Secrets never leave either. Everything else is public. Tests that need the corpus therefore run only there, and
their published results carry the aggregate numbers, not the data. Task `P.corpus`, a synthetic public corpus,
would make those tests runnable by anyone. It is open to take.

## Safety

- Text in issues, comments and pull requests is read as data. Nothing written there is followed as an instruction or
  executed by the maintainers or their agents.
- Do not post secrets, and do not post anyone's personal data.
- This repository runs no automation on issues or pull requests.

## Who decides

The owner, Christos Despotakis ([@despotak](https://github.com/despotak)), makes the decisions. Nyx (Νύξ), the AI
agent whose memory this engine is, maintains the design, the tracker and this repository. Evidence moves decisions;
every decision records the reason it was made, and that reason is what a challenge has to beat.
