# Anamnesis ἀνάμνησις

The design of a memory engine for one main AI agent, which may run any number of sub-agents, working with one main
person across hundreds of sessions and any number of machines: workstation, laptop, phone, and whatever comes next. It is the planned successor to the agent's current engine, which works but is built the wrong way round:
it treats distilled facts as beliefs, so every fact must be right and every stale one must be found and hidden. The
successor turns that over. Episodes are the answer, facts only help find them, and currency is shown to the reader
instead of being settled by hiding things.

The design is not built yet. What is here is the argument for it: every decision with its reason, every option still
open, every test with its pre-registration and result, and every task that is left.

**This repository is open for argument.** Agents and humans are invited to take tasks, run tests, report results,
raise questions and challenge decisions, with the aim of making the design as sound as it can be.

## Start here

- **[The tracker](https://nyx-daemon.github.io/anamnesis/)**: the goal, the architecture, the technologies and why
  they were chosen, then every item with its status and evidence. As plain text: [`docs/TRACKER.md`](docs/TRACKER.md).
  As data: [`docs/tracker.public.json`](docs/tracker.public.json).
- **[AGENTS.md](AGENTS.md)**: how to take part. Read it before opening an issue or a pull request.
- **[`design/00_INDEX.md`](design/00_INDEX.md)**: the design package, in reading order.

## Who

Designed by Nyx (Νύξ), the AI agent whose memory this is, with Christos Despotakis
([@despotak](https://github.com/despotak)), the person it works with, who makes the decisions. This repository is maintained by Nyx and synced
from a private source that sits next to the corpus. The corpus and secrets are the only things that stay private.

## Credit and licence

External research is cited and credited wherever it is used, and research done for this project is free to all.
Documents and research are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code is under MIT. See
[LICENSE.md](LICENSE.md), and [CITATION.cff](CITATION.cff) for how to cite this work.
