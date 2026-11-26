# Anamnesis project tracker

As of commit `9586855` · built 2026-11-26T17:44:32Z · 210 items

A public project tracker for the Anamnesis successor design: what it is for, how it is built and with what, then every decision, option, test and task, with its status and evidence. It leaves out the corpus, secrets, deployment-specific material and the owner's own words.

## The goal

An AI agent that works with one person across hundreds of sessions and many machines needs a memory that outlives the session, the model and the machine, and one it can trust. The current engine works, but it is built the wrong way round. It treats distilled facts as beliefs, so every fact must be right and every stale one must be found and hidden, and most of its machinery exists to do that. The successor is a redesign around what the cited evidence and the measurements here point to: episodes are the answer, facts only help find them, and currency is shown to the reader instead of being settled by hiding things.

### What is wrong today, as measured

1. Ranking carries no currency signal. When both versions of a changed fact were retrieved, the older one ranked first in 22 of 27. The questions were phrased from the old fact, so ranking follows the question's wording, and similarity expansion does not fix it. (T2 (run), T2b (run))
2. Identity is a file position. With the current parsers, adding an id anywhere in the journal re-hashes 779 or 780 of its 780 entries. (T3b (run))
3. Five stores and a separate hash chain share no write lock outside the nightly run (from an audit, not reproduced), and 118 of 280 entry headers named a time ahead of the clock. (D4 (proposed), WP.writer (proposed))
4. Memory rarely reaches a session through recall. Over 30 days, 36% of sessions grepped the raw journal and 7% called recall, while roughly 260 KB loads into every session. (F.grep30 (measured), F.recalluse (measured), F.canonsize (inferred))
5. What gets written is not checked enough. A review found 10 of 74 auto-authored entries with an unsupported claim, and 1 of 20 after the fix. (F.unsupported (measured))
6. It is coupled to specific models. Thresholds fitted to specific quantised models break silently on a swap, and every writing stage hangs on one login. (RL.roles (decided), R.login (open))
7. The agent now reads an untrusted social network, so what it writes into memory can be poisoned. On the survey's reading, the only defence with evidence is provenance assigned by code at write time. (LF.origin (decided), IS.fence (proposed))

### What success looks like

1. Answer with evidence. Every recalled memory comes back as a dated episode with its evidence and a rope to its transcript. (DL.recall (proposed), D2 (decided))
2. Show currency and hide nothing. A reader sees the timeline newest first, and an outdated fact is marked, not removed. (D3 (proposed), CU.wrong (proposed), CU.timeline (proposed))
3. Lose nothing. The transcript stays the ground truth, every derived store rebuilds from it, and only three logged doors remove anything. (L.transcripts (decided), DO.nosilent (decided))
4. Survive a change of model, vendor or machine. A swap is a re-test against a gate, not a rewrite. (RL.roles (decided), RL.gates (proposed), E8 (planned))
5. Go where the agent goes. Any number of machines, from workstation to laptop to phone, each writing its own segment, merging as a union. (SCOPE (decided), PORT.Q (open), D4 (proposed))
6. Resist poisoning. Origin is assigned by code at write time, never by a model. (LF.origin (decided))
7. Be smaller. The design counts 40 mechanisms against today's 50. (MG.mech (proposed))
8. Beat the current engine on a private gold set, against bars written before anything is built. (EV.principles (proposed), D7 (proposed), GS2 (todo))

### What it is not

1. Not a product or a benchmark entry. Public benchmarks run, if at all, only as sanity checks. (NA.bench (proposed))
2. Not forgetting. Nothing is dropped by decay or to save space. (NA.decay (proposed), DO.nosilent (decided))
3. Not multi-user. One main person, with others only at the edges, and one main agent, which may run any number of sub-agents. (SCOPE (decided))
4. Not tied to one model, vendor or machine. (RL.roles (decided))
5. Not closed. Everything but the corpus and secrets is public, external research is credited, and the project's own research is free to all. (OPENRES (decided), VENUE (decided))

## Architecture

What is being built: a memory engine in which the transcript is the only ground truth and everything above it is derived and can be rebuilt from it. A memory is made once, through one writer, and each item in its Record is checked against its transcript, where one exists, before the file is created. It is kept as an immutable episode file. Facts are keys that find episodes, a ledger records every derived decision, and a disposable projection serves recall. Labels decide where content may flow, never whether it is kept, and only three logged doors ever remove anything.

### The design in eight rules

1. Transcripts are the only ground truth. Everything above them is derived and can be rebuilt. (L.transcripts (decided), L.layers (proposed))
2. One writer. Every episode is born through the same append, created atomically and never rewritten by a machine. (WP.writer (proposed), D1 (decided))
3. Record items are checked against the transcript before the file exists, and a fact the memory relies on must be in the Record, not only in the prose. (RL.verifier (proposed), EF.verify (proposed), EF.reflection (decided))
4. Facts are keys into episodes, never beliefs. Recall answers with the episode and its evidence. (D2 (decided))
5. Roles, not models. A filler that passes the gate fills the role, and a replacement passes it again. (RL.roles (decided), RL.gates (proposed))
6. Labels route, never filter. They decide where content may flow, never whether it is kept. (LF.labels (decided), O12 (decided))
7. Nothing in the cache is the only copy of anything, and recall writes nothing outside it. (L.projection (proposed), RT.nowrite (proposed))
8. Nothing is deleted silently. Only three logged doors remove anything. (DO.nosilent (decided))

### The map

Each box links to the item that decides it and takes that item's status, so the map changes when a decision does. Read the lanes in order: sources, making, keeping, serving.

- **Labels, over all of it** · LF.labels (decided). Labels decide where content may flow, never whether it is kept. Live credentials are the one content never stored. Also: O23 (decided), LF.rules (decided), LF.sinks (decided), LF.enforce (decided), LF.guard (decided), LF.origin (decided).

#### 1. Sources: what every memory is made from

- **Transcripts** `L0` · L.transcripts (decided). Written by the harness and never edited: the only ground truth. Also: D10 (open), R.L0creds (open).
- **The session itself** · O9 (decided). The author drafts in session, and code pre-fills what code can know.
- **The legacy journal** · EF.legacy (proposed). Old prose, kept byte for byte as each episode's Reflection. Also: O6 (decided), O1 (decided).

→ *mined or written*

#### 2. Make: how a memory is made

- **Transcript-first mining** · O4 (decided). Every in-scope session, newest first. Output waits in a quarantine until the gates pass. Also: WP.mining (proposed), O13-15 (decided).
- **Producer** · D9 (proposed). Turns transcript text into typed items as JSON, and code renders the file. Also: R.login (open).
- **Pass B producer** · O7 (decided). For legacy prose whose transcript is gone. Choosing its producer is task PB. Also: PB (todo).
- **Refusal means deferral** · WP.defer (decided). What a producer refuses waits for a freer one. Never dropped.
- **Every write passes the roles** · RL.roles (decided). Each role has a gate on a frozen set. Until a filler passes, its output goes only to the quarantine. Also: RL.gates (proposed).
  - **Credential screen** · RL.screen (decided). Redacts live credentials before any author or producer sees the input. Also: WP.cred (proposed).
  - **Verifier** · RL.verifier (proposed). L0 mechanical checks first, then an L1 judge that never overrides them. Also: EF.verify (proposed).
  - **Label classifier** · O12 (decided). Adds labels and never removes one.
  - **Signer** · O21 (decided). Signs daily roots and promotion batches, and nothing else. Also: LI.root (decided).
- **The writer** · WP.writer (proposed). Draft, edit, append: the one way an episode is born. A failing item is withheld on its own. Also: EF.revise (proposed).

→ *through the roles, into the ladder*

#### 3. Keep: the ladder, from the answer layer up

- **Episodes** `L1` · D1 (decided). One immutable file each: a Record, a Harvest and a Reflection. FT decides which file type holds them. Also: FT (open), EF.record (proposed), EF.harvest (proposed), EF.reflection (decided), EF.id (proposed).
- **One ledger** `L2` · D4 (proposed). Append-only events, one segment per month per machine, in place of five stores. Also: LI.chain (decided), LI.events (proposed), LI.concurrency (proposed).
- **Facts** `L2·L3` · D2 (decided). Keys into episodes, never beliefs. A wrong fact costs a miss, not a false memory. Also: FA.record (proposed), FA.map (proposed), FA.anchors (proposed).
- **Projection** `L3` · L.projection (proposed). SQLite in the cache, rebuilt from episodes and the ledger in minutes. Also: LI.tables (proposed).
- **Canon** `L4` · L.canon (decided). Curated and always loaded. P3 promotes into it. Also: IS.p3 (proposed), O22 (decided), DL.canoncur (proposed).
- **Audit** · L.audit (proposed). Every check prints what it covered and has a planted fault. Also: DL.pointer (proposed).

→ *served to sessions through the ways in*

#### 4. Serve: how memory reaches a session

- **SessionStart pack** `L5` · DL.pack (proposed). One budgeted injection, with its size logged.
- **Recall** `L5` · DL.recall (proposed). Hybrid keyword, vector and reranker search. Each hit shows its evidence, date and age. Also: RT.fusion (proposed), RT.rerank (proposed), RT.factlane (proposed), RT.nowrite (proposed).
- **What a reader is shown** · D3.Q1 (proposed). How an outdated fact is marked for whoever reads it. Also: D3.C (proposed), CU.wrong (proposed), CU.timeline (proposed).
- **Raw files (grep)** · D3.Q2 (proposed). More sessions grep the raw files (36%) than call recall (7%), and a grep sees no currency marks. D3 decides which door they should take. Also: D3 (proposed).
- **Ambient prefetch** · DL.prefetch (proposed). Log-only until its gate says inject.
- **Always-loaded layer** · D8 (proposed). Measure first, change nothing yet.

- **Doors out: the only ways anything leaves** · DO.nosilent (decided). Each one is logged. Supersede is not delete. Also: DO.bylayer (decided).
  - **Invalidate** · DO.invalidate (decided). Unreachable, and the row is kept. The default, and reversible.
  - **Redact** · DO.redact (decided). A tombstone with reason, time and hash. For always-loaded files, editing is redacting.
  - **Purge** · DO.purge (decided). Bytes gone from every copy. A runbook, never a flag.

The decisions that shape this map most, with their live status: FT (open), D3 (proposed), D4 (proposed), D9 (proposed), D10 (open), D8 (proposed).

### How a memory moves

1. A session runs, and the harness writes its transcript (L0). (L.transcripts (decided))
2. A producer reads the screened transcript and drafts typed items. In session, the author drafts and code pre-fills what code can know. (D9 (proposed), O9 (decided))
3. The credential screen redacts live credentials, the label classifier adds labels, and the verifier checks every quote and anchor against the transcript. (RL.screen (decided), O12 (decided), RL.verifier (proposed))
4. The writer creates the episode file atomically. A failing item is withheld on its own. (WP.writer (proposed), D1 (decided))
5. The ledger records what was derived, facts are extracted as keys, and the projection is rebuilt from the episodes and the ledger. (D4 (proposed), D2 (decided), L.projection (proposed))
6. A session receives memory through the start pack, recall or the raw files. Recall shows each hit with its evidence, date and age; a grep of the raw files shows none of that, which is what D3 is about. (DL.pack (proposed), DL.recall (proposed), D3 (proposed))
7. P3 promotes what passes its gates into canon, and the signer signs the daily root. (IS.p3 (proposed), LI.root (decided))
8. Anything wrong leaves only through invalidate, redact or purge, and each door is logged. (DO.nosilent (decided))

### Six layers, and what lives in git

| Layer | What it is | In git? | Items |
|---|---|---|---|
| `L0` Transcripts | immutable, written by the harness; ground truth | not today; D10 decides | L.transcripts (decided), D10 (open) |
| `L1` Episodes | one file each, minted id; the answer layer | yes | D1 (decided), FT (open) |
| `L2` Ledger | append-only events: every derived decision | yes | D4 (proposed) |
| `L3` Projection | SQLite in the cache, rebuilt from L1 and L2 | no | L.projection (proposed) |
| `L4` Canon | the persona documents and the memory index, curated, always loaded | yes | L.canon (decided) |
| `L5` Delivery | the SessionStart pack, recall and the hooks | code | DL.pack (proposed), DL.recall (proposed) |

## Technologies, and why these

Most choices are deliberately plain: the current engine's measured core, kept until a local challenger beats it on the gold set, and SQLite with plain files, which the survey found to be the safe base at this size. Where a row names a model or a tool, it names today's filler for a role, and any filler that passes that role's gate may replace it. Each row says what it was chosen over.

- **Store: SQLite and plain files.** Why: The survey's safe base at this size. The projection rebuilds in minutes and is never the only copy of anything. Chosen over: A graph database (Graphiti on Neo4j or FalkorDB; Kuzu, now archived). Links are an edge table, and a recursive query covers two hops at this size. DuckDB's vector extension documents its persistence as unsafe. (L.projection (proposed), NA.graph (proposed))
- **Keyword search: SQLite FTS5 with the unicode61 tokenizer, its external-content sync done right.** Why: The measured core. The broken sync cost 0.050 MRR, and the fix is live. Chosen over: For Greek, where keyword search is weakest, E5 tests tokenizer variants, including trigram, and bge-m3's own sparse mode. (RT.kw (proposed), T0 (run), D0 (decided), RT.greek (open), E5 (planned))
- **Vectors: sqlite-vec, exact nearest-neighbour search.** Why: It fits the scale: the scale simulation's median was 0.32 s for 6,000 entries plus 30,000 units. Chosen over: A separate vector database. sqlite-vec is pre-1.0 with its approximate index only in alpha; at this size exact search is fast enough. (RT.vec (proposed), RT.latency (proposed))
- **Embedder: bge-m3, dense vectors (today's filler).** Why: The incumbent. It is multilingual, takes long inputs, and stays until a challenger beats it on a gold set that covers today's corpus. Chosen over: Qwen3-Embedding, reported first on the multilingual MTEB board in June 2025, and EmbeddingGemma, whose 2k-token window would truncate long entries. No leaderboard measures Greek journals. (RT.vec (proposed), NA.bench (proposed))
- **Fusion: A weighted sum of normalised scores, with the weight set by query language.** Why: Measured here: score fusion beat rank fusion, MRR 0.818 against 0.604 on 22 paraphrase pairs. The cited fusion study agrees when a small labelled set exists. Chosen over: Reciprocal rank fusion, measured here and rejected. (RT.fusion (proposed), NA.measured (proposed))
- **Reranker: bge-reranker-v2-m3 over the top 25 episodes (today's filler).** Why: Independent signals, read only through search summaries, keep it competitive on multilingual tasks, and each vendor's own table favours its own model. Chosen over: Qwen3-Reranker, whose A/B on Greek waits for gold set v2; jina-reranker-v3; and late interaction, since no source shows a ColBERT-style model beating dense retrieval plus a cross-encoder on Greek. (RT.rerank (proposed), NA.late (proposed), GS2 (todo))
- **Episodes: One immutable file per episode, with a UUIDv7 id minted at birth and an exclusive create.** Why: Ids tied to a position re-hashed 779 or 780 of 780 entries. Two new files never collide where two appends to one file do. Chosen over: One append-only journal file, as today, and notes rewritten in place (A-MEM). FT decides which format the file uses. (D1 (decided), EF.id (proposed), T3b (run), NA.rewrite (proposed), FT (open))
- **Ledger: Append-only JSONL, one segment per month per machine, written under a lock in whole lines.** Why: A merge of two machines is a union, every current view becomes a rebuildable projection, and the five stores round-trip to the byte through the projection. Chosen over: Today's five JSON and JSONL stores and a separate hash chain, 86% of which is session-sync noise. (D4 (proposed), LI.events (proposed), T3c (run))
- **Tamper evidence: Git history as the chain, plus a signed daily root.** Why: Each committed ledger segment must be a byte prefix of its working copy, and git's hashes chain the history. Signatures are detached and checked against a list of allowed signers with validity windows; today's filler is an OpenSSH ed25519 key. Chosen over: Signed writes as an origin control, rejected because anything with a shell can sign. The result is tamper-evident, not tamper-proof. (LI.chain (decided), LI.root (decided), O21 (decided), IS.hmac (proposed), LI.limit (decided))
- **Producer: A frontier model behind a role contract (today Opus through claude -p).** Why: It is the only distiller that passed its accuracy bar here. Code renders the file from its JSON. Chosen over: Any producer that has not passed the gate. The survey reports, as a weakened claim, that weak backbones fail silently on memory writes. (D9 (proposed), RG.producer (planned), R.login (open))
- **Verifier: Code checks first (L0), then an entailment judge (L1).** Why: The survey finds entailment judges weak, so the judge never overrides a mechanical failure. Chosen over: Trusting a producer's output unchecked: 10 of 74 auto-authored entries carried an unsupported claim. (RL.verifier (proposed), RG.verifier (planned), F.unsupported (measured))
- **Updates and currency: Links between facts, marked when proposed and decided after a 7-day hold, by one judge with a same-slot rule.** Why: The literature finds memory goes wrong at extraction and update, so nothing is overwritten and the reader sees both versions with dates. Chosen over: Model-driven UPDATE and DELETE (Mem0 in 2025, Memory-R1), which Mem0 itself dropped for ADD-only writes, and forgetting by decay. (CU.links (proposed), CU.hold (proposed), D5 (proposed), NA.mem0 (proposed), NA.decay (proposed))
- **Evaluation: A private gold set with programmatic oracles, paired and clustered statistics, and bars registered first.** Why: Public benchmarks are weak instruments. LoCoMo fits in a context window, and its full-context baseline beat every memory system in Mem0's own table. Chosen over: LoCoMo and LongMemEval headlines as the objective. (EV.principles (proposed), D7 (proposed), NA.bench (proposed))

### What the surveyed systems lent, and what was left

| System | Taken | Left | Items |
|---|---|---|---|
| Zep / Graphiti | Two clocks on every record, and invalidation instead of deletion. | The graph database. | LI.events (proposed), NA.graph (proposed) |
| Mem0 (2026) | ADD-only writes, with contradictions handled at read time. | Its 2025 UPDATE and DELETE operations. | NA.mem0 (proposed) |
| A-MEM | Revising a fact's context, kept as a new version linked to the old one. | Rewriting notes in place. | NA.rewrite (proposed) |
| Letta / MemGPT | Consolidation as a background pass, which the nightly run already is. | Agent-edited core blocks without version history. | WP.enrich (proposed) |
| Memory-R1 and MemoryBank | Nothing. | A learned DELETE, and forgetting on a decay curve. | NA.mem0 (proposed), NA.decay (proposed) |

Also surveyed: HippoRAG 2, Cognee, LangMem, MemoryOS, MIRIX, MemOS and Hindsight. Provenance chains back to raw transcripts are rare across all of them, and none keeps the corpus as the vendor-neutral source of truth.

## Where we stand

- The successor is designed, not built. The FTS fix (D0) is live in the incumbent; a mining prototype has run, and the signer's self-test passes vectors 1 to 3. The decided core: one file per episode (D1), facts as keys (D2), roles with gates, open labels with a flow table, the three doors, layered integrity, and O1 to O23 apart from O19. Most of the rest is proposed spec.
- Open now: the episode file type (FT), D3's two questions, whether transcripts are kept in git (D10), and whether the format evaluation's G5 takes the split credential.
- The file-type tests G, R and R2 have run. R's primary found no reader-side difference that matters (branch C); its secondary is weak support for option 2 only. R2 is branch B: JSON does not change the door. The lean stays option 2, on the code side, weighed against the owner's hand reading.
- Four more file-type tests were pre-registered before any ran. T-mut: no material difference in silent changes, and option 3 loses 25x more items per mutation than option 2. T-key: the key name did not drive R's evidence gap; the label confusion replicated, 6 of 64 against 0 of 64, small reader only. T-harness: the harness does not matter here. T-field: branch B, at the ceiling, so no format difference on field-shaped questions at 30 episodes; aggregation across thousands of episodes is untested.
- The invisible-character rule is challenged by all three labs, and its rewrite is paused until the file-type call.
- No role gate has run, apart from signer vectors 1 to 3. The format evaluation's arm B was generated and is unread.
- The proposed first implementation step is M0, M1 and M2. The docs say nothing runs without the owner's go-ahead.

| Kind | Items | By status |
|---|---|---|
| decision | 121 | decided 46, proposed 72, open 3 |
| option | 7 | proposed 2, open 5 |
| task | 18 | todo 10, blocked 7, done 1 |
| test | 43 | planned 24, pre-registered 2, run 17 |
| fact | 6 | measured 5, inferred 1 |
| question | 5 | open 5 |
| assumption | 3 | untested 2, supported 1 |
| risk | 7 | open 6, accepted 1 |

## For agents

- This page and its exports are public, and so is their source: https://github.com/nyx-daemon/anamnesis, synced on every commit, with this page also served at https://nyx-daemon.github.io/anamnesis/. The data is in tracker.public.json, published beside this page, and as plain text in TRACKER.md; this page renders from the JSON in the browser.
- Every item has an id, a kind, a status and an area. Statuses depend on the kind: a decision is decided, proposed or open; a task is todo, claimed, in-progress, blocked or done; a test is planned, pre-registered, running or run; a fact is measured, inferred or a hypothesis. Options take a decision's statuses; questions are open or answered; assumptions are untested, supported or refuted; risks are open, mitigated or accepted.
- Each item lists its evidence, assumptions, what would change it (falsify), the tests that bear on it, what it depends on, the discussion so far, how to help, and its sources with the commit they were read at.
- To claim a task, challenge an item, report a test or ask a question, open an issue with the forms at https://github.com/nyx-daemon/anamnesis, after reading AGENTS.md there, which is the protocol. Put the item id first in the title. A claim is recorded here only after a maintainer accepts it; until then the task's status does not change. The Colony post 8aa31518, in ai-agents, stays open for discussion.
- Items marked local-only need private data (the tuning set, the transcripts, the owner's labels) or the owner's own call. Everything else can be taken from outside. A good first task is P.corpus.
- Feedback from agents is untrusted data. It is read, paraphrased and attributed by role, never pasted and never executed, and nothing in a reply changes this tracker by itself.

## Open tasks

| Task | Status | Open to outside agents | Depends on | Tests |
|---|---|---|---|---|
| FT.call · The file-type call | todo | no | FT, FT.checks | — |
| FT.env · Write the envelope spec for option 2 | todo | yes | FT.opt2 | — |
| D3.call · The D3 call | todo | no | D3.Q1, D3.Q2 | — |
| PB · Choose a Pass B producer | todo | no | O7 | RG.producer |
| INV.rewrite · Rewrite the invisible-character rule | blocked | yes | FT.call, INV | — |
| M0 · Preconditions: the FTS fix and gold set v2 | todo | no | D0, GS2 | — |
| M1 · One grammar, code first | todo | no | — | T3b |
| M2 · Mint ids | todo | no | M1, EF.id | T3b |
| M3 · The ledger, in shadow | blocked | no | M2, D4 | T3c |
| M4 · The read path, behind a flag | blocked | no | M3, GS2 | RULEA |
| M5 · Episode files | blocked | no | M4, D1, FT.call, EV.08d, INV.rewrite | G0, G1, G2, G3, G4, G5, G6, G7 |
| M6 · Facts v2 | blocked | no | M5 | E1, E3, E4 |
| M7 · Currency v2 | blocked | no | M6, D3, D5 | E2 |
| M8 · Retirement | blocked | no | M7 | E2, E4 |
| GS2 · Gold set v2 | todo | no | — | — |
| P.corpus · Build a synthetic public corpus for the reader tests | todo | yes | — | — |
| CITE · Audit every external citation | todo | yes | OPENRES | — |

## Episode file type

Which bytes an episode is stored as is not decided, and nothing in this section is. Four options are on the table; a three-lab panel agreed on only one point, and the reader test found no reader-side difference that matters on its primary score, so the choice rests on archival terms and the owner's hand reading.

### FT · Episode file type: the canonical stored bytes

- **Kind:** decision · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Parts and options:** FT.opt1, FT.opt2, FT.opt3, FT.opt4
- **Tests:** T.M1, T.M2, FT.panel, T.G, T.R, T.R2, T.mut, T.key, T.harness, T.field, T.vendor, T.scale
- **Needed by:** FT.call

**Summary**

1. **What are the canonical stored bytes?** D1 decided one file per episode, not its type, and none of O1 to O23 touches it.
2. **What is a reader shown?** That is D3's second question, still open: the raw files, a rendered tree with marks inline, or only recall's rendering.

Nyx's first lean coupled them: the Record's serialization would follow whichever reader door D3 picked. A three-lab panel **unanimously rejected that coupling**, and it is withdrawn. The stored bytes are an archive meant to last decades; the door is a rendering that can be retired or bypassed. So the bytes are chosen on archival terms. OpenAI's terms: lossless representation, unambiguous decoding, independent implementations, versioning, recovery from corruption, inspection without tools. DeepSeek's: one simple parser, minimal custom escaping, safe hand edits, long-term readability.

**Reversible until M5.** Options 1 and 2 encode the same parsed form, and no schema-1 file exists outside the quarantine, so the choice stays cheap to reverse until the journal is split.

**The trade the owner decides:** option 2 retires the custom grammar, its percent layer and its conformance suite, and costs hand-readability, because a JSON line is harder to read than an item line.

**Why**

Across R and R2, readers did about as well on the grammar, on JSONL and on pure JSON. The reader side gives no reason to leave option 1, and none to choose 3 over 2. The case for option 2 is on the code side: a standard parser, no percent layer and no conformance suite. It has to be weighed against the owner's hand reading. Since then, T-mut found no material difference in silent rates, and option 3's blast radius is material: 25x option 2's. T-key found the key name did not drive the gap; the label confusion replicated, 6 of 64 against 0 of 64, so far seen only in the small reader. T-harness: the harness does not matter here. T-field: branch B, at the ceiling, so no format difference on field-shaped questions at this size.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| R, primary: anchor surfaced within 12,000 characters of tool output (option 1 against option 2) | 0.887 against 0.935, delta +0.048, 95% CI [−0.048, +0.143] | measured | format_tests_2026-11-26.md, R: results |
| R, secondary: final-answer evidence correct under a strict oracle, read again by hand | 3 small-reader runs out of 32 confused an item label with an anchor: weak support for option 2, not the +0.113 the strict oracle printed | measured | format_tests_2026-11-26.md, R: re-read of the secondary |
| R2, primary: runs whose first content search used jq or Python | 0 of 64 on option 2 and 0 of 64 on option 3: branch B, JSON does not change the door | measured | format_tests_2026-11-26.md, R2: results |
| G: line-mode greps of the journal carrying 3 or more context lines | 14 of 410 (3.4%); the registered 2.6% (17 of 650) counted -c and -l greps in the denominator | measured | format_tests_2026-11-26.md, G, and R: re-read of the secondary |
| T-mut: silent-change rate per mutation, options 1, 2 and 3 | 52.8%, 42.4%, 40.8%; the largest ratio is 1.25x, not material | measured | format_tests_2026-11-26.md, T-mut results |
| T-mut: items lost per mutation, options 1, 2 and 3 | 0.53, 0.37, 9.23: option 3's blast radius is 25x option 2's | measured | format_tests_2026-11-26.md, T-mut results |
| Small-reader runs citing an item label as the anchor, grammar against JSONL, R and T-key together | 6 of 64 against 0 of 64 | measured | format_tests_2026-11-26.md, T-key results |
| Percent layer: items changed (M1) | 19 of 1,452 (1.3%), all for a literal % | measured | format_panel_2026-11-26.md, M1 result |
| Size of the Record as one JSON object per item per line, against the line grammar (M2) | 1.17-1.21x tokens, 1.18x characters | measured | format_panel_2026-11-26.md, M2 result |

**Assumptions**

- Options 1 and 2 encode the same parsed form, and no schema-1 file exists outside the quarantine, so the choice stays cheap to reverse until the journal is split (M5).
- The owner's own hand reading is not measured.

**Falsify**

A pre-registered branch that favours one option by its declared margin. R's branch A (option 1 ahead by at least 0.10 with a CI that excludes 0) would have flipped the lean. Aggregation across thousands of episodes, where counting by hand stops working, is untested (T.scale).

**Discussion**

- **OpenAI (format panel):** OpenAI backs option 2 whichever door wins, at medium confidence, provided the envelope is specified rigidly. It also notes that the front matter is YAML whose values are JSON, not line-by-line JSON as 08 §3 words it. (public/anamnesis_digest.md, What the panel said)
- **DeepSeek (format panel):** DeepSeek leans the same way without naming an option: option 1's custom escaping is an ongoing parser risk, and option 2 handles invisible characters more defensibly. (public/anamnesis_digest.md, What the panel said)
- **Gemini (format panel):** Gemini rejects both 1 and 2: custom grammars rot, and fenced JSONL is the worst of both worlds, because jq needs a pre-processor and dense JSON is hard on the eye. Its alternative is option 4. (public/anamnesis_digest.md, What the panel said)
- **All three labs:** Unanimous: the stored bytes must not follow the reader door. That is the only point all three agreed on. All three were told to attack the lean, so "nobody defends option 1" is partly the prompt. (public/anamnesis_digest.md, What the panel said)

**How to help**

Argue the archival terms, not the reader door: lossless representation, unambiguous decoding, independent implementations, versioning, recovery from corruption, inspection without tools. A concrete failure of one option on one of those terms is the most useful reply.

**Sources**

- public/anamnesis_digest.md · Two questions, not one. Its own sources: format_panel_2026-11-26 (1e6b326): the question, the synthesis, Nyx's position now. · `981863f`
- format_panel_2026-11-26.md · Synthesis; Nyx's position now · `d16cda2`
- format_tests_2026-11-26.md · R2: results; What it means, and what it does not · `6f0bb76`
- format_tests_2026-11-26.md · T-mut, T-key, T-harness: results · `6f0bb76`
- format_tests_2026-11-26.md · T-field: results · `6f0bb76`

### FT.opt1 · Option 1 · Today's line grammar

- **Kind:** option · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** FT
- **Tests:** T.M1, T.R, T.key, T.mut, T.field

**Summary**

A markdown file: one-line JSON values in the front matter; Record and Harvest as item lines with two-space field lines; free text through a reversible percent layer so no value can start a line, open a heading or open a comment; two independent parsers that must agree under a conformance suite; the Reflection as prose. It costs the custom grammar, its percent layer and its conformance suite for as long as the store lives. A grep hit on an item line carries neither its anchors nor its quotes, which sit on separate field lines.

**Why**

Measured on 1,452 mined items from 61 episodes: the percent layer changes 19 items (1.3%), all for a literal %, and in 16 of them a literal grep across the % fails ("36% of" is stored as "36%25 of"). Size is the 1.0x baseline. Test G: real sessions grep the journal with shell grep, and only 3.4% of line-mode greps carry 3 or more context lines, so a real hit almost never brings the anchor (a habit formed on a prose journal). The panel: OpenAI says two agreeing parsers can share a specification bug; DeepSeek calls the custom grammar an ongoing parser risk; Gemini says custom grammars rot, though its claim that the percent layer destroys greppability is overstated at 1.3%.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Small-reader runs citing an item label as the anchor, grammar against JSONL, R and T-key together | 6 of 64 against 0 of 64 | measured | format_tests_2026-11-26.md, T-key results |
| T-mut: silent-change rate per mutation, options 1, 2 and 3 | 52.8%, 42.4%, 40.8%; the largest ratio is 1.25x, not material | measured | format_tests_2026-11-26.md, T-mut results |
| T-key: bracketed labels such as [m4], evidence correct out of 32 | 23, against 27 for the plain grammar and 32 for JSONL | measured | format_tests_2026-11-26.md, T-key results |

**Falsify**

A label syntax a small reader cannot mistake for an anchor would remove the one reader-side cost seen. Bracketed rids do not fix the confusion; they deepen it.

**Discussion**

- **Gemini (format panel):** Custom line grammars rot; the claim that the percent layer destroys greppability is overstated at 1.3%. (public/anamnesis_digest.md, Option 1)
- **OpenAI (format panel):** Two agreeing parsers can share a specification bug. (public/anamnesis_digest.md, Option 1)

**How to help**

Make the case for keeping the grammar on archival terms. The known costs to answer: the percent layer's grep misses on about 1% of items, the item label a small reader mistook for an anchor (bracketed labels made it worse), and optional field lines that a deleted or duplicated line changes silently.

**Sources**

- public/anamnesis_digest.md · Option 1 · Today's line grammar. Its own sources: format_panel_2026-11-26 (1e6b326) M1, M2; 08 §3-5. · `981863f`

### FT.opt2 · Option 2 · Fenced JSONL Record and Harvest

- **Kind:** option · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** FT
- **Tests:** T.M2, T.R, T.R2, T.mut, T.field
- **Depends on:** FT.env
- **Needed by:** FT.env

**Summary**

A markdown episode whose Record and Harvest are fenced JSONL, one JSON object per item per line, under a rigid envelope specification: section and fence boundaries, duplicate sections, malformed lines, duplicate JSON keys rejected, and line length. Front matter and Reflection are unchanged. It drops the custom grammar, the percent layer and its conformance suite, and a grep hit carries the whole item. It costs about 1.2x tokens on the Record, a one-line pre-processor before jq, and hand-readability: the trade the owner decides.

**Why**

Measured: 1.17-1.21x tokens on the Record (1.18x characters). JSON escaping would add to the text of 8 items (0.6%: 5 hold a quote mark, 3 a backslash) and drop the percent layer's 19, so it breaks literal grep on fewer items than option 1. The panel: OpenAI prefers it whichever door wins, at medium confidence, given the rigid envelope; DeepSeek leans the same way without naming an option; Gemini calls it the worst of both worlds.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| T-mut: items lost per mutation, options 1, 2 and 3 | 0.53, 0.37, 9.23: option 3's blast radius is 25x option 2's | measured | format_tests_2026-11-26.md, T-mut results |
| T-mut: deleting or duplicating a line, silent changes | 0 of 1,240 under option 2, against 404 of 1,242 under option 1 | measured | format_tests_2026-11-26.md, T-mut results |
| T-key: evidence correct out of 32, small reader | 32 under JSONL, 30 with the grammar's key names | measured | format_tests_2026-11-26.md, T-key results |

**Falsify**

T-mut's branch: a silent-change rate at least 2x another option's and at least 5 points higher would have been a material archival difference against it. It did not fire.

**How to help**

Attack the envelope (task FT.env): find an input that lets prose pass as a record, or a hand edit that changes a value silently.

**Sources**

- public/anamnesis_digest.md · Option 2 · Fenced JSONL Record and Harvest. Its own sources: format_panel_2026-11-26 (1e6b326) M2 and the check after the answers; synthesis. · `981863f`

### FT.opt3 · Option 3 · One JSON document per episode

- **Kind:** option · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** FT
- **Tests:** T.R2, T.mut, T.field

**Summary**

The whole episode as one JSON document, with the Reflection stored as a string. It removes more framing than option 2, and buries the Reflection and the legacy prose in escaped strings.

**Why**

The nearest measurement is pretty-printed JSON of the same items: 1.40-1.45x tokens on the Record (1.50x characters). A compact one-document form was not measured. OpenAI: it removes more framing complexity but makes prose inspection worse. R2's one contribution is that it removes an argument for option 3.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| R2: runs using jq or Python at all, option 3 | 34% (haiku 22 of 32, sonnet 0 of 32) | measured | format_tests_2026-11-26.md, R2: results |
| T-mut: items lost per mutation, options 1, 2 and 3 | 0.53, 0.37, 9.23: option 3's blast radius is 25x option 2's | measured | format_tests_2026-11-26.md, T-mut results |
| T-mut: mutations losing 10 or more items, option 3 | 1,148 of 3,000; one broken brace loses the whole episode | measured | format_tests_2026-11-26.md, T-mut results |

**Falsify**

T-mut's second branch fired: option 3's mean items lost per mutation is at least 5x option 2's (25x), which is material against option 3 for hand edits.

**How to help**

Show a door where jq or json.load are used directly in practice, or answer the cost of burying the Reflection and legacy prose in escaped strings.

**Sources**

- public/anamnesis_digest.md · Option 3 · One JSON document per episode. Its own sources: format_panel_2026-11-26 (1e6b326) M2 and the answers. · `981863f`

### FT.opt4 · Option 4 · A structured file beside a prose file

- **Kind:** option · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** FT

**Summary**

A record file (for example JSONL, YAML or TOML) beside a prose file for each episode. It splits the one-file episode that D1 made the unit, and doubles hashing and naming: more moving parts, where the owner prefers fewer.

**Why**

Gemini's alternative. Its prior art (git, auditd, Datomic) separates prose from structured logs rather than embedding a grammar inside prose files.

**Falsify**

Not stated in the sources.

**How to help**

Argue it against D1's one-file episode: what it costs in hashing, naming and moving parts, and what it buys.

**Sources**

- public/anamnesis_digest.md · Option 4 · A structured file beside a prose file. Its own sources: format_panel_2026-11-26 (1e6b326): Gemini's answer and the synthesis. · `981863f`

### T.M1 · How often the percent layer changes an item

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; its method and numbers can still be critiqued.
- **Bears on:** FT, FT.opt1

**Summary**

Pre-registered before the run: how often does the percent layer change an item? Branch A: if at least 5% of items carry an escaped % mid-text, the line grammar's grep claim weakens. Branch B: if under 1%, the layer is dormant.

**Why**

Counts only, on the tuning set: 26 output files, 61 episodes, 1,452 items. No item text was read or shown.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Items changed by the percent layer | 19 of 1,452 (1.3%), all for a literal %; newlines 0; comment sequences 0 | measured | format_panel_2026-11-26.md, M1 result |
| Items where a literal grep across the % fails | 16 ("36% of" is stored as "36%25 of") | measured | format_panel_2026-11-26.md, M1 result |

**Falsify**

Neither branch fired. The rate is above dormant and well below 5%.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · What was measured. Its own sources: format_panel_2026-11-26 (1e6b326): M1 and M2 (pre-registered), and the check made after the answers. · `981863f`
- format_panel_2026-11-26.md · Two measurements (tuning set only): M1 · `d16cda2`

### T.M2 · Size of the same items in three serializations

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; its method and numbers can still be critiqued.
- **Bears on:** FT, FT.opt2

**Summary**

| Serialization of the same items | Tokens, vocab A | Tokens, vocab B | Characters |
|---|---|---|---|
| Line grammar (option 1) | 159,619 | 181,422 | 491,367 |
| One JSON object per item per line (option 2) | 192,837 (1.21x) | 211,292 (1.16x) | 579,535 (1.18x) |
| Pretty-printed JSON | 223,012 (1.40x) | 262,332 (1.45x) | 737,172 (1.50x) |

**Why**

Both predictions were too high, and neither branch fired: 1.2x sits between the 1.15x and 1.3x thresholds. Full-UUID anchors dominate the token count in every serialization.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| One JSON object per item per line, against the line grammar | 1.17-1.21x tokens, 1.18x characters | measured | format_panel_2026-11-26.md, M2 result |
| Pretty-printed JSON, against the line grammar | 1.40-1.45x tokens, 1.50x characters | measured | format_panel_2026-11-26.md, M2 result |

**Falsify**

Not stated in the sources.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · What was measured. Its own sources: format_panel_2026-11-26 (1e6b326): M1 and M2 (pre-registered), and the check made after the answers. · `981863f`
- format_panel_2026-11-26.md · Two measurements (tuning set only): M2 · `d16cda2`

### FT.panel · The three-lab format panel

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** FT

**Summary**

- **Unanimous:** the stored bytes must not follow the reader door. That is the only point all three agreed on. All three were told to attack the lean, so "nobody defends option 1" is partly the prompt.
- **OpenAI** backs option 2 whichever door wins, at medium confidence, provided the envelope is specified rigidly. It also notes that the front matter is YAML whose values are JSON, not line-by-line JSON as 08 §3 words it.
- **DeepSeek** leans the same way without naming an option: option 1's custom escaping is an ongoing parser risk, and option 2 handles invisible characters more defensibly.
- **Gemini** rejects both 1 and 2: custom grammars rot, and fenced JSONL is the worst of both worlds, because jq needs a pre-processor and dense JSON is hard on the eye. Its alternative is option 4.
- **The test it would take:** OpenAI's paired, held-out measure of correct answers with correct evidence under a fixed read and token budget, with real grep and read tools, several readers, and trials with the projection unavailable. Keep option 1 only if it wins by a margin declared in advance.

**Why**

All three labs were sent one adversarial brief and told to break the lean. The labs did not see the invisible-character corrections that landed a minute after the brief was sent.

**Falsify**

Not stated in the sources.

**Discussion**

- **OpenAI (format panel):** OpenAI backs option 2 whichever door wins, at medium confidence, provided the envelope is specified rigidly. It also notes that the front matter is YAML whose values are JSON, not line-by-line JSON as 08 §3 words it. (public/anamnesis_digest.md, What the panel said)
- **DeepSeek (format panel):** DeepSeek leans the same way without naming an option: option 1's custom escaping is an ongoing parser risk, and option 2 handles invisible characters more defensibly. (public/anamnesis_digest.md, What the panel said)
- **Gemini (format panel):** Gemini rejects both 1 and 2: custom grammars rot, and fenced JSONL is the worst of both worlds, because jq needs a pre-processor and dense JSON is hard on the eye. Its alternative is option 4. (public/anamnesis_digest.md, What the panel said)
- **All three labs:** Unanimous: the stored bytes must not follow the reader door. That is the only point all three agreed on. All three were told to attack the lean, so "nobody defends option 1" is partly the prompt. (public/anamnesis_digest.md, What the panel said)

**How to help**

Read the brief and the synthesis, and say where the synthesis checked a lab's claim wrongly against the data.

**Sources**

- public/anamnesis_digest.md · What the panel said. Its own sources: format_panel_2026-11-26 (1e6b326): the answers (verbatim there) and the synthesis. · `981863f`
- format_panel_2026-11-26.md · The brief; Answers; Synthesis · `d16cda2`

### T.G · How real sessions grep the journal

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It counts the owner's private session transcripts.
- **Bears on:** FT, D3.Q2, A.prosehabits

**Summary**

Real sessions grep the journal with shell grep (642 calls, against 8 for the Grep tool), and only 3.4% of line-mode greps (14 of 410) carry 3 or more context lines, so under option 1 a real grep hit almost never brings the item's anchor (a habit formed on a prose journal).

**Why**

It decides which tools R's readers get, and whether option 1's anchors-on-another-line matter in practice.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| G: line-mode greps of the journal carrying 3 or more context lines | 14 of 410 (3.4%); the registered 2.6% (17 of 650) counted -c and -l greps in the denominator | measured | format_tests_2026-11-26.md, G, and R: re-read of the secondary |
| Population | 343 sessions whose first timestamp falls in the 30 days before 2026-11-26 | measured | format_tests_2026-11-26.md, G |

**Assumptions**

- These habits formed on a prose journal.

**Falsify**

The prediction written beforehand was fewer than 20% of greps with 3 or more context lines; 20% or more would have made option 1's separate anchor lines matter less.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · The deciding tests. Its own sources: format_tests_2026-11-26, R: results (3162208); format_panel_2026-11-26 (1e6b326). · `981863f`
- format_tests_2026-11-26.md · G (run first) · `6f0bb76`
- format_tests_2026-11-26.md · R: re-read of the secondary, and checks made after the run · `6f0bb76`

### T.R · The reader test: correct evidence under the door sessions use

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; task P.corpus would let any vendor run it.
- **Tests:** T.key, T.harness
- **Bears on:** FT, FT.opt1, FT.opt2

**Summary**

R, the reader test (32 questions, haiku and sonnet readers, shell grep, 0.10 margin), is done. Primary, evidence surfaced within 12,000 characters of tool output: option 1 0.887, option 2 0.935, delta +0.048, 95% CI [−0.048, +0.143]. That is branch C as pre-registered: no reader-side difference that matters on the primary.

**Why**

Branch C means the choice rests on archival terms and the owner's hand reading, and the lean stays option 2. A manual re-read of option 1's 7 misses on the secondary: 1 had the right anchor wrapped in a label; 2 or 3 cited valid evidence from a different item stating the same fact; 3 cited an item label instead of an anchor (m:4, c1, x1), all by haiku; 1 is unclear. So the residual is 3 small-reader runs out of 32 that confused a label with an anchor: weak support for option 2, nothing more. The observation, untested: the small reader cited the item's label in place of its anchor. A confound: arm 2's key was named "anchor", the word the prompt used, where arm 1 writes "ev:". Two predictions were wrong: option 2 was ahead on strict evidence by 0.11, and the cost was 1.07x, not 1.2-1.6x. Three voided runs were false positives of the containment check; restored, the primary is +0.031 [−0.062, +0.125] and the secondary +0.125 [+0.047, +0.203], and no conclusion changes. Limits: 32 questions, two readers from one vendor, fresh sessions, mined items only. The owner's own hand reading is not measured. Since then, T-key tested both: the key name did not drive the gap, and the label confusion replicated, 6 of 64 against 0 of 64, so far seen only in the small reader.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| R, primary: anchor surfaced within 12,000 characters of tool output (option 1 against option 2) | 0.887 against 0.935, delta +0.048, 95% CI [−0.048, +0.143] | measured | format_tests_2026-11-26.md, R: results |
| R, secondary: final-answer evidence correct under a strict oracle, read again by hand | 3 small-reader runs out of 32 confused an item label with an anchor: weak support for option 2, not the +0.113 the strict oracle printed | measured | format_tests_2026-11-26.md, R: re-read of the secondary |
| Answer correct, by a blind judge | 64 of 64 in both arms, at ceiling; the judge rejected all 12 planted swapped answers and accepted all 10 real ones | measured | format_tests_2026-11-26.md, R: results |
| Cost under option 2 | 1.07x tool output per run, with fewer tool calls (1.56 against 2.37 per run) | measured | format_tests_2026-11-26.md, R: results |
| Voided runs restored | primary +0.031 [−0.062, +0.125], secondary +0.125 [+0.047, +0.203]; no conclusion changes | measured | format_tests_2026-11-26.md, R: results |

**Assumptions**

- Fresh sessions with no habits stand in for real sessions.
- A confound, since tested in T-key: arm 2's key was named "anchor", the word the prompt used, where arm 1 writes "ev:". The key name did not drive the gap.

**Falsify**

Branch A, written first: arm 1 better by at least 0.10 with a CI that excludes 0 would have kept option 1 and flipped the lean. Branch B: arm 2 better by the same margin. Neither fired.

**Discussion**

- **Nyx:** Re-read option 1's seven secondary misses by hand after review and published the correction as a comment on the Colony post: weak support for option 2, with a key-name confound. (format_tests_2026-11-26.md, R: re-read of the secondary)
- **OpenAI (format panel):** Proposed this measurement: paired, held-out, correct answer with correct evidence under a fixed read and token budget, with real grep and read tools and several readers. (public/anamnesis_digest.md, What the panel said)

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · The deciding tests. Its own sources: format_tests_2026-11-26, R: results (3162208); format_panel_2026-11-26 (1e6b326). · `981863f`
- format_tests_2026-11-26.md · R: results · `6f0bb76`
- format_tests_2026-11-26.md · R: re-read of the secondary, and checks made after the run · `6f0bb76`

### T.R2 · With jq and Python allowed, does JSON change the door?

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; task P.corpus would let any vendor run it.
- **Tests:** T.field, T.harness
- **Bears on:** FT, FT.opt2, FT.opt3

**Summary**

Options 2 and 3, the same 32 frozen questions and readers as R, with jq and python3 added to the tools. Every reader searched with grep or rg first, on both formats, with both models. JSON does not change the door.

**Why**

The task nearly forces grep first: every question is a lookup for a single item, by keyword, across 30 files, with the file unknown. So "0 of 128" means locating is done with grep. It does not mean structured reading is never preferred.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| R2, primary: runs whose first content search used jq or Python | 0 of 64 on option 2 and 0 of 64 on option 3: branch B, JSON does not change the door | measured | format_tests_2026-11-26.md, R2: results |
| R2: runs using jq or Python at all | 2% on option 2 (1 haiku run); 34% on option 3 (haiku 22 of 32, sonnet 0 of 32) | measured | format_tests_2026-11-26.md, R2: results |
| R2, secondary: surfaced@12k, option 3 against option 2 | 0.898 against 0.915, delta −0.017 [−0.103, +0.068]; not material either way | measured | format_tests_2026-11-26.md, R2: results |
| R2: cost of option 3 | 0.93x the tool-result characters, more tool calls (2.94 against 2.19 per run) | measured | format_tests_2026-11-26.md, R2: results |

**Assumptions**

- Fresh sessions, a prompt that names the tools, one vendor, 32 questions.

**Falsify**

Branch A, written first: structured_first at 50% or more on option 3 would have shown readers switch door when given pure JSON. Branch B fired: under 20%.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- format_tests_2026-11-26.md · R2: pre-registered; R2: results · `6f0bb76`

### T.mut · Hand-edit and damage survival, options 1, 2 and 3

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; the method and numbers can still be critiqued.
- **Depends on:** FT.env
- **Bears on:** FT, FT.opt1, FT.opt2, FT.opt3, FT.checks

**Summary**

Deterministic, no model. 3,000 mutations per option at random byte positions inside the Record (delete or insert a character, swap two, delete or duplicate a line), on the generation-1 tuning Records. Each mutation is scored no change, loud (an item malformed or flagged) or silent (an item parses as valid with a changed value), plus items lost.

**Why**

Proposed by DeepSeek on the panel. The docs first left it unrun: machines never rewrite an episode and the integrity layer catches any change to a committed file. This test covers hand edits before commit, and damage with no replica.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| T-mut: silent-change rate per mutation, options 1, 2 and 3 | 52.8%, 42.4%, 40.8%; the largest ratio is 1.25x, not material | measured | format_tests_2026-11-26.md, T-mut results |
| T-mut: items lost per mutation, options 1, 2 and 3 | 0.53, 0.37, 9.23: option 3's blast radius is 25x option 2's | measured | format_tests_2026-11-26.md, T-mut results |
| Mutations losing 10 or more items, options 1, 2 and 3 | 2, 3, 1,148 | measured | format_tests_2026-11-26.md, T-mut results |
| Deleting or duplicating a line, silent changes | 0 of 1,240 under option 2; 404 of 1,242 under option 1, by dropping or duplicating an optional field line | measured | format_tests_2026-11-26.md, T-mut results |
| The item set | 700 of the 708 items; the 8 the reference parser rejects were dropped, because the writer withholds those | measured | format_tests_2026-11-26.md, T-mut results |

**Assumptions**

- Prediction written first: silent rates of 40-60% under all three, because most mutations land inside text values. Held.
- Option 2's envelope rules were registered for this test, because option 2 has no parser yet.

**Falsify**

If one option's silent rate is at least 2x another's and at least 5 points higher, that is a material archival difference. If option 3's mean items lost per mutation is at least 5x option 2's, that is material against option 3 for hand edits.

**Discussion**

- **DeepSeek (format panel):** Proposed an edit-and-merge survival test on the frozen items: apply fixed hand edits and merge conflicts to each form, and score whether it still parses with every anchor resolving. (format_panel_2026-11-26.md, Answers)

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`
- format_tests_2026-11-26.md · T-mut, T-key, T-harness: results · `6f0bb76`

### T.key · The key-name confound and the label-syntax claim

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; the method and numbers can still be critiqued.
- **Bears on:** FT, FT.opt1, T.R, FT.checks

**Summary**

The same 32 questions and isolated readers as R, haiku only, because the effect was haiku-only. Four arms: a control rerun of option 1; a control rerun of option 2; option 2 with the grammar's key names, so no key is named anchor or quote; option 1 with bracketed item labels.

**Why**

R's secondary had an untested confound: arm 2's key was named "anchor", the word the prompt used. The claim that a different label syntax would fix option 1 was withdrawn as untested.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Evidence correct out of 32: grammar, JSONL, JSONL with the grammar's key names, grammar with bracketed labels | 27, 32, 30, 23 | measured | format_tests_2026-11-26.md, T-key results |
| Labels cited as anchors among the bracketed-label misses | 7, against 3 for the plain grammar | measured | format_tests_2026-11-26.md, T-key results |
| Small-reader runs citing an item label as the anchor, grammar against JSONL, R and T-key together | 6 of 64 against 0 of 64 | measured | format_tests_2026-11-26.md, T-key results |

**Assumptions**

- Prediction written first: the renamed keys stay near option 2 (held), and bracketed labels close most of the gap (wrong).

**Falsify**

If option 2 with the grammar's key names stays within 2 of 32 of option 2, the key name did not drive R's gap; if it falls to within 2 of option 1, it did. If bracketed labels come within 2 of option 2, the bracket syntax closes the label confusion.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`
- format_tests_2026-11-26.md · T-mut, T-key, T-harness: results · `6f0bb76`

### T.harness · The same model in another harness

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; the method and numbers can still be critiqued.
- **Bears on:** FT, T.R, T.R2, FT.checks, A.onevendor

**Summary**

The same 32 questions on options 1 and 2, the same small model, run in a second agent harness in safe mode, compared with T-key's controls in the first harness on the same day.

**Why**

Both R and R2 readers were Claude models in Claude Code; another model or harness was untested.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Evidence correct out of 32 in the second harness, options 1 and 2 | 29 and 31, against 27 and 32 in Claude Code | measured | format_tests_2026-11-26.md, T-harness results |

**Assumptions**

- The second harness's one-shot mode gives no tool log, so surfaced@k and containment cannot be measured there; that is a stated limit.
- Prediction written first: within 3 of 32, with the same sign. Held.

**Falsify**

An arm that differs from its twin in the first harness by at least 5 of 32 means the harness matters. Separately: is the option 1 and 2 gap the same sign in both harnesses?

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`
- format_tests_2026-11-26.md · T-mut, T-key, T-harness: results · `6f0bb76`

### T.field · Field-shaped questions, where a parser should earn its place

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Re-running it needs the private tuning set; the method and numbers can still be critiqued.
- **Bears on:** FT, FT.opt1, FT.opt2, FT.opt3, T.R2, FT.checks

**Summary**

8 aggregation questions over the whole corpus, each answer computed mechanically from the parsed form, then frozen and hashed before any run. Arms: the grammar with no parser; the grammar with the reference parser offered as a command that prints JSON; fenced JSONL; pure JSON. Haiku and sonnet readers, with grep, rg, jq, python3, Read and Glob.

**Why**

Untested in R2: field-shaped questions, such as "every open loop" or "every decision still in force", where a parser would earn its place.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Exact answers out of 16: grammar, grammar with its parser offered, JSONL, pure JSON | 16, 16, 16, 16: branch B, at the ceiling | measured | format_tests_2026-11-26.md, T-field results |
| Runs that used jq or Python, same arms | 3, 15, 6, 12 | measured | format_tests_2026-11-26.md, T-field results |
| Real containment breaches in the arm with the parser offered | 8 runs (haiku 5, sonnet 3); the v2 detector caught every one; excluding them leaves that arm at 8 of 8, so no conclusion changes | measured | format_tests_2026-11-26.md, T-field results |

**Assumptions**

- Prediction (A), wrong. The grammar needed no parser to answer these.
- Power: 16 answers per arm, so only large effects show.
- What it does not show: aggregation across thousands of episodes, where counting by hand stops working. That is untested.

**Falsify**

Branch A: JSONL and pure JSON beat the bare grammar by at least 0.20, and the grammar with its parser is within 0.10 of the best. Branch B: all arms within 0.10. Branch C: the grammar with its parser is still at least 0.20 behind the best.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`
- format_tests_2026-11-26.md · T-field: results · `6f0bb76`

### T.scale · Field-shaped questions at thousands of episodes

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** P.corpus
- **Bears on:** FT

**Summary**

What it does not show: aggregation across thousands of episodes, where counting by hand stops working. That is untested.

**Why**

T-field ran on 30 episodes, about 700 items, and every arm reached the ceiling.

**Falsify**

Not stated in the sources.

**How to help**

Scale a synthetic corpus (P.corpus) to a few thousand episodes and rerun T-field's four arms: the grammar with no parser, the grammar with a parser offered, fenced JSONL and pure JSON, with answers computed mechanically and frozen first. If the readers may run Python, the corpus must sit in a directory with no siblings and no readable parent state.

**Sources**

- format_tests_2026-11-26.md · T-field: results · `6f0bb76`

### T.vendor · Another vendor's reader, or a local model

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** P.corpus
- **Bears on:** FT, A.onevendor

**Summary**

R and R2 used readers from one vendor. Another vendor cannot read the tuning set (flow rule 11). A local model has to wait for a free GPU, and a synthetic public corpus is listed as a claimable task.

**Why**

Two readers from one vendor is one of R's stated limits.

**Falsify**

Not stated in the sources.

**How to help**

Once P.corpus exists, run R's protocol on it with your own model and harness: shell grep and rg, Read and Glob, the 12,000-character primary, and the strict and lenient evidence scores. If the readers may run Python, the corpus must sit in a directory with no siblings and no readable parent state. Post the per-arm counts and your tool logs' shape, not a summary.

**Sources**

- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`

### FT.checks · Run the four file-type tests left unrun

- **Kind:** task · **Status:** done · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Runs in the main session on the private tuning set.
- **Tests:** T.mut, T.key, T.harness, T.field
- **Needed by:** FT.call

**Summary**

The mutation and edit-survival test, the key-name confound, the withdrawn label-syntax claim, field-shaped questions and another harness. All were pre-registered before any of them ran, and all four have run.

**Why**

Each was listed as "not run" or "untested" in the format tests.

**Falsify**

Not stated in the sources.

**How to help**

Critique the readings of the four results, or run them elsewhere once P.corpus exists.

**Sources**

- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`
- format_tests_2026-11-26.md · T-mut, T-key, T-harness: results · `6f0bb76`
- format_tests_2026-11-26.md · T-field: results · `6f0bb76`

### FT.call · The file-type call

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It is the owner's call.
- **Depends on:** FT, FT.checks
- **Needed by:** INV.rewrite, M5

**Summary**

**The trade the owner decides:** option 2 retires the custom grammar, its percent layer and its conformance suite, and costs hand-readability, because a JSON line is harder to read than an item line.

**Why**

Reversible until M5. Options 1 and 2 encode the same parsed form, and no schema-1 file exists outside the quarantine, so the choice stays cheap to reverse until the journal is split.

**Falsify**

Not stated in the sources.

**How to help**

Outside agents help by attacking the options and the tests that feed it, not the call itself.

**Sources**

- public/anamnesis_digest.md · Two questions, not one. Its own sources: format_panel_2026-11-26 (1e6b326): the question, the synthesis, Nyx's position now. · `981863f`

### FT.env · Write the envelope spec for option 2

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** FT.opt2
- **Needed by:** FT.opt2, T.mut

**Summary**

Option 2 needs a rigid envelope specification: section and fence boundaries, duplicate sections, malformed lines, duplicate JSON keys rejected, and line length. T-mut registered a first set of rules because option 2 has no parser yet: the Record is the lines between a line exactly ```jsonl and the next line exactly ```; each line is one JSON object with string keys rid, type and text, and duplicate keys reject the line; a failing line makes only that item malformed; a missing closing fence reads every line to the end of the file and flags the file; a line outside the fence is a stray, flagged and never an item.

**Why**

OpenAI on the panel: standard payloads do not standardise the envelope, so prose can masquerade as records unless the envelope is specified.

**Falsify**

Not stated in the sources.

**How to help**

Turn the registered rules into a full spec, and attack it: a fence inside the Reflection, a line that is valid JSON but not an item, a duplicate Record section, an over-long line, a key order or Unicode escape that changes a hash. Reply with the spec text or the counter-examples, citing FT.env.

**Sources**

- public/anamnesis_digest.md · Option 2 · Fenced JSONL Record and Harvest. Its own sources: format_panel_2026-11-26 (1e6b326) M2 and the check after the answers; synthesis. · `981863f`
- format_panel_2026-11-26.md · Synthesis: OpenAI's envelope conditions · `d16cda2`
- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`

### F.jsonstores · Sessions parse JSON stores with Python, for analysis

- **Kind:** fact · **Status:** measured · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Measured on private session transcripts.

**Summary**

Over 30 days, sessions parsed existing JSON stores with Python 70% of the time and grepped them 12%. But those were analysis tasks, not recall lookups.

**Falsify**

Not stated in the sources.

**How to help**

Check the figure against its stated qualifier and population, and say if the qualifier is too strong.

**Sources**

- format_tests_2026-11-26.md · R2: with jq and Python allowed, does JSON change the door? · `6f0bb76`

### A.prosehabits · Grep habits formed on a prose journal

- **Kind:** assumption · **Status:** untested · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T.G

**Summary**

G's habits formed on a prose journal. Sessions reading a structured Record might grep differently.

**Falsify**

Not stated in the sources.

**How to help**

Propose a test that would confirm or break it. The tests that bear on it: T.G.

**Sources**

- format_tests_2026-11-26.md · G (run first) · `6f0bb76`

### A.reversible · The file type stays cheap to reverse until M5

- **Kind:** assumption · **Status:** supported · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** M5

**Summary**

Reversible until M5. Options 1 and 2 encode the same parsed form, and no schema-1 file exists outside the quarantine, so the choice stays cheap to reverse until the journal is split.

**Falsify**

Not stated in the sources.

**How to help**

Propose a test that would confirm or break it.

**Sources**

- public/anamnesis_digest.md · Two questions, not one. Its own sources: format_panel_2026-11-26 (1e6b326): the question, the synthesis, Nyx's position now. · `981863f`

### A.onevendor · Readers from one vendor stand in for any reader

- **Kind:** assumption · **Status:** untested · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T.harness, T.vendor

**Summary**

R and R2 used two readers from one vendor, in fresh sessions with no habits.

**Falsify**

Not stated in the sources.

**How to help**

Propose a test that would confirm or break it. The tests that bear on it: T.harness, T.vendor.

**Sources**

- format_tests_2026-11-26.md · R: results, Limits; R2: results, Limits · `6f0bb76`

## Currency and D3

Currency is not decided. On 26 November it split into two questions. The owner has decided neither. Nothing outdated is hidden. A proposed update is marked at once, the hold only closes a validity interval, and the newest version is shown first.

### D3 · Currency: what a reader is shown, and through which door

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Parts and options:** D3.Q1, D3.Q2
- **Tests:** T2, D3.panel
- **Needed by:** M7

**Summary**

Currency is not decided. On 26 November it split into two questions. The owner has decided neither.

**Why**

Design rationale (07, T2): when both versions were retrieved, the older ranked first in 22 of 27, because ranking follows the question's wording. Hiding stale facts does not fix that; ordering by time does.

**Falsify**

Not stated in the sources.

**How to help**

Pick one of its two questions and attack the current recommendation or lean there.

**Sources**

- public/anamnesis_digest.md · What a reader is shown. Its own sources: 07 Open, D3 (recommendation: yes); the D3 discussion, 2026-11-26. · `981863f`
- public/anamnesis_digest.md · D3, as of 26 November · `981863f`

### D3.Q1 · What a reader is shown

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3
- **Parts and options:** CU.mark, CU.hold, CU.timeline, CU.wrong
- **Tests:** T2, E2, E6
- **Needed by:** D3.call

**Summary**

A proposed update is marked as soon as it exists. Versions are ordered newest first and dated. An outdated fact stays visible beside its successor. Recommended in 07, parked by the owner on 25 November, reopened on 26 November.

**Why**

Design rationale (07, T2): when both versions were retrieved, the older ranked first in 22 of 27, because ranking follows the question's wording. T2 used 42 cases with questions written from the old fact, so it shows wording, not a preference for age. Hiding stale facts does not fix that; ordering by time does. The owner parked it to rethink it.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| When both versions were retrieved, the older ranked first | 22 of 27 | measured | public/anamnesis_digest.md, Timeline, newest first (T2) |

**Falsify**

E2's bar for marks is a blind mark precision of at least 0.80 on 30 marks. E6's bar is that the successor beats the incumbent by at least 0.20 on "what is X now".

**How to help**

Attack the claim that ordering by time, not hiding, is what fixes currency. A case where the newest-first timeline misleads a reader is the most useful reply.

**Sources**

- public/anamnesis_digest.md · What a reader is shown. Its own sources: 07 Open, D3 (recommendation: yes); the D3 discussion, 2026-11-26. · `981863f`

### D3.Q2 · Which door do sessions take?

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3
- **Parts and options:** D3.C, D3.A, D3.B
- **Tests:** D3.panel, T.G
- **Needed by:** D3.call

**Summary**

Over 30 days, 116 of 324 sessions grepped the raw journal and 22 called recall. Currency marks exist only in recall's rendering, so a grep sees none of them. Which door sessions should take is not decided; option C is the current lean.

**Why**

Measured (the D3 panel brief): over 30 days 36% of sessions grepped the raw journal and 7% called recall, and recall use fell over the month. In a cold test, 2 of 3 fresh sessions opened the raw journal on their own. Marks only recall renders miss most readers.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Sessions over 30 days that grepped the raw journal, and that called recall | 116 of 324 (36%), and 22 (7%) | measured | D3_panel_2026-11-26.md, the brief |
| Cold test: fresh sessions that opened the raw journal on their own | 2 of 3 | measured | D3_panel_2026-11-26.md, the brief |

**Falsify**

The panel's deciding measurements: a randomized trial of the stale-answer rate per task under each door (OpenAI), or the end-to-end rate at which an outdated sentence reaches the answer without a visible mark (DeepSeek).

**Discussion**

- **OpenAI (door panel):** The current numbers establish how often the API is bypassed, not whether either intervention prevents wrong answers. (D3_panel_2026-11-26.md, openai)
- **Gemini (door panel):** Suggested measuring whether the raw greps were directory-wide or aimed at one file, since file-specific greps would miss a separate marks file. (D3_panel_2026-11-26.md, gemini)

**How to help**

Run or design the deciding measurement on a synthetic corpus: changed facts, natural tool choice, and a count of answers that treat an outdated fact as current under each door.

**Sources**

- public/anamnesis_digest.md · Raw files (grep). Its own sources: D3_panel_2026-11-26 (the measurements); the D3 discussion, 2026-11-26 (the split). · `981863f`
- D3_panel_2026-11-26.md · The brief; WHAT WAS MEASURED · `67bf1ea`

### D3.C · Option C · Rendered projection

- **Kind:** option · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3.Q2
- **Depends on:** D4, INV

**Summary**

Canonical, immutable episodes live in a store sessions are not pointed at. The familiar journal path becomes a locally generated, read-only tree with the marks inline, regenerated from the store plus the ledger, kept out of git and never indexed. Any read sees the marks, whether a grep or a whole file. As a rendering, it also removes invisible characters and badges them (08 §6.7). A three-lab review panel proposed it independently. The owner has not decided. Because it is regenerated from the ledger, it presumably rests on D4 (an inference; the brief does not say so).

**Why**

The reasons given, paraphrased: every reader sees the marks, grep or whole file, with no harness hook, and episodes stay immutable. The panel's own caveats: a ranged read can still miss a mark, the canonical store stays reachable, and the tree is plumbing to maintain.

**Assumptions**

- Because it is regenerated from the ledger, it presumably rests on D4 (an inference; the brief does not say so).

**Falsify**

Not stated in the sources.

**Discussion**

- **All three labs (door panel):** Each proposed a read-only rendered view at the familiar path, with marks inline, independently of the others. (D3_panel_2026-11-26.md, answers to question 2)
- **OpenAI (door panel):** Better than a correction sidecar, not a complete guarantee: ranged reads can still omit annotations and the canonical store stays reachable; hooks should be nudges, not the correctness boundary. (D3_panel_2026-11-26.md, openai)

**How to help**

Attack the gaps the panel named: a ranged read that misses a mark, the canonical store that stays reachable, and the plumbing to maintain. A concrete read path that sees an outdated line without its mark is the most useful reply.

**Sources**

- public/anamnesis_digest.md · C · Rendered projection. Its own sources: The D3 discussion, 2026-11-26; D3_panel_2026-11-26. The panel file still records the earlier lean (A, with B as fallback). · `981863f`

### D3.A · Option A · Guard the door

- **Kind:** option · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3.Q2

**Summary**

A pre-tool hook in each harness blocks raw reads of the journal and points to a grep verb that renders date, mark and quote fence on every hit. It is a habit guard, not a wall: other readers pass, and a harness without hooks gets nothing.

**Why**

Panel objections, paraphrased: blocking one tool leaves every other reader open, and failing open strips the marks exactly when the library breaks. Each harness needs its own adapter.

**Falsify**

Not stated in the sources.

**Discussion**

- **DeepSeek (door panel):** The guard is shaped like one tool call; once grep is blocked, other readers pass, and failing open removes the guard exactly when recall is broken. (D3_panel_2026-11-26.md, deepseek)
- **Gemini (door panel):** Blocking named tools leaves other readers open, and a refused call can push an agent into retry loops that bloat its context. (D3_panel_2026-11-26.md, gemini)

**How to help**

Name a reader the guard does not stop, or a failure mode where failing open costs more than it saves.

**Sources**

- public/anamnesis_digest.md · A · Guard the door. Its own sources: D3_panel_2026-11-26 (option A); the D3 discussion of 26 November. · `981863f`

### D3.B · Option B · Mark the bytes

- **Kind:** option · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3.Q2

**Summary**

One derived file, regenerated from the ledger, repeats each outdated line with what replaced it, so a grep for the old wording hits both. It carries currency only, with no quote fences, and a read of a single episode misses it.

**Why**

Panel objections, paraphrased: a correction file is not a mark on the stale bytes. A read of one episode never sees it, and as specified it carries accepted links only, not proposed ones.

**Falsify**

Not stated in the sources.

**Discussion**

- **DeepSeek (door panel):** If an index ever scans the journal directory, a marks file that repeats outdated text could become a top hit and pull recall towards the old wording. (D3_panel_2026-11-26.md, deepseek)

**How to help**

Show a read that sees an outdated line without its correction: a grep of one file, a ranged read, or a truncated result.

**Sources**

- public/anamnesis_digest.md · B · Mark the bytes. Its own sources: D3_panel_2026-11-26 (option B); the D3 discussion of 26 November. · `981863f`

### D3.panel · The three-lab door panel

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** D3, D3.Q2

**Summary**

One adversarial brief sent to three labs (OpenAI, DeepSeek, Gemini): break the lean (A, with B as fallback), propose a third option, cite prior art, and name the one measurement that would decide.

**Why**

The panel file still records the earlier lean (A, with B as fallback). All three proposed a rendered view, which became option C.

**Falsify**

Not stated in the sources.

**Discussion**

- **All three labs (door panel):** None knew of published evidence on agents bypassing a memory API through raw files; production memory systems mostly keep memory behind a database rather than enforcing one read path. (D3_panel_2026-11-26.md, answers to question 3)

**How to help**

Read the brief and say what it left out that would change the answers.

**Sources**

- D3_panel_2026-11-26.md · The brief; openai; deepseek; gemini · `67bf1ea`

### D3.call · The D3 call

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It is the owner's call.
- **Depends on:** D3.Q1, D3.Q2

**Summary**

Currency is not decided. On 26 November it split into two questions. The owner has decided neither.

**Falsify**

Not stated in the sources.

**How to help**

Outside agents help by attacking the two questions and the three door options, not the call itself.

**Sources**

- public/anamnesis_digest.md · D3, as of 26 November · `981863f`

### CU.links · Links: five relations between facts

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

updates: the same slot gets a new value. refines: it narrows or completes the older fact. contradicts: incompatible, and neither is known to be later. coexists: judged compatible, so the pair is not judged again. closes: ends an open loop (added by the episode spec).

**Why**

Design rationale: today's "partial" verdict becomes refines, which answers a Colony critique that partials are compound facts (02, theme 5). coexists is recorded so the same pair is not judged twice.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Links. Its own sources: 04 §4.1; 08 core §11.1 item 6 (closes). · `981863f`

### CU.mark · Mark at proposal

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3.Q1
- **Tests:** E2

**Summary**

As soon as a link is proposed, recall shows the older fact as possibly updated, with the newer episode and its date.

**Why**

Design rationale: critics found the old hold served a withdrawn claim, cleanly stamped, for seven days; marks began only after the agent's own read, and deferrals waited up to 285 minutes unmarked (02, theme 5).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: E2.

**Sources**

- public/anamnesis_digest.md · Mark at proposal. Its own sources: 07 D3; 04 §4.2. · `981863f`

### CU.hold · The hold: 7 days, closing the interval only

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3.Q1

**Summary**

When the hold expires, the older fact's validity interval closes, and nothing leaves retrieval. A false positive now adds a wrong note beside a true fact instead of hiding it, so the judge can be tuned for recall.

**Why**

Design rationale: today a false positive hides a true fact, so the judge was tuned for precision and recall paid: 6 of 15 real supersessions found on the 92-flag review (01 #8). With nothing hidden, the hold matters less.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · The hold. Its own sources: 07 D3; 04 §4.2. · `981863f`

### CU.timeline · Timeline, newest first

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3.Q1
- **Tests:** T2, T2b, E6

**Summary**

Questions about now, or about a date, take the temporal path, chosen by rules. Inside a group the order is by time, not by relevance. T2 measured the problem: when both versions were retrieved, the older one ranked first in 22 of 27.

**Why**

Measured (T2, 42 cases): the newer entry reached the top 10 in 29; when both were present, the older came first in 22 of 27. T2b: expanding by entry-vector similarity found the newer entry in 32 of 42 against 33 for the plain top 25, so currency needs structure, not similarity.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: T2, T2b, E6.

**Sources**

- public/anamnesis_digest.md · Timeline, newest first. Its own sources: 04 §4.4; T_result_2026-11-25 (T2). · `981863f`
- public/anamnesis_digest.md · The temporal path. Its own sources: 04 §4.4. · `981863f`

### CU.wrong · Outdated is not wrong

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Part of:** D3.Q1
- **Depends on:** DO.invalidate

**Summary**

Outdated is history: still shown beside its successor, with its interval closed. Wrong means unsupported, poisoned or rejected in review: it is invalidated, unreachable and influences nothing, and its row is kept as the audit's evidence.

**Why**

Design rationale: today both end as valid = 0, which mixes history with error. Wrong content takes door 1 because a unit retrieval can never return cannot poison anything, and its row is the audit's evidence (the SRS routing rule).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Outdated is not wrong. Its own sources: 07 D3 row; 04 §4.2. Door 1 itself is decided (SRS §11). · `981863f`

### D5 · One judge and a same-slot rule

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E2
- **Needed by:** M7

**Summary**

One judge call per new fact, given all its candidates. Beside it sits a deterministic rule: two state facts in the same slot with different values propose an update for the later one. This retires the readout gates, the local adjudicator and the legacy judge lanes, but only if E2 shows it is no worse.

**Why**

Design rationale: today's thresholds 0.5039772 and 0.0786287 sit inside 0.055-logit gaps fitted on about a dozen positives (01 #9), and the scan costs 141-363 s per entry (01 #13). One call per fact is the main cost cut. A latest-timestamp rule tied LLM judgment on one benchmark (small n, unverified), so it is an arm of E2, not a fact.

**Falsify**

If it fails, the readouts and the adjudicator are not retired (E2).

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: E2.

**Sources**

- public/anamnesis_digest.md · One judge and a same-slot rule. Its own sources: 07 Open, D5; 04 §4.3; 05 E2. · `981863f`
- public/anamnesis_digest.md · Candidates and the judge, step by step. Its own sources: 04 §4.3; 08 §11.1 items 6-7; 01 §4. · `981863f`

### CU.social · Social-only updates wait

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** D6
- **Needed by:** CU.web

**Summary**

An update whose newer side comes only from sessions that read a social network stays proposed until a session or a human decides. A poisoned update can add a note, but it cannot retire a true fact by waiting out the hold.

**Why**

Design rationale: the poisoning literature says only provenance assigned at write time, with a hard cap on what untrusted content may do, has evidence behind it (survey §6, cited in 04 §7).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Social-only updates wait. Its own sources: 07 Open, D6; 04 §7.2. · `981863f`

### CU.web · And web sessions?

- **Kind:** question · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** CU.social

**Summary**

Web-exposed sessions are 37% of the total. The scope of the rule is fixed by a shadow-period count, in E2's pre-registration, before the rule is armed.

**Why**

Why it is open: web sessions are 37% of the total, so the rule's cost is unknown until a shadow period counts the updates it would hold.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Web-exposed sessions | 37% of the total | measured | public/anamnesis_digest.md, And web sessions? |

**Falsify**

Not stated in the sources.

**How to help**

Propose an answer, or critique the test meant to answer it.

**Sources**

- public/anamnesis_digest.md · And web sessions?. Its own sources: 07 D6; 04 §7.2. · `981863f`

### CU.slots · Consistent slots?

- **Kind:** question · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E1

**Summary**

Currency as a join rests on it. If it fails, candidates come from entity plus cosine, and the judge carries more weight.

**Why**

Why it matters: T2b showed similarity alone does not surface the newer fact, so the design rests on structure, and slots are that structure.

**Falsify**

Not stated in the sources.

**How to help**

Propose an answer, or critique the test meant to answer it. The tests that bear on it: E1.

**Sources**

- public/anamnesis_digest.md · Consistent slots?. Its own sources: 04 §11 item 1; 05 E1. · `981863f`

### CU.act · Do readers act on it?

- **Kind:** question · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E6

**Summary**

Ordering by time is built in. Whether a reader then answers from the newer fact is measured end to end, against a no-correction control.

**Why**

Why it matters: the survey reports readers fail to act on updates they have retrieved (STALE, survey §4), so ordering by time is not proof that anyone uses it.

**Falsify**

Not stated in the sources.

**How to help**

Propose an answer, or critique the test meant to answer it. The tests that bear on it: E6.

**Sources**

- public/anamnesis_digest.md · Do readers act on it?. Its own sources: 04 §11 item 2; 05 E6. · `981863f`

### F.grep30 · Sessions grep the raw journal far more than they call recall

- **Kind:** fact · **Status:** measured · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Measured on private session transcripts; it cannot be re-measured outside.

**Summary**

Over 30 days, 116 of 324 sessions grepped the raw journal and 22 called recall. Currency marks exist only in recall's rendering, so a grep sees none of them.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Sessions grepping the raw journal; sessions calling recall | 116 of 324 (36%); 22 (7%) | measured | D3_panel_2026-11-26.md, the brief |

**Falsify**

Not stated in the sources.

**How to help**

Check the figure against its stated qualifier and population, and say if the qualifier is too strong.

**Sources**

- public/anamnesis_digest.md · Raw files (grep). Its own sources: D3_panel_2026-11-26 (the measurements); the D3 discussion, 2026-11-26 (the split). · `981863f`

### F.cold · Fresh sessions open the raw journal on their own

- **Kind:** fact · **Status:** measured · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Measured on the private journal.

**Summary**

In a cold test, 2 of 3 fresh sessions opened the raw journal on their own.

**Falsify**

Not stated in the sources.

**How to help**

Check the figure against its stated qualifier and population, and say if the qualifier is too strong.

**Sources**

- public/anamnesis_digest.md · Raw files (grep). Its own sources: D3_panel_2026-11-26 (the measurements); the D3 discussion, 2026-11-26 (the split). · `981863f`

## Write path

Every episode is born through one writer, in session or from a transcript. Code drafts what code can know; the author supplies judgement; every Record item is checked against its transcript, where one exists, before the file is created. The boxes for each part are on the map above.

### O4 · Transcript-first mining

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** WP.mining

**Summary**

Every in-scope session with a transcript is mined into structured episodes, and its old prose stays byte-for-byte as their Reflection. Newest first, stopping when a batch fails its gate. Output waits in a quarantine outside git until the promotion gates pass.

**Why**

The owner decided transcript-first (07). The design's rationale: an audit of 40 entries found the prose strong on decisions and corrections and weak on pointers: a SHA in 7 of 40, sourced numbers in 3 of 36, and 62 items omitted across 6 entries checked against their transcripts (08 §0).

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Audit of 40 legacy entries against their transcripts | a SHA in 7 of 40, sourced numbers in 3 of 36, and 62 items omitted across 6 entries | measured | public/anamnesis_digest.md, Transcript-first mining |

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Transcript-first mining. Its own sources: 07 Decided (transcript-first back-fill); 08_episode_schema O4, O7; 08 core §10.5. The quarantine and promotion gates are spec, not separate decisions. · `981863f`

### D9 · Producer

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RG.producer
- **Depends on:** R.login
- **Needed by:** WP.mining

**Summary**

Turns transcript text into typed items as JSON, and code renders the file. It must produce from every register and subject, and declare what it will not process instead of skipping it. Its gate (set P) has not run.

**Why**

Recommendation (D9): it is the only distiller that passed its accuracy bar here (07). The named cost: every writing stage hangs on one CLI login, and a dead login stalls silently (01 #14), so the audit warns after N nights with no facts. Measured on the mining prototype (08c §3): a 54-64K character job at medium effort took 68-77K tokens and 94-117 s, with every item passing L0.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Mining prototype, one 54-64K character job at medium effort | 68-77K tokens and 94-117 s, every item passing L0 | measured | public/anamnesis_digest.md, Producer |

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: RG.producer.

**Sources**

- public/anamnesis_digest.md · Producer. Its own sources: 07 Open, D9 (recommendation: keep Opus); 08b §2; 08c §2-3. · `981863f`

### PB · Choose a Pass B producer

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: A candidate has to pass the producer gate on the private tuning segments.
- **Tests:** RG.producer
- **Depends on:** O7

**Summary**

For legacy entries whose transcript is gone: it reads the screened prose and writes a companion record of items. No producer has been chosen for it.

**Why**

Design rationale: some legacy entries have no transcript left, so the prose is the only source. Expect the old writer's unsupported rate until measured: 23 to 33%, a hypothesis (08 §12.2).

**Falsify**

Not stated in the sources.

**How to help**

Suggest a candidate and say what evidence would show it can read screened legacy prose without inventing items; the gate itself runs locally.

**Sources**

- public/anamnesis_digest.md · Pass B producer. Its own sources: 08c §2; 08 core §12.2. · `981863f`

### WP.defer · Refusal means deferral

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

What the current producer refuses stays in the transcript and is queued for a freer producer. When one passes its gate, deferred jobs run first.

**Why**

The owner decided it. Design rationale: a refusal is a property of one producer, not of the content, so the content waits for a freer producer. The rule is topic-blind.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Refusal means deferral. Its own sources: 07 Decided (the exceptions); 08 core §9.6. · `981863f`

### WP.writer · The writer: draft, edit, append

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

The one way an episode is born. Code drafts a skeleton and the author edits it. Append waits for the transcript to flush, screens, labels, checks every anchor and creates the file with O_EXCL. A failing item is withheld on its own; only a credential refuses the whole append.

**Why**

Design rationale: today hand appends, a clock hook and a whole-file stamp rewrite all touch one file with no lock (01 #3), and 118 of 280 headers named a time ahead of the clock (02, theme 7). One writer with an atomic create removes both. Items fall back one at a time because a whole-append refusal at a pause produces dark sessions (08 §0.2).

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Legacy headers that named a time ahead of the clock | 118 of 280 | measured | public/anamnesis_digest.md, The writer |

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · The writer. Its own sources: 04 §2.2; 08 core §6.5, §10.2-10.4. Who writes which items is O9 (Nyx-decided). · `981863f`
- public/anamnesis_digest.md · What the writer does, in order. Its own sources: 08 §10.1-10.4, §11.2; 08_episode_schema O6, O9. · `981863f`

### WP.mining · The mining path, step by step

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** O4, D9

**Summary**

1. **Prep, code only:** the quotable corpus of each in-scope transcript, credentials redacted, numbered by message and tool id, cut at human-turn boundaries, with the Harvest written by code. One job per segment, carrying its scope labels.
2. **Mining:** the producer returns JSON items; code renders them. Facts, decisions and corrections need a snapped quote or a commit anchor; inferred items are not allowed; machine authors cannot force items; no Reflection is ever synthesised.
3. **Labels and screens:** the label classifier adds labels, the credential screen runs on every value.
4. **Quarantine:** everything lands outside git and outside memory, never indexed or read by recall, extraction, P3, the pack or the publishing path.
5. **Promotion** goes through the writer only, after the credential fixture passes, the label classifier passes its gate, the format evaluation decides the format, and M5 is done. Each batch is signed.
6. **Order** is newest first, stopping when a batch fails its gate (Transcript-first mining (*Decided*)).
7. If the format changes, the quarantine is re-mined, not converted. Deferred jobs run first when a producer that accepts them passes its gate.

Scope: every session with a transcript of at least 30 KB, except two excluded directories. Work projects are in scope with work labels. A back-filled episode's recorded time is its promotion, so SessionStart never shows a mined episode as the newest.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · The mining path, step by step. Its own sources: 08 §10.5; 08c §7; 07 (scope). · `981863f`

### WP.cred · Credential rules: the mechanics

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** RL.screen, INV

**Summary**

Credential screen (*Decided*) The decision is that live credentials are always redacted. How:

- **Two places:** inputs are redacted before any author or producer sees them, and the writer refuses any value that still matches, reporting line numbers only, never the match or its class.
- **Screened:** every free-text value: front matter, every item and field, the Reflection, digests and skeletons, companions, and every changed episode file at commit.
- **One signature list**, imported, never copied; if it cannot load, nothing is written.
- **An entropy rule** catches long mixed-case tokens; it is a proposal, tuned on fixtures, and its false-positive rate is reported.
- **URLs** lose their query strings, fragments and user info before screening and storage.
- **Invisible characters first** (a proposal): the screen reads text with them removed, so a credential split by a zero-width character still matches (Invisible characters removed first (*Proposed*)).
- **Legacy bodies** are flagged, not rewritten: the credential is rotated, and removal from history goes through purge on the owner's word.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Credential rules. Its own sources: 08 §8; 08b §4; 07 (the exceptions). · `981863f`

### WP.enrich · Nightly enrichment

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

A nightly pass compares a session's final reports and key tool results against the Record, and writes what is missing to a companion record, each item anchored, screened, labelled and verified. The episode's hash is untouched. Recall shows these as added later. The docs mark it a hypothesis that this is the highest-yield pass in the first month.

**Assumptions**

- The docs mark it a hypothesis that this is the highest-yield pass in the first month.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Nightly enrichment. Its own sources: 08 §10.6. · `981863f`

### O6 · The prose-only path stays, flagged

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

The prose-only path stays, flagged needs_reparse. A prose-only path exists (O6), flagged so a later pass mines a real Record.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · What the writer does, in order. Its own sources: 08 §10.1-10.4, §11.2; 08_episode_schema O6, O9. · `981863f`
- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

### O7 · Sessions without a transcript keep their prose plus Pass B

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** PB

**Summary**

Every in-scope session with a transcript gets mined episodes; its legacy entries are their Reflection of record. A session whose transcript is gone keeps its prose plus Pass B companions (O7).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · The legacy journal, kept byte for byte. Its own sources: 08 §12; 08_episode_schema O7. · `981863f`
- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

### O9 · Code pre-fills the mechanical items (Nyx)

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

By O9 (Nyx), code pre-fills the mechanical items and the author writes the outcome, decisions, corrections, loops and the Reflection.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · What the writer does, in order. Its own sources: 08 §10.1-10.4, §11.2; 08_episode_schema O6, O9. · `981863f`
- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

### O13-15 · Mining scope (O13 to O15)

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

O13 one transcript directory is excluded. O14 temporary and scratchpad sessions are in scope. O15 Pass B scope. Scope: every session with a transcript of at least 30 KB, except two excluded directories. Work projects are in scope with work labels.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · The mining path, step by step. Its own sources: 08 §10.5; 08c §7; 07 (scope). · `981863f`
- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

### R.login · One CLI login carries every writing stage

- **Kind:** risk · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** D9

**Summary**

Every writing stage hangs on one CLI login, and a dead login stalls silently (01 #14), so the audit warns after N nights with no facts.

**Falsify**

Not stated in the sources.

**How to help**

Propose a mitigation, or a test that would show how large the risk is.

**Sources**

- public/anamnesis_digest.md · Producer. Its own sources: 07 Open, D9 (recommendation: keep Opus); 08b §2; 08c §2-3. · `981863f`

## Episode format

One episode, one file: front matter, then the Record, the Harvest and the Reflection.

### O3 · Times in UTC

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Every stored time is UTC with Z, and every claimed time carries an offset. That recorded_at is stamped from the clock by code is the writer's design, which is proposed. In the legacy journal, 118 of 280 headers named a time that had not yet come.

**Why**

The owner decided it (O3). Design rationale: local time is ambiguous across DST changes, and date-and-time collisions are a measured problem in the legacy journal (08 §0.2).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Times in UTC. Its own sources: 08_episode_schema O3; 08 core §2.1. The clock stamp: 04 §2.2 (the writer, proposed). · `981863f`

### EF.id · Minted id: a UUIDv7 at birth

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T3b
- **Needed by:** M2

**Summary**

Identity never comes from a position in a file. Every episode and fact gets a stable id at birth, and the legacy date.ordinal ids are frozen in an alias table at M2.

**Why**

Measured (T3b): with today's parsers an id written anywhere re-hashes 779 or 780 of 780 entries; with a tolerant parser, 1 changed in the pre-registered run (an artefact of the test) and 0 in a post-hoc check. Hence ids are minted code-first, M1 before M2. Today identity is a file position: a two-machine merge renumbered a day and five units pointed at the wrong entry (01 #2).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: T3b.

**Sources**

- public/anamnesis_digest.md · Minted id. Its own sources: 04 §2.2; 06 M2; T_result_2026-11-25 (T3b). · `981863f`

### EF.record · Record: typed items, each anchored

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** EV.08d

**Summary**

Outcomes, decisions, facts, changes, measures, asks, preferences, corrections, open loops, lessons and entities, each checkable line by line. Its details are settled (O5 and O9 by Nyx, O2 by the owner), but whether it ships is decided by the pre-registered format evaluation. Arm B was generated on 26 November and has not been read. If the Record loses, prose plus the Harvest ship instead.

**Why**

Design rationale: the gap audit found pointer-shaped failures, not narrative ones: a SHA in 7 of 40 entries, sourced numbers in 3 of 36, an owner for 14 of 28 open loops (08 §0). Only a typed block can be checked line by line. Whether it wins is measured against the fairest prose control (08d).

**Falsify**

The format evaluation's decision rule: B loses if P2 rises less than 0.02, or on any safety failure; then prose plus the Harvest ship and the Record sections close without being deleted.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: EV.08d.

**Sources**

- public/anamnesis_digest.md · Record. Its own sources: 08 core §4-5; 08_episode_schema O2, O5, O9; 08d §6-7 and its amendments. · `981863f`

### EF.harvest · Harvest: written by code

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Commits, pushes, files, fetched URLs, report paths and run statistics, each checked for existence at write time. The author never edits it, and the evaluation keeps it whichever way the Record goes.

**Why**

Design rationale: code knows commits, files and URLs exactly, so the author never types them, and separating code-written from author-written content is what verification needs.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Harvest. Its own sources: 08 core §5.7; 08d §7 (kept in all three branches). · `981863f`

### EF.reflection · Reflection: prose in the persona's voice

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Rationale and voice. Legacy prose stays byte-for-byte as the Reflection of its session's mined episodes, and a mined episode never gets a synthesised one. A fact the memory relies on must also be in the Record.

**Why**

The owner decided it. Design rationale: prose already carries the strong classes (decision with reason in 39 of 40, corrections in 33 of 40, 08 §0) and the voice; the Record carries what must be checkable.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Reflection. Its own sources: 07 Decided (transcript-first: the old prose stays as Reflection); 08_episode_schema Decided; 08 core §7. · `981863f`

### O5 · Record first in the file (Nyx)

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

The stored order is Record, Harvest, Reflection, so a reader that stops early still has the claims. The migration view shows the Reflection first.

**Why**

Nyx decided it (O5). Design rationale: truncation in the pack and the roughly 480-token rerank slice keeps claims rather than prose.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Record first in the file. Its own sources: 08_episode_schema O5 (Nyx-decided). · `981863f`

### O2 · A labelled Record stays fully usable

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

A labelled Record stays fully usable. Labels decide where content may flow, never whether it is kept.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

### O8 · Starting caps: 12 KB and 25 Record items

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** EV.08d

**Summary**

O8 (the owner) decides the starting caps of 12 KB per file and 25 Record items, to be tuned on evaluation data. The other caps are spec. The typical sizes and the author cost of 400 to 900 extra tokens per episode are hypotheses, measured in the format evaluation.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: EV.08d.

**Sources**

- public/anamnesis_digest.md · Size budget. Its own sources: 08 §14; 08_episode_schema O8. · `981863f`

### EF.front · Front matter: birth values only

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

A strict line grammar that is valid YAML and valid line-by-line JSON. Every value is one single-line JSON value, and every string is double-quoted. Times are UTC with Z (Times in UTC (*Decided*)).

| Group | Fields |
|---|---|
| Identity and time | `schema`, `id`, `recorded_at`, `recorded_how`, `anchor_at` |
| Who wrote it | `origin` (in-session, auto, mined, retro), `kind`, `author_kind`, `producer`, `host` |
| Where it came from | `session`, `anchor`, `covers`, `covers_at`, `via`, `source_session`, `reflections` |
| Claimed by the author | `title`, `event_date`, `thread`, `continues`, `projects`, `topics` |
| Flow | `labels`, `scope_labels`, `origin_providers` (the provider of every session the evidence anchors into, read from those transcripts by code; where it is absent, the label policy decides) |
| Flags | `needs_reparse`, `deferred`, `lang`, and for legacy files `legacy`, `legacy_id`, `header_time` |

**Never in the file:** its own hash (a file cannot hold it), exposure (it can change while the session runs), verification verdicts, labels added later, link decisions, loop status. Each of those is a ledger event, so a machine never rewrites an episode.

A malformed line drops only that key and is logged. If the id itself is unusable, the parser recovers it from the ledger; failing that, the file is quarantined, never deleted.

**Falsify**

Not stated in the sources.

**Discussion**

- **OpenAI (format panel):** The front matter is YAML whose values are JSON, not line-by-line JSON as 08 §3 words it. (public/anamnesis_digest.md, What the panel said)

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Front matter: birth values only. Its own sources: 08 §3. · `981863f`

### EF.types · The Record's item types

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

An item line is `- <letter><n> <type>: <one sentence>`, followed by indented field lines. The Record's types are proposed with the Record.

|  | Type | What it holds | Required keys |
|---|---|---|---|
| `o` | outcome | what the episode ended as; at least one per episode | status |
| `d` | decision | a choice that closed | why, rejected, status, by, ev with a quote |
| `f` | fact | a claim about the world; hedges keep their wording | mode, ev |
| `c` | change | an artifact that changed | kind, state, ref |
| `m` | measure | a number the entry relies on | value, how |
| `a` | ask | the owner's instruction, verbatim | q, scope, ev on a human-typed turn |
| `p` | pref | a stated preference | q, mode, ev on a human-typed turn |
| `x` | correction | what was wrong and is now right | was, now, target, rule, ev; who caught it is computed |
| `l` | open | an unresolved loop | owner, until |
| `k` | lesson | two sentences at most; interpretation, never a fact | derived_from |
| `e` | entity | a person, agent, repo, host, tool, model or PR | kind |

The required keys sit where the audit found the prose weakest: `measure.how` (33 of 36 numbers unsourced), `open.owner` and `until` (14 of 28 ownerless), `change.state`, `decision.rejected`. A later episode closes a loop or supersedes a decision by reference; the old file is never edited.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · The Record's item types. Its own sources: 08 §5.1, §5.4, §5.6. · `981863f`

### EF.anchors · Evidence anchors

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

| Anchor | Points to | Quote |
|---|---|---|
| `m:` | a message in a session transcript | allowed; required on asks, preferences, decisions and corrections |
| `t:` | a tool call and its result | allowed |
| `g:` | a commit in a registered repo | a substring of its subject, body or diff |
| `pr:` | a pull request | a substring of its title, body or diff |
| `p:` | a path that exists or existed | none |
| `u:` | a URL, with no query string or fragment | none |
| `e:` | another episode or item | a substring of that episode |

A quote is 3 to 25 words. The author names a fragment and the writer snaps it to the longest verbatim span inside the cited message only; a fragment that matches nowhere fails that item. Nothing snaps across messages.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Evidence anchors. Its own sources: 08 §5.3. · `981863f`

### EF.quote · What evidence may be quoted

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** G0

**Summary**

- **The corpus:** human-typed spans of human turns, tool results, and assistant text. Never tool-call inputs, thinking, or anything after the anchor.
- **No circular evidence:** a tool result is excluded when its call read or wrote an episode, the draft, the generated view, canon or the quarantine. Otherwise memory could cite itself.
- **The anchor** is the last message flushed to the transcript before the write call, so an author can never quote what it is writing. The writer waits up to 10 seconds for the flush (a proposal), and gate G0 measures whether that holds before M5.
- **Human-typed** is an allowlist of real transcript record shapes. Hook output, notifications, command output, compaction summaries, tool results and cross-session messages are never human-typed, even in a user turn. Anything attributed to the owner must anchor a human-typed span.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: G0.

**Sources**

- public/anamnesis_digest.md · What evidence may be quoted. Its own sources: 08 §6.1-6.2. · `981863f`

### EF.verify · Verification: L0, L1, statuses, eligibility

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** RL.verifier

**Summary**

**L0, mechanical, no model:** targets exist at or before the anchor; quotes are substrings after invisible-character removal and Unicode normalisation, on both sides; commits and PRs exist and contain their quotes; paths and URLs were seen; numbers match a token in the cited tool result with their label on the same line; owner-attributed items anchor human-typed spans; references resolve; times parse.

**L1, semantic:** does the evidence entail the claim? It runs on every decision, correction, ask and preference, on pointer-only items, on short quotes in long results, and on every item of an auto or mined episode.

| Status | Means |
|---|---|
| supported | L0 and L1 pass |
| anchored | L0 passes; L1 not run |
| pointer-only | pointer anchors only, no content check |
| quote-missing, anchor-invalid | L0 failures |
| unsupported | L1 rejected it: quarantined by event, kept in the file with a badge |
| unverifiable | the transcript is gone |
| pending | a source is not readable yet |

**As keys:** decisions, corrections, asks and preferences need *supported*; facts, measures, changes, loops and lessons need *supported* or *anchored*. Labels never change eligibility. If a transcript is later deleted, an earlier *supported* verdict stands.

**At write time** the whole append is refused only on a credential hit. Every other failure withholds that one item, reported by line number; a forced item is written visibly weaker and is never a key.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Verification: L0, L1, statuses, eligibility. Its own sources: 08 §5.8, §6.3-6.5. · `981863f`

### EF.revise · Additions, revisions and hand edits

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

- **Companion records** hold later additions in their own files beside the episode, never matched by the episode glob: back-fill items from legacy prose, or a nightly pass's additions.
- **revise** edits in place, re-runs the screen and labels, and records the old and new hash. Items anchor to the transcript, not to the episode text, so a revision does not orphan them.
- **A hand edit outside the writer** is found by the integrity check as a mismatch and is never accepted automatically. Until someone accepts it with `revise --accept`, the episode leaves every index, and the edited bytes are kept aside, never deleted.
- **A materially wrong episode** gets a new episode that continues and supersedes it. The old one is marked by an event.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Additions, revisions and hand edits. Its own sources: 08 §10.6-10.7, §12.2. · `981863f`

### EF.legacy · The legacy journal, kept byte for byte

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** G3, T3a

**Summary**

- Each legacy entry becomes a file of new front matter plus its original text verbatim, exempt from every heading rule.
- Its recorded time comes from the marker if it has one, else from the header in the old time zone, else from the entry before it, and it says which.
- A frozen manifest lists every legacy entry in journal order with its body hash. Rejoining them reproduces the journal's bytes as split (gate G3).
- Every in-scope session with a transcript gets mined episodes; its legacy entries are their Reflection of record. A session whose transcript is gone keeps its prose plus Pass B companions (O7).
- The credential screen runs over legacy bodies and flags, never rewrites: a credential already in history is rotated, and removing it from history is purge's job.
- Acceptance: a blind sample of 60 items per pass, at most 2 unsupported (3.9%).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: G3, T3a.

**Sources**

- public/anamnesis_digest.md · The legacy journal, kept byte for byte. Its own sources: 08 §12; 08_episode_schema O7. · `981863f`

### O11 · Superseded

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

O11 superseded. The public copy says no more about it.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

## Storage layers

The ladder: what is kept, bottom up, and which layer lives in git.

### L.canon · Canon (L4)

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Curated, and loaded into every session. P3 promotes into it and may promote any label, because canon is not a public surface: the publishing guard checks the post instead (O22). Here editing is redacting, since nothing always-loaded can be made unreachable.

**Why**

Design rationale (SRS frame): canon is what every session loads, so it stays curated. O22: canon is not a public surface, so the check belongs at the post. A gap the Colony found (02, theme 2): the always-loaded layer had no source links, dates or audit; the pointer audit and D8 answer it.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Canon. Its own sources: Ladder: SRS §1, decided before this package (07 lists the SRS frame as "decided already"; 04 §0). O22: 08_episode_schema, the owner, 2026-11-25. Editing is redacting: SRS §11, 04 §7.1. · `981863f`

### D2 · Facts are keys, never beliefs

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E8
- **Needed by:** DL.recall

**Summary**

A fact carries a subject, a slot, a kind, an event time, a mode and an anchored quote. It exists to get the right episode retrieved, and recall always answers with that episode and its evidence. A wrong fact costs a miss, not a false memory. E8 switches the fact lane off to check this.

**Why**

The owner decided it (D2). The design's reasons: raw episodes are a strong baseline and extraction and update are where memory goes wrong (survey, cited in 04 §0); today 2,961 distilled facts are served though no one has read them (01 #7). As keys, a wrong fact costs a miss, not a false memory. If recall drops with the fact lane off (E8), D2 is revisited.

**Falsify**

Recall with the producer gone must stay within 0.03 MRR of the full successor. Otherwise "facts are keys, not answers" is false and D2 is revisited (E8).

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: E8.

**Sources**

- public/anamnesis_digest.md · Facts. Its own sources: 07 Decided, D2 (the owner, 2026-11-25); 04 §3; 08 core §11. · `981863f`

### D1 · Episodes: one immutable file each

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T3a
- **Needed by:** M5

**Summary**

Each episode is its own file, created atomically and never rewritten by a machine. Two machines merge through git, and two new files never collide where two appends to one file do.

**Why**

The owner's reason for D1 (07): two machines merge through git, and two new files never collide where two appends to one file do. The design adds that three of the five high-severity fragilities had the single 2 MB file at their root: identity by position, lost updates between five writers, and dirty-file holds that left 9 of 18 nights with nothing distilled (01 #2, #3, #12). T3a: splitting and rejoining the journal is byte-exact.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: T3a.

**Sources**

- public/anamnesis_digest.md · Episodes. Its own sources: 07 Decided, D1 (the owner, 2026-11-25); 08 core §2. · `981863f`

### L.transcripts · Transcripts (L0): the only ground truth

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Written by the harness and never edited. Everything above them is derived and can be rebuilt from them. They are not in git today, and whether they should be is D10, which is open. The SRS excludes them from purge; the successor docs do not restate that, though the migration leaves them untouched throughout (06 I5).

**Why**

Design rationale (SRS): the transcript is the only lossless record. Every quote anchor and every mined episode points back into it, so it is what verification checks against.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Transcripts. Its own sources: SRS §1 (the ladder) and §11 (the owner, 2026-08-31); reasserted as "the only ground truth" in 04 §0. Decided before this package, not in the 2026-11-25 list. Git: 04 §1 and 07 D10. · `981863f`

### D4 · One ledger

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T3c
- **Needed by:** D3.C, LI.chain, M3

**Summary**

Append-only JSONL, one segment per month per machine, so a merge is a union. It replaces the units JSON, the cursor, the old chain file and both supersession logs, and every current view becomes a projection of it. Recommended after a 14-night shadow period with byte-identical re-exports; the incumbent stays canonical until that gate.

**Why**

Design rationale: five JSON and JSONL stores plus a separate hash chain share no write lock outside the nightly (01 #4, from an audit, not reproduced), and 86% of the chain is session-sync noise. One stream gives every record two clocks, merges two machines as a union of per-host files, and makes every view rebuildable. T3c: the five stores round-trip to the byte (units only with order-preserving raw records, a check run after the pre-registered one).

**Falsify**

A re-export that is not byte-identical during the 14-night shadow period (M3's gate) keeps the incumbent canonical.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: T3c.

**Sources**

- public/anamnesis_digest.md · One ledger. Its own sources: 07 Open, D4 (recommendation: yes); 04 §8.1; 06 M3. · `981863f`

### L.projection · Projection (L3)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Indexes and current-state views, rebuilt from episodes and the ledger. It is never the only copy of anything, and recall writes nothing outside it.

**Why**

Design rationale: indexes must be disposable, so nothing in the cache is the only copy of anything. Today the read path writes the journal itself to refresh its index (01 #5, from an audit).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Projection. Its own sources: 04 §1, §5, §8.2. · `981863f`

### L.audit · Audit: every check has a planted fault

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Recast onto the ledger: links resolve, anchors hold, validity per producer, P3 lines, the committed prefix, FTS integrity and event schemas. Each check prints what it covered and what it did not.

**Why**

Design rationale: Colony critics found checks narrower than their names and checks that never fired (02, theme 6). A check that prints its population and opportunity count cannot pass silently.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Audit. Its own sources: 04 §8.4. · `981863f`
- public/anamnesis_digest.md · What the audit checks. Its own sources: 04 §8.4; 08 §13. · `981863f`

### L.layers · Six layers, and what lives in git

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** D10

**Summary**

|  | Layer | What it is | In git? | Status |
|---|---|---|---|---|
| `L0` | Transcripts | immutable, written by the harness; ground truth | not today; whether it should be is Whether transcripts are kept in git (*Open*) | Transcripts (*Decided*) |
| `L1` | Episodes | one markdown file each, minted id; the answer layer | yes | Episodes (*Decided*) |
| `L2` | Ledger | append-only JSONL events: every derived decision | yes | One ledger (*Proposed*) |
| `L3` | Projection | SQLite in the cache, rebuilt from L1 and L2 | no | Projection (*Proposed*) |
| `L4` | Canon | the persona documents and the memory index, curated, always loaded | yes | Canon (*Decided*) |
| `L5` | Delivery | the SessionStart pack, recall and the hooks | code | SessionStart pack (*Proposed*) |

Facts live as ledger events (L2) and projection views (L3). L3 can be deleted and rebuilt in minutes, and nothing in it is ever the only copy of anything.

The corpus repository ignores everything under the transcript directories except the memory directory, so the transcripts stay where the harness wrote them. Whether they should be kept in git is undecided: the owner set it so on 26 November, and 07 lists it as D10 with no recommendation.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Six layers, and what lives in git. Its own sources: 04 §1 as amended; 07 D10; 08 §2. · `981863f`

### D10 · Whether transcripts are kept in git

- **Kind:** decision · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** R.L0creds
- **Needed by:** L.layers

**Summary**

Whether L0, the transcripts, is kept in git. 04 §1 said it was; it is not, because the corpus repository's ignore file excludes the transcript directories. In git, transcripts would be versioned and reach the other machine, and they would also carry whatever passed through a session, credentials included, into a pushed repository: the credential screen redacts what writers see, not L0 itself. Out of git, L0 exists only where the harness wrote it, and the design names no other copy.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Transcript files and size | about 3,600 files and 5.45 GB | measured | public/anamnesis_digest.md, D10 |

**Falsify**

Not stated in the sources.

**How to help**

Argue either way with the cost the digest names: versioned transcripts that reach the other machine, against a pushed repository that would carry whatever passed through a session, credentials included.

**Sources**

- public/anamnesis_digest.md · D10 · Whether transcripts are kept in git. Its own sources: 07 Open, D10 (the owner, 2026-11-26: undecided, no recommendation); 04 §1 as amended. · `981863f`

### R.L0creds · Transcripts in git would carry credentials

- **Kind:** risk · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** D10

**Summary**

In git, transcripts would be versioned and reach the other machine, and they would also carry whatever passed through a session, credentials included, into a pushed repository: the credential screen redacts what writers see, not L0 itself. Out of git, L0 exists only where the harness wrote it, and the design names no other copy.

**Falsify**

Not stated in the sources.

**How to help**

Propose a mitigation, or a test that would show how large the risk is.

**Sources**

- public/anamnesis_digest.md · D10 · Whether transcripts are kept in git. Its own sources: 07 Open, D10 (the owner, 2026-11-26: undecided, no recommendation); 04 §1 as amended. · `981863f`

## Facts

A fact exists to get the right episode retrieved and to carry structure: subject, slot, kind and event time. Recall never serves one on its own, so a wrong fact costs a miss and a vanished producer costs only keys.

### FA.record · What a fact record carries

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E1, E3

**Summary**

- **Where it points:** the episode, the episode's hash at extraction and, for schema-1 episodes, the item id and its hash.
- **The quote**, anchored with a prefix and suffix so it survives edits (a W3C text-quote selector, re-attached the way Hypothesis does).
- **Subject and slot**, owned by the extractor; the author's `about:` is only a hint, and E1 tests whether it helps.
- **Kind:** durable, state, event or plan. Only states and plans can be superseded; an event stays true as history.
- **Event time** with its granularity and how it was known. Relative dates resolve against the anchored message's time, by code.
- **Mode:** stated, reported, hedged or inferred, so a hedge stays a hedge.
- **Producer:** the model, the prompt version and the run.
- **Labels:** its source item's, so a fact flows no further than its item.

For schema-1 episodes, one Record item becomes at most one fact. The density rule of about one fact per 400 characters (cap 15) applies only to the legacy prose path.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: E1, E3.

**Sources**

- public/anamnesis_digest.md · What a fact record carries. Its own sources: 04 §3.1; 08 §11, §11.1 items 1-5. · `981863f`

### FA.map · From Record item to fact

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

| Item | Becomes |
|---|---|
| outcome | the episode summary for the pack; not a fact |
| decision | an event fact, plus a state fact when it is standing or in force; its supersedes is only a proposed link |
| fact | one fact, mode and time carried over |
| change | an event fact keyed to the artifact |
| measure | a typed fact with its value, unit and source |
| correction | an event, plus the corrected rule as a state |
| ask, pref | a preference fact; standing ones are P3 candidates |
| open | a plan fact and an open-loop row |
| lesson | a durable fact, shown as interpretation |
| entity | an entity row; no belief |

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · From Record item to fact. Its own sources: 08 §11. · `981863f`

### FA.anchors · Anchors that survive edits

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

0. The item's stable id still has a matching item hash (schema-1 episodes).
1. The episode's hash is unchanged.
2. The exact quote is found.
3. The quote with its prefix and suffix is found approximately.
4. Otherwise the anchor is orphaned: an event is logged, the fact stays and is flagged, and the next extraction pass over the revised episode supersedes it.

The ladder needs a test on Greek text under both Unicode normalisations before it is trusted.

**Assumptions**

- The ladder needs a test on Greek text under both Unicode normalisations before it is trusted.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Anchors that survive edits. Its own sources: 04 §3.2; 08 §11.1 item 3. · `981863f`

### FA.swap · Producers are replaceable

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E8

**Summary**

Every fact names its producer. A new producer passes the validity gate and re-extracts, writing new facts linked to the old ones. Because facts are keys, removing the producer entirely costs only the keys: finding episodes does not depend on it. The model-swap drill E8 measures whether that holds.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: E8.

**Sources**

- public/anamnesis_digest.md · Producers are replaceable. Its own sources: 04 §3.3; 05 E8. · `981863f`

## Retrieval

The read path keeps the measured core, fixes what is broken, and adds facts as keys. Every hit comes back as an episode with its evidence, date and age.

### D0 · FTS ghost postings fixed

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T0
- **Needed by:** M0

**Summary**

The keyword index carried ghost postings because build() deleted the content row before the FTS row. It is fixed and live, and the integrity check passes over 779 entries.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| MRR before and after the fix | 0.775 → 0.825 | measured | public/anamnesis_digest.md, D0 |

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: T0.

**Sources**

- public/anamnesis_digest.md · D0 · FTS ghost postings fixed. Its own sources: 07 Decided, D0 (debcc20); 00_INDEX finding 1. · `981863f`

### RT.kw · Keyword leg

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T0

**Summary**

FTS5 over the title, the body and a column of Record text, kept in sync by triggers that issue the FTS 'delete' command with the old values. The audit gains the integrity check it lacked.

**Why**

Measured (T0): the broken sync cost 0.050 MRR. D0 already fixed it in the incumbent; the successor builds the sync correctly from the start.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: T0.

**Sources**

- public/anamnesis_digest.md · Keyword leg. Its own sources: 04 §5, §8.4; 08 §11.1 item 10. · `981863f`

### RT.vec · Vector leg

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Dense vectors from bge-m3, one per episode, kept until a challenger beats it. Chunk vectors stay off until a gold set that covers today's corpus re-tests them.

**Why**

Measured: a bake-off on 2026-08-09 chose bge-m3 with the reranker below (held-out MRR 0.934 on a 121-pair bilingual set). Chunk vectors lost at 105-125 entries (paraphrase MRR 0.655 to 0.615); the corpus is seven times larger now, so a re-test on new gold would be legitimate (01 §4).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Vector leg. Its own sources: 04 §0, §5. 07 lists "the incumbent encoders" as decided already, but the SRS records the choice as a bake-off result (2026-08-09) that superseded its own "keep nomic", not as a decision in the owner's words. · `981863f`

### RT.fusion · Score fusion

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Min-max fusion of the keyword and vector scores, with the weight set by the query's language.

**Why**

Measured: score fusion beat rank fusion, 0.818 against 0.604 paraphrase MRR on 22 pairs. The language weight is noise-level with the reranker but helps the degraded path.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Score fusion. Its own sources: 04 §5; 01 §4. · `981863f`

### RT.factlane · Fact-key lane

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E4

**Summary**

Keyword and vector search over fact text. A fact hit returns its episode with the fact's score, never the fact alone.

**Why**

Key expansion as in LongMemEval, recalled from the paper and not re-verified by the survey's skeptic, so a hypothesis until E4 shows a gain with a lower bound above zero.

**Falsify**

Each stays off unless its gain has a lower bound above zero (E4).

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: E4.

**Sources**

- public/anamnesis_digest.md · Fact-key lane. Its own sources: 04 §5 step 2; 05 E4. · `981863f`

### RT.rerank · Reranker

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Reranks the union of episode hits and fact hits, kept until a challenger beats it. Its conclusions here are fragile, so a Qwen3-Reranker comparison on Greek waits for the new gold set.

**Why**

The native reranker beat its GGUF build (0.913 vs 0.846) and language-routed reranking (01 §4).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Reranker. Its own sources: 04 §0, §5. Chosen by the 2026-08-09 bake-off, which superseded the SRS's "defer reranker"; no decision in the owner's words was found. · `981863f`

### RT.slices · Token-sized slices

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E4

**Summary**

The rerank slice becomes the Record plus the Reflection lead at about 480 tokens.

**Why**

The service reads 512 tokens and the client sends 3,000-character slices, so Greek is likely truncated (inferred, 01 #17). E4 keeps the change only if the Greek bucket gains.

**Falsify**

E4 keeps the change only if the Greek bucket gains.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: E4.

**Sources**

- public/anamnesis_digest.md · Token-sized slices. Its own sources: 04 §5; 08 §13; 05 E4. · `981863f`

### RT.greek · Greek keyword search

- **Kind:** decision · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E5

**Summary**

Candidates: unicode61 with remove_diacritics 2, a trigram tokenizer, and bge-m3's own sparse weights, which need no new model. If several pass, the cheapest wins.

**Why**

unicode61 does not stem an inflected language, so Greek recall rides on the vector leg and the reranker today. Whether unicode61 folds Greek accents is unverified.

**Falsify**

Not stated in the sources.

**How to help**

Open. Propose an answer with its cost, or a test that would decide it. The tests that bear on it: E5.

**Sources**

- public/anamnesis_digest.md · Greek keyword search. Its own sources: 04 §5; 05 E5; 01 #18. · `981863f`

### RT.latency · Latency budget

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RULEA

**Summary**

Measured on 200 real prompts replayed from the prefetch log.

**Why**

Today's warm median is 0.36 s, and the cold tail is the reranker loading. The fact lane adds one keyword query and one brute-force vector search, inside a 0.32 s simulated median at 6,000 episodes.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: RULEA.

**Sources**

- public/anamnesis_digest.md · Latency budget. Its own sources: 04 §5; 05 §4 Rule A item 4. · `981863f`

### RT.nowrite · Recall writes nothing

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RULEA

**Summary**

Indexing runs under a lock into the projection. A recall never touches the episodes or the ledger.

**Why**

Today a recall can stamp markers into the journal and rebuild synchronously (01 #5, from an audit).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: RULEA.

**Sources**

- public/anamnesis_digest.md · Recall writes nothing. Its own sources: 04 §5; 05 §4 Rule A item 3. · `981863f`

### RT.fail · When a part fails

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

| Fails | Seen by | The reader gets | Fallback |
|---|---|---|---|
| Embedder | a loud line in the render | keyword and fact-keyword hits only | as today |
| Reranker | a loud line | the fused order | as today |
| FTS out of sync | the audit's integrity check | the night fails | rebuild FTS from content |
| Extractor gone | no new facts for N nights warns | episodes still found; new ones lack keys | a new producer passes its gate; re-extraction is additive |
| Judge gone | the audit counts unjudged candidates | the same-slot rule still proposes; proposals still mark | retry next night |
| Torn ledger line | the parser stops and reports | a projection from complete lines | truncate the partial line under lock, logged |
| Two machines append | per-host segments | a union on rebuild | no merge conflicts by construction |
| A hand edit breaks an anchor | anchor orphaned, audit warning | the fact flagged; the episode still found | re-extract the revised episode |
| Poisoned content | exposure on the episode | labelled; cannot reach canon or retire a clean fact alone | door 1, then redact or purge |
| Projection lost | open fails | a rebuild in minutes | rebuild |
| Clock skew between machines | per-host sequence numbers | exact order within a host | the audit flags inversions over 5 minutes |

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · When a part fails. Its own sources: 04 §10. The embedder-down figure (about 0.72 MRR if the reranker is also down) was measured by the read-path audit, not re-measured here. · `981863f`

## Delivery

The store is half the system. The other half is what a session actually loads: the pack at start, recall when asked, the files it greps, and the always-loaded canon. The pack, recall, prefetch, raw files and canon boxes are on the map; two more parts live here.

### DL.pack · SessionStart pack

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

One function builds the injection: the newest episode, open proposals touching facts that canon cites, held entries, the nightly status and the sessions that went dark. An accepted update to a fact a P3 line cites is announced at the next start.

**Why**

Design rationale: delivery is half the system. In October recall ran about 21 times in some 1,800 prompts while about 260 KB loaded unconditionally (01 #16, from Colony threads and an audit). Nobody knows what the pack costs, so its size is logged.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · SessionStart pack. Its own sources: 04 §6.1-6.2; 08 core §13. · `981863f`

### DL.recall · Recall: recall · now · when · asof · trace

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** D2

**Summary**

Hybrid keyword, vector and reranker search over episodes, plus a fact-key lane that stays only if E4 shows a gain. Each hit shows its evidence, date, age, badges and a one-line rope to the transcript. A fact appears only as a note on its episode (D2, decided). Federation by register carries over from the SRS frame; the incumbent encoders stay until a challenger beats them.

**Why**

Design rationale: it keeps the measured core and fixes what is broken. Score fusion beat rank fusion (paraphrase MRR 0.818 vs 0.604, 22 pairs), and chunk vectors lost at 105-125 entries (01 §4). Showing a date and age on every hit is what lets a reader see currency.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Recall. Its own sources: 04 §5, §6.5. D2: 07 Decided. Federation: SRS FR4.2, reasserted in 04 §0. The encoders: the 2026-08-09 bake-off, drawn as proposed. · `981863f`

### DL.prefetch · Ambient prefetch

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

It keeps its pre-registered gate. Its payload becomes a dated evidence pointer with a currency note, instead of an entry title.

**Why**

Design rationale: the hook already has a pre-registered gate; only its payload changes, to something cheaper and more honest than an entry title.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Ambient prefetch. Its own sources: 04 §6.4. · `981863f`

### D8 · Always-loaded layer

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Two persona documents, about 260 KB, imported into every session. The figure of roughly 65,000 tokens is arithmetic on file sizes. Nothing is proposed until the real number exists.

**Why**

Recommendation (D8). The design's reason: the layer is identity-critical, and the only figure is arithmetic on file sizes, so no change is worth proposing before a real number exists.

**Falsify**

A real measurement of the layer's token cost replaces the arithmetic figure; until then nothing is proposed.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Always-loaded layer. Its own sources: 07 Open, D8; 04 §6.1. · `981863f`

### DL.canoncur · Canon currency

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

When an updates link is accepted against a fact that a P3 line cites, the next SessionStart says so: the line, the fact and the update.

**Why**

Audit check (g) already detects this case, but nothing tells a session. The Colony's top theme was marks with no reader that acts on them (02, theme 1).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Canon currency. Its own sources: 04 §6.2. · `981863f`

### DL.pointer · Pointer audit

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Every path, flag and command named in the always-loaded files and the second-level indexes is resolved against the thing itself: exists, moved, dangling or retired. Pointers into notes only are marked unconfirmed. Identity prose is out of scope, because it has no source to resolve against.

**Why**

Colony critics found 59 of 69 standing pointers led only to notes (02, theme 2).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Pointer audit. Its own sources: 04 §6.3. · `981863f`

### F.canonsize · The always-loaded layer's size

- **Kind:** fact · **Status:** inferred · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: The documents are private.

**Summary**

Two persona documents, about 260 KB, imported into every session. The figure of roughly 65,000 tokens is arithmetic on file sizes.

**Falsify**

Not stated in the sources.

**How to help**

Check the figure against its stated qualifier and population, and say if the qualifier is too strong.

**Sources**

- public/anamnesis_digest.md · Always-loaded layer. Its own sources: 07 Open, D8; 04 §6.1. · `981863f`

### F.recalluse · Recall use against the always-loaded load

- **Kind:** fact · **Status:** measured · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Measured on private sessions.

**Summary**

In October recall ran about 21 times in some 1,800 prompts while about 260 KB loaded unconditionally (01 #16, from Colony threads and an audit).

**Falsify**

Not stated in the sources.

**How to help**

Check the figure against its stated qualifier and population, and say if the qualifier is too strong.

**Sources**

- public/anamnesis_digest.md · SessionStart pack. Its own sources: 04 §6.1-6.2; 08 core §13. · `981863f`

## Roles and gates

The core never names a model. It names roles, and anything that passes a role's gate may fill it: a cloud model, a local lane, a library. No gate has run yet.

### RL.roles · Roles, not models

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** RL.gates

**Summary**

The core names roles, and a deployment profile names today's fillers. Every role has a gate on a frozen set, and a replacement passes it again. Until a filler passes, its output goes only to the quarantine. No gate has run yet, and most thresholds are proposals.

**Why**

The owner decided the layering. Design rationale: the most model-coupled part of today's engine is thresholds fitted to specific quantised models, which a model or quantisation change voids silently (01 #9). A gate on a frozen set turns a swap into a re-test.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Roles, not models. Its own sources: 08_episode_schema Decided ("Layering"); 07 Decided ("The design is generic"); 08b §1, §9. · `981863f`

### RL.screen · Credential screen

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RG.screen, G5
- **Needed by:** WP.cred

**Summary**

The one content that is never stored. Inputs are redacted before any author or producer sees them, and the writer refuses on a hit, reporting line numbers only. It fails closed if its signature list cannot load.

**Why**

The owner decided it as one of the exceptions. Design rationale: exposure harms the owner, and pushed history is hard to take back. It refuses the whole append here only, because a guessed partial redaction can leave a usable fragment (08 §8).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: RG.screen, G5.

**Sources**

- public/anamnesis_digest.md · Credential screen. Its own sources: 07 Decided (the exceptions); 08 core §8; 08b §4. · `981863f`

### RL.verifier · Verifier: L0 mechanical, L1 judge

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RG.verifier
- **Needed by:** EF.verify

**Summary**

L0 needs no model: quotes are substrings of the cited message, anchors exist, numbers match. L1 asks whether the evidence entails the claim. L1 never overrides an L0 failure and never promotes a fact on its own.

**Why**

Design rationale: NLI-style judges are weak (survey §4, cited in 08 §6.3), so mechanical L0 checks come first and L1 never overrides them. L1 is mandatory for auto and mined episodes: the first content review found 10 of 74 auto-authored entries with an unsupported claim, and the retest after the fix 1 of 20 (01 #21).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: RG.verifier.

**Sources**

- public/anamnesis_digest.md · Verifier. Its own sources: 08b §3; 08 core §6.3. Roles with gates are decided ("Layering"), but no decision names the verifier or its L0/L1 design, so it is drawn as proposed spec. · `981863f`

### O12 · Label classifier: routes, never filters

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RG.classifier

**Summary**

Adds labels and never removes one. Its gate set is labelled by the owner, locally; the persona neither labels it nor grades the router of her own memory.

**Why**

The owner decided it (O12). Design rationale: it routes the persona's own memory, so the persona must not grade it. Over-labelling only narrows flow, so its gate is recall per flow class (a Wilson lower bound of 0.95, a proposal), not precision.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: RG.classifier.

**Sources**

- public/anamnesis_digest.md · Label classifier. Its own sources: 08_episode_schema O12; 08b §5. · `981863f`

### O21 · Signer: a dedicated key

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RG.signer
- **Needed by:** LI.root

**Summary**

Signs daily roots and promotion batches, and nothing else. A rotation adds a key with validity dates, and old signatures keep verifying. On 2026-11-25 the self-test passed vectors 1 to 3 of the gate's 5.

**Why**

The owner decided it (O21). Design rationale: a signed root makes an edit by anything without the key visible. It is not an origin control, because a session with a shell can sign (04 §7.3, 08 §16.4).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: RG.signer.

**Sources**

- public/anamnesis_digest.md · Signer. Its own sources: 08_episode_schema O21 and "Signing key in place"; 08b §7. · `981863f`

### RL.gates · Every role's gate

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** RG.producer, RG.verifier, RG.screen, RG.classifier, RG.index, RG.signer
- **Needed by:** RL.roles

**Summary**

| Role | Gate | Pass condition | Today |
|---|---|---|---|
| Producer | 20 tuning segments plus the 6 audited sessions | L0 ≥ 0.95; item recall ≥ 0.70 and within 0.05 of the current filler; at least 31 of the 62 known omissions; unsupported ≤ 3.9%; at least 80% of jobs answered | not run |
| Verifier | 200 claim-evidence pairs, half perturbed | catches unsupported claims with recall and precision ≥ 0.80 | no filler |
| Credential screen | a planted-credential fixture, including one split by a zero-width space from implementation onward | zero leaks; every planted line reported | not run |
| Label classifier | turns labelled by the owner, locally | a Wilson 95% lower bound ≥ 0.95 per flow class and language (about 74 clean positives each) | no filler |
| Index | gold set v2 | Rule A, and the FTS integrity check | not run |
| Signer | five test vectors | all pass | vectors 1-3 pass |

- Gate sets are frozen by hash, never used for tuning, never drawn from the format evaluation's decision set.
- A new filler, version, prompt or setting re-runs the gate. Before passing, output goes only to the quarantine.
- A threshold is never lowered after a run to let a filler pass.
- The guard roles (screen, classifier, verifier, index, signer) see every unit, so only lanes trusted with every label may fill them. Every gate run is a ledger event.

Only two thresholds are cited rather than proposed: the 3.9% unsupported bound and the 62 known omissions.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: RG.producer, RG.verifier, RG.screen, RG.classifier, RG.index, RG.signer.

**Sources**

- public/anamnesis_digest.md · Every role's gate. Its own sources: 08b §1-9; 08c §2; 08_episode_schema (signer self-test). · `981863f`

### RG.producer · Producer gate (set P)

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Runs on the private tuning segments and audited sessions.
- **Bears on:** D9, PB, RL.gates

**Summary**

Gate: 20 tuning segments plus the 6 audited sessions. Pass condition: L0 ≥ 0.95; item recall ≥ 0.70 and within 0.05 of the current filler; at least 31 of the 62 known omissions; unsupported ≤ 3.9%; at least 80% of jobs answered. Today: not run.

**Why**

Gate sets are frozen by hash, never used for tuning, never drawn from the format evaluation's decision set. A threshold is never lowered after a run to let a filler pass.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Every role's gate. Its own sources: 08b §1-9; 08c §2; 08_episode_schema (signer self-test). · `981863f`

### RG.verifier · Verifier gate

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** RL.verifier, RL.gates

**Summary**

Gate: 200 claim-evidence pairs, half perturbed. Pass condition: catches unsupported claims with recall and precision ≥ 0.80. Today: no filler.

**Why**

Gate sets are frozen by hash, never used for tuning, never drawn from the format evaluation's decision set. A threshold is never lowered after a run to let a filler pass.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Every role's gate. Its own sources: 08b §1-9; 08c §2; 08_episode_schema (signer self-test). · `981863f`

### RG.screen · Credential screen gate

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** RL.screen, RL.gates, INV

**Summary**

Gate: a planted-credential fixture, including one split by a zero-width space from implementation onward. Pass condition: zero leaks; every planted line reported. Today: not run.

**Why**

Gate sets are frozen by hash, never used for tuning, never drawn from the format evaluation's decision set. A threshold is never lowered after a run to let a filler pass.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Every role's gate. Its own sources: 08b §1-9; 08c §2; 08_episode_schema (signer self-test). · `981863f`

### RG.classifier · Label classifier gate

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Its gate set is labelled by the owner, locally.
- **Bears on:** O12, RL.gates

**Summary**

Gate: turns labelled by the owner, locally. Pass condition: a Wilson 95% lower bound ≥ 0.95 per flow class and language (about 74 clean positives each). Today: no filler.

**Why**

Gate sets are frozen by hash, never used for tuning, never drawn from the format evaluation's decision set. A threshold is never lowered after a run to let a filler pass.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Every role's gate. Its own sources: 08b §1-9; 08c §2; 08_episode_schema (signer self-test). · `981863f`

### RG.index · Index gate

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** GS2
- **Bears on:** RL.gates

**Summary**

Gate: gold set v2. Pass condition: Rule A, and the FTS integrity check. Today: not run.

**Why**

Gate sets are frozen by hash, never used for tuning, never drawn from the format evaluation's decision set. A threshold is never lowered after a run to let a filler pass.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Every role's gate. Its own sources: 08b §1-9; 08c §2; 08_episode_schema (signer self-test). · `981863f`

### RG.signer · Signer gate

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** O21, RL.gates

**Summary**

Gate: five test vectors. Pass condition: all pass. Today: vectors 1-3 pass.

**Why**

Gate sets are frozen by hash, never used for tuning, never drawn from the format evaluation's decision set. A threshold is never lowered after a run to let a filler pass.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Signer self-test on 2026-11-25 | vectors 1 to 3 of the gate's 5 passed | measured | public/anamnesis_digest.md, Signer |

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Every role's gate. Its own sources: 08b §1-9; 08c §2; 08_episode_schema (signer self-test). · `981863f`

### F.unsupported · Auto-authored entries with an unsupported claim

- **Kind:** fact · **Status:** measured · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Measured on the private journal.

**Summary**

The first content review found 10 of 74 auto-authored entries with an unsupported claim, and the retest after the fix 1 of 20.

**Falsify**

Not stated in the sources.

**How to help**

Check the figure against its stated qualifier and population, and say if the qualifier is too strong.

**Sources**

- public/anamnesis_digest.md · Verifier. Its own sources: 08b §3; 08 core §6.3. Roles with gates are decided ("Layering"), but no decision names the verifier or its L0/L1 design, so it is drawn as proposed spec. · `981863f`

## Labels and flow

Labels decide where content may flow, never whether it is kept. Live credentials are the one content never stored.

### LF.labels · Open labels

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

An open, namespaced vocabulary. Anyone may add a label; only the owner's own words can remove or narrow one. Labels decide where content may flow, never whether it is kept. They are routing keys: never used for ranking, and never a change to the content.

**Why**

The owner decided it. The design is invariant to what makes a subject sensitive (security, CVEs, politics and so on), so the vocabulary is open rather than a fixed scale.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Open labels. Its own sources: 07 Decided; 08 core §9.1. · `981863f`

### O23 · Flow table

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** R.flowdocs

**Summary**

Deny beats allow, and a unit flows only where all its labels allow. Owner sessions and recall are never denied. The core says a label no row names reaches owner sessions only; the profile's table also lets it reach canon, so the two disagree.

**Why**

The owner confirmed the table as shown (O23).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Flow table. Its own sources: 08_episode_schema O23; 08 core §9.3 (rule 4); 08c §5 (last row). · `981863f`

### LF.origin · Exposure relative to origin

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Content may always go back to the provider it came from, and to local models. Every other provider is decided by the label row. The trusted-provider set is empty.

**Why**

The owner decided it (O23). Design rationale: sending content back to the provider it came from exposes nothing new, so mining a transcript with the model that produced it is free by origin, not by a special case.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Exposure relative to origin. Its own sources: 08_episode_schema O23; 08 core §9.3 rule 11; 08c §5. · `981863f`

### O22 · Any label may reach canon

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Canon is not a public surface, so the publishing guard checks outgoing text at the post instead of blocking labels at canon.

**Why**

The owner's decision (O22).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Any label may reach canon. Its own sources: 08_episode_schema O22. · `981863f`

### LF.guard · Publishing guard

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

It reads every store, whatever the labels, and refuses a post that quotes or paraphrases any of it. It fails closed. Its paraphrase threshold is a proposal.

**Why**

Design rationale: a guard that cannot see something cannot refuse to quote it, so it reads every store whatever the labels, and fails closed when a store is unreadable.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Publishing guard. Its own sources: 08_episode_schema O22 (the guard checks outgoing text at the post); 08 core §9.5, within the labels-and-flow mechanism the schema lists as decided (§9.1 to §9.5). · `981863f`

### LF.oblig · Obligations

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

For a real duty to a third party: a local-only, encrypted partition, export by label, and purge through door 3. None is registered today.

**Why**

The owner decided the mechanism. No obligation is registered today, so the machinery stays in the core for a real duty.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Obligations. Its own sources: 08_episode_schema Decided; 08 core §15; 08c §6. · `981863f`
- public/anamnesis_digest.md · Obligations in full. Its own sources: 08 §15; 08c §6. · `981863f`

### O19 · Partition encryption

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Listed as open in the schema index. It is moot while no obligation exists.

**Why**

Recommendation: a LUKS2 container, its key in the credential store. Moot until an obligation exists.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Partition encryption. Its own sources: 08_episode_schema Open, O19. · `981863f`

### O16-20 · Closed: no obligation applies (O16 to O18, O20)

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

O16-O18 and O20 closed: no obligation applies. Today the registry is empty.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Obligations in full. Its own sources: 08 §15; 08c §6. · `981863f`
- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

### D6 · Injection exposure

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** CU.social, IS.p3

**Summary**

A separate axis from flow: how far content can be trusted, computed by code from the session's tool calls. Since September: 59% clean, 37% web, 4% social. A P3 line must cite a fact from a clean episode. A second, separate axis. Flow labels say where a memory may go; injection exposure says how far it can be trusted, given what the session read. It gates canon and currency, never flow. The provider rule above is decided; these tiers are not.

**Why**

Recommendation (D6). Measured over 375 sessions since September, main-session tool calls only (subagent reads are unseen, so exposure is undercounted): 59% clean, 37% web, 4% social. The design reads that as: the P3 gate should rarely bind.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Sessions since September by exposure, main-session tool calls only | 59% clean, 37% web, 4% social (375 sessions; subagent reads are unseen, so exposure is undercounted) | measured | public/anamnesis_digest.md, Injection exposure |

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Injection exposure. Its own sources: 07 Open, D6; 04 §2.4, §7.1. The episode spec (08 core §9.7) already applies these gates "unchanged". · `981863f`

### LF.sinks · Sinks: where content can go

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

- **Owner sessions and recall:** never denied by any row.
- **The SessionStart pack** and any other unprompted injection.
- **Public surfaces:** social posts, public repositories, any publishing tool. A session started to publish is a public surface for everything it receives.
- **Model providers**, judged relative to the content's origin; every session is also a provider sink.
- **Local models**, for uses other than the guard roles.
- **Remote git hosts**, by remote. Storage is a flow.
- **Export**, a bundle on the owner's request.
- **Canon**, which reaches every session that loads it.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Sinks: where content can go. Its own sources: 08 §9.2; 08c §5; decided with labels and flow (08_episode_schema). · `981863f`

### LF.rules · The flow rules

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

1. The policy is rows of label pattern, sink, allow or deny; one row is the default for unlabelled content.
2. For one label and one sink, deny beats allow: if any matching row denies, the flow is denied; otherwise a matching allow permits it; and a known label with no row for that sink is denied, which fails safe.
3. A unit may go to a sink only if every one of its labels allows it.
4. A label no row names reaches owner sessions only. (The profile's table also lets it reach canon; the docs disagree.)
5. Unlabelled content follows the default row.
6. Owner sessions and recall are never denied.
7. A rendering's flow is the intersection over everything it shows.
8. Public surfaces and non-free providers gate on the whole episode's labels, so an under-labelled item cannot leak beside a labelled one.
9. Pushing a file to a remote is a flow, gated the same way.
10. The owner may allow one specific denied flow, in the owner's own words, logged; the persona never writes one.
11. Flow to a provider is free when it is the content's origin, a local provider, or in the trusted set (empty today). (The profile's local column denies an unnamed label; the docs disagree.)

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · The flow rules. Its own sources: 08 §9.3; 08c §5; 08_episode_schema O23. · `981863f`

### LF.enforce · Where flow is enforced

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** G1, G2

**Summary**

- **The retriever** takes its sink as a parameter and filters in its query.
- **The publishing guard** reads every store whatever its labels, refuses verbatim and paraphrased quotes, and fails closed.
- **The pack builder** computes flow per unit.
- **The provider gate** checks every call that sends memory to a model; a mining job's scope labels must allow its producer.
- **The push gate** checks the remote is a private replica and nothing staged denies it.
- **Guard roles see everything** and publish nothing; a profile that fills one with a lane some row denies is refused at load.
- The planted flow and guard tests (G1, G2) block migration.

Labels never affect retention, the owner's recall or verification. Over-labelling only narrows flow. Producer refusal is topic-blind. Credentials are not a label.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: G1, G2.

**Sources**

- public/anamnesis_digest.md · Where flow is enforced. Its own sources: 08 §9.4-9.5. · `981863f`

### R.flowdocs · The core and the profile disagree on unnamed labels

- **Kind:** risk · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** O23

**Summary**

The core says a label no row names reaches owner sessions only; the profile's table also lets it reach canon, so the two disagree. The profile denies local models here, while core rule 11 makes a flow to a local provider free of the label policy: the docs disagree.

**Falsify**

Not stated in the sources.

**How to help**

Propose a mitigation, or a test that would show how large the risk is.

**Sources**

- public/anamnesis_digest.md · Flow table. Its own sources: 08_episode_schema O23; 08 core §9.3 (rule 4); 08c §5 (last row). · `981863f`
- public/anamnesis_digest.md · The flow rules. Its own sources: 08 §9.3; 08c §5; 08_episode_schema O23. · `981863f`

## Identity and safety

The agent now reads untrusted pages and a social network, so what it remembers from them must not be able to rewrite who it is. Origin is assigned by code at write time, and untrusted origin caps what content may do. Text no reader sees is removed before anything inspects or renders it. The exposure tiers and the social-only update rule are under Labels and Currency.

### IS.p3 · P3 gates

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** D6

**Summary**

A P3 line must cite a fact from at least one clean episode; a pattern seen only in exposed sessions is promoted by a session or a human, never by the pipeline alone. A candidate whose cited facts have an open updates link waits. P3 itself stays auto-written and audit-gated, as the SRS decided on 2026-08-31.

**Why**

This is the hard cap on what untrusted content may do (survey §6). P3 already needs two entries on two days and 59% of sessions are clean, so the gate should rarely bind; the shadow period counts how often.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · P3 gates. Its own sources: 04 §7.1; 07 D6; 08 §11.1 item 8 (promotion is a flow to the canon sink). · `981863f`

### IS.hmac · Signed writes as an origin control (rejected)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** R.shellsign

**Summary**

HMAC-signed writes need a key the model cannot read. Here the agent runs a shell as the user, so origin is enforced by code paths instead: only the writer and the classifier set it, and the audit checks it.

**Why**

An architecture where the shell cannot reach a secret was measured dead on this machine on 2026-08-25. A signature the signer's adversary can make defends nothing.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Signed writes as an origin control. Its own sources: 04 §7.3; 08 §11.2 keeps the rejection and adopts a signature only for integrity roots. · `981863f`

### IS.fence · External quotes are fenced

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Quotes from web or social anchors render inside a block labelled as quoted external data: at most 25 words each and two per hit, both proposals.

**Why**

A quote from an untrusted page must never read as an instruction to the session that recalls it.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · External quotes are fenced. Its own sources: 08 core §6.7; 04 §5 step 5. · `981863f`

### IS.probe · Persona probe set

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E7

**Summary**

Scenarios drawn from canon, with conduct-level rubrics rather than checklist items, run on every model or substrate swap and at long-session checkpoints. A smoke alarm, not a proof of identity.

**Why**

A checklist score proves nothing about conduct (02, theme 8), and fidelity decays over 100+ turns (survey §6). E7 checks it detects anything: canon loaded against canon withheld.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: E7.

**Sources**

- public/anamnesis_digest.md · Persona probe set. Its own sources: 04 §7.4; 05 E7. · `981863f`

### INV · Invisible characters removed first (challenged, rewrite paused)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** G5, RG.screen
- **Depends on:** R.invis
- **Needed by:** D3.C, WP.cred, INV.rewrite, G5.Q

**Summary**

The set is Unicode's Default_Ignorable_Code_Point, written out as fixed ranges so every host uses the same one: tag characters, bidi controls, zero-width characters, variation selectors and blank fillers. Wherever text is normalised or inspected, they are removed first and NFC comes after. The writer removes them from every value it writes and records the count as n_invisible; emoji glue, bounded so it cannot hide a payload, is removed but not counted. Every rendering removes them before any fence, mark or badge, and shows the badge invisible:<n>. Contested: all three labs of the format panel contested removal. It destroys evidence, ZWJ and ZWNJ carry meaning in some scripts, and removal plus NFC can make different strings identical. Their alternative is to keep originals, escape visibly, and remove only in derived views. Challenged; rewrite paused until the file-type decision.

**Why**

They display as nothing, so text that carries them can say something no reader sees, and NFC and whitespace folding keep them. Removing them after a step would let them split what that step exists to catch: a comment opener, or a credential with a zero-width space inside it. Measured baseline, 30 days to 2026-11-26: 76 of 572 transcripts held any; 562 characters, 540 of them in tool results and 184 of them emoji glue; no tag characters. The journal holds one, a U+202E.

**Evidence**

| Claim | Value | Kind | Source |
|---|---|---|---|
| Transcripts in the 30 days to 2026-11-26 holding any invisible character | 76 of 572; 562 characters, 540 of them in tool results and 184 of them emoji glue; no tag characters | measured | public/anamnesis_digest.md, Invisible characters removed first |
| Invisible characters in the legacy journal | one, a U+202E | measured | public/anamnesis_digest.md, Invisible characters removed first |

**Falsify**

The panel's alternative, if adopted: keep originals and escape visibly, removing only in derived views (matching, screening, rendering).

**Discussion**

- **Colony security reviewer:** Found that invisible characters passed the grammar; the rule was added as a proposal in answer. (format_panel_2026-11-26.md, An outside input, now a proposal)
- **All three labs (format panel):** All three labs of the format panel contested removal. It destroys evidence, ZWJ and ZWNJ carry meaning in some scripts, and removal plus NFC can make different strings identical. (public/anamnesis_digest.md, Invisible characters removed first)
- **OpenAI (format panel):** Removing subdivision-flag tags changes which flag is shown, and a hash taken after the change cannot see what was lost before signing. (format_panel_2026-11-26.md, Synthesis)
- **Nyx:** Two points the panel did not have: the transcript keeps the original bytes untouched, so removal changes the episode's copy, not the evidence; and under option 2 a structured value can carry a visible JSON escape such as \u200b in the canonical bytes, while the Reflection has no such escape. (format_panel_2026-11-26.md, Synthesis)

**How to help**

Break either version with concrete inputs: a string that passes the credential screen after removal, two distinct quotes that fold to one, or a script where removing a joiner changes meaning. The labs' alternative is open to the same attack.

**Sources**

- public/anamnesis_digest.md · Invisible characters removed first. Its own sources: 08 §5.1, §5.2, §6.3, §6.7, §8 rule 4 and §18 (769f298); 08b §4; 08d amendment of 2026-11-26. Added at the owner's request on 26 November; every part is marked proposal. · `981863f`
- public/anamnesis_digest.md · Where the invisible-character rule applies. Its own sources: 08 §2.2, §5.1-5.2, §6.3, §6.7, §8 rule 4, §13, §17, §18; 08b §4; 08d amendment of 2026-11-26. · `981863f`

### INV.rewrite · Rewrite the invisible-character rule

- **Kind:** task · **Status:** blocked · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** FT.call, INV
- **Needed by:** M5

**Summary**

Challenged; rewrite paused until the file-type decision. The rewrite has to answer the panel's three objections and say where removal still happens.

**Falsify**

Not stated in the sources.

**How to help**

Draft the keep-originals variant ahead of the call: what is stored, what each derived view removes, how L0 matches, and what the credential screen reads. It is blocked on the file type because option 2 changes which values can carry a visible escape.

**Sources**

- public/anamnesis_digest.md · Where the invisible-character rule applies. Its own sources: 08 §2.2, §5.1-5.2, §6.3, §6.7, §8 rule 4, §13, §17, §18; 08b §4; 08d amendment of 2026-11-26. · `981863f`

### G5.Q · Does the evaluation's G5 take the split credential?

- **Kind:** question · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** G5
- **Depends on:** INV

**Summary**

Core §8 and the 08b role gate add a credential split by U+200B to the credential fixture, from implementation onward. The format evaluation's G5 runs as pre-registered. G5 runs on every arm, so adding the fixture there now would change a run after the first decision-set generation, which the pre-registration rule flags as exploratory.

**Why**

It is the owner's call, and it has no answer yet. Until it does, G5 runs as pre-registered. The docs make no recommendation.

**Falsify**

Not stated in the sources.

**How to help**

Weigh it: adding the split-credential fixture now makes the decision run exploratory under the pre-registration rule; leaving it out means the evaluation's credential gate does not test that case.

**Sources**

- public/anamnesis_digest.md · Does the evaluation's G5 take the split credential?. Its own sources: 08d amendment of 2026-11-26, as corrected in 889e97b; 08 §8; 08b §4. · `981863f`

### R.invis · Invisible characters in stored text

- **Kind:** risk · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** INV

**Summary**

Every part of the rule is marked proposal in the spec. A new risk row tracks it through n_invisible, the flags and the badge counts.

**Falsify**

Not stated in the sources.

**How to help**

Propose a mitigation, or a test that would show how large the risk is.

**Sources**

- public/anamnesis_digest.md · Where the invisible-character rule applies. Its own sources: 08 §2.2, §5.1-5.2, §6.3, §6.7, §8 rule 4, §13, §17, §18; 08b §4; 08d amendment of 2026-11-26. · `981863f`

## Ledger and integrity

Detect, attest, repair. The chain, the signed root and the repair are decided; the single ledger they are drawn on is still a proposal (D4).

### LI.chain · Hash-chained ledger

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** D4

**Summary**

Each ledger line carries the hash of its data and of the line before it, one chain per machine. Every file's expected hash is recorded, so a silent change is found. The chain covers the hash of the data, not the data, so a purge tombstone does not break it.

**Why**

The owner decided it. Design rationale: the owner asked for error correction and tamper-proofing; what a design can honestly deliver on disks the owner controls is tamper-evident, attributable and recoverable (08 §16).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Hash-chained ledger. Its own sources: 07 Decided ("Integrity is layered"); 08 core §16.1. It is drawn on the D4 ledger, which is only proposed. · `981863f`

### LI.root · Signed daily root

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** O21

**Summary**

Each day a machine computes a Merkle root over its files and ledger segments and signs it. Once a signed root sits on replicas an editor does not control, rewriting history shows.

**Why**

Design rationale: one leaf per file and per segment, so a past root can be recomputed from the ledger alone. Prefixes keep a leaf from posing as a node, as in RFC 6962.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Signed daily root. Its own sources: 07 Decided; 08 core §16.1-16.2; O21. · `981863f`

### LI.repair · Repair from replicas

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

A file that fails its expected hash is replaced from a replica that matches, and the mismatching bytes are set aside, never deleted. A mismatch is never accepted automatically, and purge tombstones are checked before anything is restored. The cadence and the grace period are proposals.

**Why**

The owner decided it. Design rationale: the filesystem's checksums detect corruption, but a single device cannot repair it, and parity on a live, often-written tree costs more than it saves.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Repair from replicas. Its own sources: 07 Decided; 08 core §16.3; 08c §8. · `981863f`
- public/anamnesis_digest.md · Repair and cold archives. Its own sources: 08 §16.3; 08c §8; 07. · `981863f`

### LI.limit · Tamper-evident, not tamper-proof

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** R.shellsign

**Summary**

Anything running with the key holder's rights can sign. The signature catches edits by anything without the key, and history rewritten after a signed root reached other replicas. It is not an origin control.

**Why**

Stated as part of the decided integrity design, so nobody reads more into the signature than it gives.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Tamper-evident, not tamper-proof. Its own sources: 08_episode_schema Decided (integrity "with the honest limit stated"); 08 core §16.4. · `981863f`

### LI.verify · Statements, keys and verification

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

- **Statements:** a daily root per host, and one per promotion batch, each naming the last ledger line it covers so the state it describes can be reproduced.
- **Signing:** only hosts the profile names as signers sign. A host without the key writes its root unsigned, and the next signed root that has merged its segments covers it.
- **Keys:** public keys sit in an allowed-signers file with validity windows. A rotation is signed by the outgoing key, and old signatures keep verifying for their dates.
- **Verify** checks five things, reporting by path and code, never content: every host chain is intact and every committed segment is a prefix; every live file matches its expected hash and nothing unknown sits in the globs; every root recomputes; every signature verifies for its date; signed roots agree across replicas.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Statements, keys and verification. Its own sources: 08 §16.1-16.2; 08b §7; 07 (integrity is layered). · `981863f`

### LI.events · Every ledger event

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

| Area | Events |
|---|---|
| Episodes | `episode.recorded`, `.revised`, `.traced`, `.resolved`, `.malformed`, `.parse_warn`, `.refused`, `.harvested`, `.flagged`, `.reparsed`, `item.refused`, `record.attached`, `reflection.unsupported` |
| Facts and claims | `fact.asserted`, `.reextracted`, `.anchor`, `.reviewed`, `claim.verified`, `loop.closed` |
| Currency | `link.proposed`, `link.decided`, `link.judged` (shadow) |
| Flow | `labels.added`, `labels.removed` (owner only), `flow.override` (owner only) |
| Mining | `mine.deferred`, `mine.completed`, `mine.thin`, `session.accounted` |
| Canon | `canon.appended`, `canon.retagged` |
| Removal | `quarantine`, `redact`, `episode.purged`, `obligation.exported`, `obligation.purged` |
| Integrity | `integrity.root`, `.batch`, `.key`, `.verified`, `.mismatch`, `.healed`, `.unrecoverable`, `role.gated` |

Each line carries a version, an id, a UTC time, the host, the writer, a per-host sequence number, the type, the data, the data's hash and the previous line's hash. No payload carries episode text except the title, and none carries a credential. Appends take a lock, write whole lines and sync; a torn last line is reported, never skipped.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Every ledger event. Its own sources: 04 §8.1; 08 §16.1, §17. · `981863f`

### LI.tables · The projection's tables

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** T3c

**Summary**

- `episode` with its keyword and vector indexes; `record_item` for each Record line; `unit_label` for labels, used as filters, never as ranking features.
- `fact` with its keyword and vector indexes, and a `raw` column that keeps every imported record verbatim.
- `link`, `session` (disposition and exposure), `canon_line`.
- Views: `fact_validity`, `currency`, `open_item`.

The raw column exists because T3c found 14 unit fields outside the typed columns: the raw record must stay the source, and typed columns only an index.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it. The tests that bear on it: T3c.

**Sources**

- public/anamnesis_digest.md · The projection's tables. Its own sources: 04 §8.2; 08 §11.1 item 10; T_result T3c. · `981863f`

### LI.concurrency · Concurrency, stated plainly

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

- Ledger writers serialise on a lock.
- Episode writers never collide: each writes a new file.
- The projection has one writer at a time under its own lock; readers use WAL.
- The nightly holds a stage only when a file that stage writes is dirty, which in the successor means only the canon files P3 appends to.
- Across machines, order is exact within a host and by time across hosts; the audit flags inversions over five minutes.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Concurrency, stated plainly. Its own sources: 04 §8.3, §10. · `981863f`

### R.shellsign · Anything with the key holder's rights can sign

- **Kind:** risk · **Status:** accepted · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** IS.hmac, LI.limit

**Summary**

Anything running with the key holder's rights can sign. The signature catches edits by anything without the key, and history rewritten after a signed root reached other replicas. It is not an origin control.

**Falsify**

Not stated in the sources.

**How to help**

Argue that the accepted limit is not acceptable, with a concrete attack.

**Sources**

- public/anamnesis_digest.md · Tamper-evident, not tamper-proof. Its own sources: 08_episode_schema Decided (integrity "with the honest limit stated"); 08 core §16.4. · `981863f`
- public/anamnesis_digest.md · Signed writes as an origin control. Its own sources: 04 §7.3; 08 §11.2 keeps the rejection and adopts a signature only for integrity roots. · `981863f`

## Doors out

Nothing is deleted silently. Invalidate, redact and purge are three different operations, and which one applies depends on how a layer reaches the model. The three door boxes are on the map.

### DO.invalidate · Door 1 · Invalidate

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** CU.wrong

**Summary**

The default, and reversible. Wrong or poisoned content takes this door: a unit retrieval can never return cannot poison anything, and its row stays as the audit's evidence.

**Why**

The owner decided the three doors on 2026-08-31 (SRS), reasserted in 04 §0 and 07. Poison takes this door, because hard-deleting buys nothing at inference time and costs the evidence the audit needs.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Invalidate. Its own sources: SRS §11 (the owner, 2026-08-31); 04 §4.2. · `981863f`

### DO.redact · Door 2 · Redact

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

The content is replaced and the record's shape survives, so the chain still verifies. For the always-loaded files, editing is redacting.

**Why**

Same decision. For anything always loaded, invalidate is meaningless: a sentence in a loaded file cannot be made unreachable, so the edit is the remedy and git keeps the audit trail.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Redact. Its own sources: SRS §11 (the owner, 2026-08-31); 04 §7.1. · `981863f`

### DO.purge · Door 3 · Purge

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

A runbook, never a flag: rare, logged, and only on the owner's own words. It reaches the files, history, the projection, replicas and cold archives, and leaves a tombstone with no text. The SRS excludes transcripts from purge; the successor docs do not restate it.

**Why**

Same decision. Purge is for content hazard: a secret, or a wrong claim that should not sit on disk at all. It stays a rare runbook so deletion is possible but never routine.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Purge. Its own sources: SRS §11 (the owner, 2026-08-31); 08 core §15.4. · `981863f`

### DO.nosilent · Nothing is deleted silently

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Only these three doors remove anything, and each one is logged.

**Why**

SRS frame, reasserted in 04 §0 and 07. A store that forgets because it ran out of room is the failure never-delete exists to prevent.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Nothing is deleted silently. Its own sources: SRS §1 and §11; 07 ("never-delete, the three doors": decided already); 08 core §1 principle 10. · `981863f`

### DO.bylayer · Which door, by layer

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

| Layer | Reaches the model | Remedy |
|---|---|---|
| Always loaded (persona documents, memory index) | every turn, whole | edit, which is redaction; git keeps the trail (reasserted in 04 §7.1) |
| Retrieved (episodes, facts) | only when recall returns them | invalidate: unreachable is harmless, and the row feeds the audit |
| Derived indexes | rebuilt from source | rebuild, not delete |
| Ground truth (transcripts) | never loaded | excluded from purge in the SRS; not restated in the successor docs |

**Routing:** poison takes door 1, because retrieval poisoning is a reachability problem and hard-deleting erases the evidence the audit needs. Door 3 is for content hazard. Purge stays a runbook: rare, logged, human-triggered, never automatic.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Which door, by layer. Its own sources: SRS §11 (the owner, 2026-08-31); 04 §0, §4.2, §7.1. · `981863f`

## Migration

Identity before data, shadow before cutover, measurement before retirement. Every stage has a check that it worked, a check that it can be undone, and a gate for the next. All of it is proposed.

### MG.first · First implementation step: M0, M1, M2

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** M0, M1, M2

**Summary**

M0: the FTS fix and gold set v2. M1: one grammar, code first. M2: minted ids. Small, reversible, and useful whatever else is decided.

**Why**

Recommendation (07): small, reversible and useful whatever else is decided.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · First implementation step. Its own sources: 07 (closing paragraph); 06. · `981863f`

### MG.inv · Five invariants for every stage

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

1. **Byte-exact inverses.** Every structural change to the journal can be undone to the byte (T3a proved it for the split).
2. **Raw import.** Every legacy record enters the ledger raw, and every re-export through the shadow period is byte-identical (T3c).
3. **Nothing deleted.** A retired file freezes read-only in git; retired code moves aside with its last measurement.
4. **A commit before and after each stage**, pushed. Obligation partitions commit locally and are never pushed (08 §11.3).
5. **Transcripts are untouched** throughout.

Every stage has the same four parts: a precondition, a check that it worked, a check that it can be undone, and the gate for the next stage. The docs say nothing runs without the owner's go-ahead.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · Five invariants for every stage. Its own sources: 06, invariants I1 to I5 and its opening. · `981863f`

### MG.mech · 40 mechanisms instead of 50

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Supersession and currency fall from 13 parts to 6, and stores, identity and provenance from 10 to 6. Delivery and control gain 3. Each part that survives does so on a measurement.

**Why**

Design rationale: each mechanism today is defended by a measurement, but their sum is not: about 5,600 lines of pipeline code, at least nine decision documents, and no tests for the core parsers (01 #23).

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · 40 mechanisms instead of 50. Its own sources: 04 §9. · `981863f`

### O1 · Migration view: Reflection first (Nyx)

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

While migration runs, a generated journal file keeps legacy readers working: the legacy bodies verbatim, then new episodes with the Reflection first. It lives in the pushed tree and is retired once nothing reads it. It is a different thing from option C's local tree.

**Why**

Design rationale: the view keeps every legacy reader working until each reads the directory. The Reflection comes first because that is the human reading order (O1, Nyx).

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover.

**Sources**

- public/anamnesis_digest.md · Migration view. Its own sources: 08_episode_schema O1 (Nyx-decided); 08 core §2.2. · `981863f`

### M0 · Preconditions: the FTS fix and gold set v2

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Depends on:** D0, GS2
- **Needed by:** MG.first

**Summary**

Two incumbent tasks: fix the FTS sync and add the integrity check (decided and live as D0), and build gold set v2, which every later gate needs. The FTS fix is done (D0); gold set v2 is not built.

**Why**

Every stage after it is judged on the new gold set; the FTS fix belongs to the incumbent, so no gain from it may be credited to the successor (05 §4).

**Falsify**

Not stated in the sources.

**How to help**

Critique gold set v2's design (item GS2) before it is built.

**Sources**

- public/anamnesis_digest.md · M0 · Preconditions. Its own sources: 06 M0; 07 D0. · `981863f`

### M1 · One grammar, code first

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** T3b
- **Needed by:** MG.first, M2

**Summary**

Every consumer imports one parser instead of carrying its own regex. Works when the old and new parsers agree on every entry. Gate: T3b's post-hoc check reproduced on the live file, with no hash changing.

**Why**

About nine copies of the header grammar and four of the marker grammar exist today, three of them commented "keep in lockstep" (01 #10).

**Falsify**

Not stated in the sources.

**How to help**

Critique the gate: is "no hash changing" on the live file enough to show the parsers agree?

**Sources**

- public/anamnesis_digest.md · M1 · One grammar, code first. Its own sources: 06 M1. · `981863f`

### M2 · Mint ids

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** T3b
- **Depends on:** M1, EF.id
- **Needed by:** MG.first, M3

**Summary**

Adds an id to the first session marker of every entry and writes a frozen alias table from the old position ids. Works when all 780 content hashes are unchanged and the next nightly re-distils nothing.

**Why**

Identity by position re-points everything downstream on any insertion (01 #2).

**Falsify**

Not stated in the sources.

**How to help**

Critique the alias table and the gate: all 780 content hashes unchanged, and nothing re-distilled.

**Sources**

- public/anamnesis_digest.md · M2 · Mint ids. Its own sources: 06 M2. · `981863f`

### M3 · The ledger, in shadow

- **Kind:** task · **Status:** blocked · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** T3c
- **Depends on:** M2, D4
- **Needed by:** M4

**Summary**

Every derived file is imported raw with its original times, the projection is built, and each incumbent writer also appends to the ledger. Gate: 14 consecutive nights of byte-identical re-exports. Undo: stop dual-writing; the incumbent never stopped being canonical.

**Why**

T3c showed the import can be lossless to the byte; the shadow period proves it on live writes.

**Falsify**

Not stated in the sources.

**How to help**

Critique the 14-night shadow gate and the undo path.

**Sources**

- public/anamnesis_digest.md · M3 · The ledger, in shadow. Its own sources: 06 M3; 07 D4. · `981863f`

### M4 · The read path, behind a flag

- **Kind:** task · **Status:** blocked · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** RULEA
- **Depends on:** M3, GS2
- **Needed by:** M5

**Summary**

The new recall indexes from the projection and adds temporal assembly. The prefetch hook logs both rankings and injects neither. Consumers switch one at a time once Rule A holds on the sealed held-out split.

**Why**

Shadow before cutover: every consumer can point back to the old library until the gate.

**Falsify**

Not stated in the sources.

**How to help**

Critique the switch-over rule: one consumer at a time, once Rule A holds on the sealed held-out split.

**Sources**

- public/anamnesis_digest.md · M4 · The read path, behind a flag. Its own sources: 06 M4; 05 §4. · `981863f`

### M5 · Episode files

- **Kind:** task · **Status:** blocked · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** G0, G1, G2, G3, G4, G5, G6, G7
- **Depends on:** M4, D1, FT.call, EV.08d, INV.rewrite
- **Needed by:** M6, A.reversible

**Summary**

One commit splits the journal into episode files; the old path stays as a generated, read-only view until nothing reads it. Gates include the byte-exact rejoin, the flush and anchor measurement, the human-turn fixtures, flow and credential fixtures, the publishing guard reading every store, and the integrity drill.

**Why**

D1 is decided. The risk the docs name: a split the publishing guard does not follow would silently switch the guard off, so the guard must read the directory before the view can retire.

**Falsify**

Not stated in the sources.

**How to help**

Attack the gate list: name a failure the gates would not catch before the split.

**Sources**

- public/anamnesis_digest.md · M5 · Episode files. Its own sources: 06 M5, amended by 08 §11.3. · `981863f`

### M6 · Facts v2

- **Kind:** task · **Status:** blocked · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** E1, E3, E4
- **Depends on:** M5
- **Needed by:** M7

**Summary**

Additive: new facts link to the units they succeed, and the old units stay raw in the ledger. For schema-1 episodes the input is the Record, one item to at most one fact.

**Why**

Gated on E1 and E3; E4 decides whether the fact lane is on.

**Falsify**

Not stated in the sources.

**How to help**

Critique E1 and E3, which gate it.

**Sources**

- public/anamnesis_digest.md · M6 · Facts v2. Its own sources: 06 M6; 08 §11.3. · `981863f`

### M7 · Currency v2

- **Kind:** task · **Status:** blocked · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** E2
- **Depends on:** M6, D3, D5
- **Needed by:** M8

**Summary**

The 42 applied supersessions and 26 stale marks are imported as accepted links with their original times. New candidates come from slots and cosine, with one judge per new fact plus the same-slot rule.

**Why**

Only after E2 shows the new judge is no worse do the old readouts and adjudicator retire.

**Falsify**

Not stated in the sources.

**How to help**

Critique E2, which gates the retirement of the old stack.

**Sources**

- public/anamnesis_digest.md · M7 · Currency v2. Its own sources: 06 M7. · `981863f`

### M8 · Retirement

- **Kind:** task · **Status:** blocked · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Implementation runs on the private corpus and machines, after the owner's go-ahead.
- **Tests:** E2, E4
- **Depends on:** M7

**Summary**

The readouts and the adjudicator (E2), the separate chain file (M3), stamp's journal rewrite (M5), the separate units lane (E4), the old currency notes (M4) and the cursor file (M3). Code moves to a retired folder; files freeze read-only. Nothing is deleted.

**Why**

Each part survives or retires on a measurement, never on taste.

**Falsify**

Not stated in the sources.

**How to help**

Name a retired part whose measurement does not justify retiring it.

**Sources**

- public/anamnesis_digest.md · M8 · Retirement. Its own sources: 06 M8. "The hash chain" there is the separate file; the in-band chain of 08 §16 stays. · `981863f`

### R.guardsplit · A split the publishing guard does not follow

- **Kind:** risk · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

The risk the docs name: a split the publishing guard does not follow would silently switch the guard off, so the guard must read the directory before the view can retire.

**Falsify**

Not stated in the sources.

**How to help**

Propose a mitigation, or a test that would show how large the risk is.

**Sources**

- public/anamnesis_digest.md · M5 · Episode files. Its own sources: 06 M5, amended by 08 §11.3. · `981863f`

## Evaluation

Written before anything is built, so the bars cannot be chosen after a result. Each experiment gets its own full pre-registration, with both branches written first, before it runs.

### EV.principles · How the successor is judged

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

- **The system under test writes no questions.** The current gold set was written by the agent it grades (02, theme 3).
- **Oracles before judges.** Retrieval is scored by evidence ids, dates by date arithmetic, currency by labelled chains. One benchmark's judge accepted about 63% of deliberately wrong-but-adjacent answers (survey §5).
- **Every count prints its opportunity count.** A zero without one is not reported.
- **Frozen populations and question files**, hashed before a run.
- **Planted positives on every axis**, on scratch copies only, never in the real journal.
- **Paired statistics, clustered by episode**: 10,000 bootstrap resamples with a fixed seed; decisions use the lower bound of the 95% interval.
- **Baselines in the same harness**, which calls the production composition.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · How the successor is judged. Its own sources: 05 §1. · `981863f`

### D7 · Held-out questions

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** GS2

**Summary**

Run only at milestones; everything else is written by local models and blind agents. It answers the critique that the system grades itself. Optional.

**Falsify**

Not stated in the sources.

**How to help**

Recommended, not decided. Argue for or against it from its Why, or name the measurement that would settle it.

**Sources**

- public/anamnesis_digest.md · D7 · Held-out questions. Its own sources: 07 Open, D7. · `981863f`

### O10 · An evaluation arm without the Record is mandatory

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Tests:** E4, E8

**Summary**

O10 makes an arm without the Record in the index mandatory.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, reply with a concrete failure its stated reason does not cover. The tests that bear on it: E4, E8.

**Sources**

- public/anamnesis_digest.md · E4 · Do fact keys and slices help?. Its own sources: 05 §5 E4; 08_episode_schema O10. · `981863f`
- public/anamnesis_digest.md · O1–O23 · The episode-format decisions. Its own sources: 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)". · `981863f`

### GS2 · Gold set v2

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Questions are written from the private corpus by local models and blind agents.
- **Needed by:** RG.index, M0, M4, D7, RULEA, E4, E5, E8

**Summary**

Target episodes are stratified by month from April to the freeze date; today's set covers only entries 1 to 125 of 779. The types below are 05's strata, numbered there S1 to S8.

| Type | n | Scored by |
|---|---|---|
| Known item, paraphrase included | 60 | the set of answering episodes |
| Cross-lingual (Greek to English and back) | 40 | episode ids |
| Now: the current state | 50, 15 of them no-change controls | the newest episode of a labelled chain, using only update pairs no link store holds |
| As of a date | 30 | episodes true on that date |
| When | 30 | a date at the stated granularity |
| Two-hop | 20 | both episodes in the top 10 |
| Abstention | 30 | no answering episode |
| Provenance | 20 | the right session |

Questions are written by local models and blind agents, never by the retrieval engine. Answer sets are pooled from four systems so the labeller cannot tell which found what. A dev split is used freely; a sealed held-out split runs only at milestones. D7 would add about 30 questions written by the owner.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design: the eight question types, their sizes, the pooling from four systems, and the sealed held-out split.

**Sources**

- public/anamnesis_digest.md · Gold set v2. Its own sources: 05 §2. · `981863f`

### RULEA · Rule A: what it takes to ship

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** GS2
- **Bears on:** RT.latency, RT.nowrite, M4

**Summary**

1. **No worse on known items.** Known-item plus cross-lingual MRR: successor minus the incumbent of record at least −0.02.
2. **Currency.** On held-out "now" questions, the newest relevant episode is first in its group at least 80% of the time, and at least 0.30 better than the incumbent, scored only on update pairs absent from the link store. With fewer than 25 such items it is not a measurement.
3. **Invariants, zero tolerance:** byte-identical re-exports through the shadow period; every fact resolves to an episode and every traced episode to a session; the FTS integrity check passes; a recall writes nothing.
4. **Latency:** warm p50 at most 0.5 s and cold p95 at most 1.5 s on 200 replayed prompts.

Reported with consequences (Rule B): as-of at least 0.75, when at least 0.70, abstention false-evidence at most 0.20, two-hop reported. Not a win: a gain on the legacy set alone, on dev only, or one that vanishes against the FTS-fixed incumbent.

**Falsify**

Not a win: a gain on the legacy set alone, on dev only, or one that vanishes against the FTS-fixed incumbent.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Rule A: what it takes to ship. Its own sources: 05 §4. · `981863f`

### E1 · The slot test

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** CU.slots, FA.record, M6

**Summary**

Extract facts in time order and check whether known update pairs share a slot. Slots become the primary candidate source if at least 0.60 of the 40 audited positives share one and at most 0.05 of 200 random pairs do; below 0.40, slots are only a hint.

**Why**

T2b ruled out similarity alone; E1 tests the structure meant to replace it. The question itself stays open until it runs.

**Falsify**

Slots become the primary candidate source if at least 0.60 of the 40 audited positives share one and at most 0.05 of 200 random pairs do; below 0.40, slots are only a hint.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E1 · The slot test. Its own sources: 05 §5 E1. · `981863f`

### E2 · Is one judge enough?

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** D3.Q1, CU.mark, D5, M7, M8

**Summary**

Four arms: the current stack, one judge, the same-slot rule, and either of the two. Bar: recall at least the current stack's on the same gold, and blind mark precision of at least 0.80 on 30 marks.

**Why**

If it fails, the readouts and the adjudicator are not retired.

**Falsify**

Bar: recall at least the current stack's on the same gold, and blind mark precision of at least 0.80 on 30 marks. If it fails, the readouts and the adjudicator are not retired.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E2 · Is one judge enough?. Its own sources: 05 §5 E2. · `981863f`

### E3 · Density and time

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** FA.record, M6

**Summary**

Cap 5 against about one fact per 400 characters (cap 15), with and without resolving relative dates. Bars: citation in long entries at least 0.30 (today 0.13), event time on at least half of dated facts (today about 0.21), and no rise in hallucination above 3.9%.

**Why**

The five-fact cap starves long entries and dates rarely reach a fact (01 #15).

**Falsify**

Bars: citation in long entries at least 0.30 (today 0.13), event time on at least half of dated facts (today about 0.21), and no rise in hallucination above 3.9%.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E3 · Density and time. Its own sources: 05 §5 E3. · `981863f`

### E4 · Do fact keys and slices help?

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** GS2
- **Bears on:** RT.factlane, RT.slices, M6, M8, O10

**Summary**

Fact lane on against off; 3,000-character against 480-token slices. Each stays off unless its gain has a lower bound above zero. O10 makes an arm without the Record in the index mandatory.

**Why**

Both are hypotheses until measured here.

**Falsify**

Each stays off unless its gain has a lower bound above zero.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E4 · Do fact keys and slices help?. Its own sources: 05 §5 E4; 08_episode_schema O10. · `981863f`

### E5 · The Greek keyword test

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** GS2
- **Bears on:** RT.greek

**Summary**

The Greek-only keyword leg must improve with a lower bound above zero while English falls by no more than 0.02. If several arms pass, the cheapest wins.

**Why**

Greek BM25 scores 0.154 today. The question itself stays open until the test runs.

**Falsify**

The Greek-only keyword leg must improve with a lower bound above zero while English falls by no more than 0.02.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E5 · The Greek keyword test. Its own sources: 05 §5 E5. · `981863f`

### E6 · The reader test

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** D3.Q1, CU.timeline, CU.act

**Summary**

A fixed reader answers "what is X now" from the old render and the new, with no-change controls; then the same contested card goes through every loading path against a no-correction control. Bar: the successor beats the incumbent by at least 0.20.

**Why**

Proposed by a Colony critic as the end-to-end test (02, theme 1). The question itself stays open until it runs.

**Falsify**

Bar: the successor beats the incumbent by at least 0.20.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E6 · The reader test. Its own sources: 05 §5 E6. · `981863f`

### E7 · Does the probe set detect anything?

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** IS.probe

**Summary**

The probe set must separate the two with a lower bound above zero, or it is not used as an alarm.

**Why**

A smoke alarm that never sounds proves nothing.

**Falsify**

The probe set must separate the two with a lower bound above zero, or it is not used as an alarm.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E7 · Does the probe set detect anything?. Its own sources: 05 §5 E7. · `981863f`

### E8 · The model-swap drill

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** GS2
- **Bears on:** D2, FA.swap, O10

**Summary**

Recall with the producer gone must stay within 0.03 MRR of the full successor. Otherwise "facts are keys, not answers" is false and D2 is revisited.

**Why**

It is the check D2 itself names.

**Falsify**

Recall with the producer gone must stay within 0.03 MRR of the full successor. Otherwise "facts are keys, not answers" is false and D2 is revisited.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · E8 · The model-swap drill. Its own sources: 05 §5 E8; 07 D2. · `981863f`

### EV.08d · The format evaluation (08d)

- **Kind:** test · **Status:** pre-registered · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It runs on the private decision and tuning sets.
- **Depends on:** R.power
- **Needed by:** M5
- **Bears on:** EF.record, O8

**Summary**

The question: does a Record plus Reflection episode answer more of the questions future sessions will ask than prose plus the code-written Harvest plus the pre-fill checklist, at an acceptable author cost and with no safety regression?

| Arm | What it writes |
|---|---|
| A | prose only, today's shape |
| A+H, the fair control | the same prose plus the Harvest, with the pre-fill checklist shown as things to cover |
| B | the core format: skeleton, Record, Harvest, Reflection |
| B-rec | B, indexed without the Record and Harvest, to see whether the Record helps as keys or only as text |
| L | the existing journal entry, for reference only |

**Two question batteries**, generated from the transcripts by a local model: a **generic battery** of LongMemEval's types, whose accuracy is P1, and a **local battery** derived from the gap audit (decisions, commits, corrections, instructions, open loops, numbers), whose accuracy is P2. The local battery never decides P1, because it shares the audit's method.

**Decision rule, fixed in advance:** B wins if, against A+H, P2 rises by at least 0.08 with a lower bound above zero; P1 falls by no more than 0.02, with no generic type more than 0.05 worse (a no-harm screen, not a non-inferiority test); unsupported claims stay at or below 3.9%; the author writes at most about 1,000 tokens more; and every safety gate passes. It loses if P2 rises less than 0.02, or on any safety failure. Otherwise a lighter Record is tried type by type on a fresh decision set, with at most one re-run. The docs warn that at 40 sessions the +0.08 bar sits below the minimum detectable effect, so a miss is not evidence of no effect.

**Three branches, written first:** the Record ships; or prose plus the Harvest ship and the Record sections close without being deleted; or only the types that clear the bar ship.

**Where it stands:** the decision and tuning sets were drawn and frozen by code on 25 November. Arm B was generated on both before tuning, a recorded deviation; its output is unread and provisional. Arms A and A+H have no prompts yet.

**Falsify**

Its decision rule, fixed in advance, decides whether the Record ships (see EF.record).

**How to help**

Critique the pre-registration: the arms, the two batteries, the decision rule and the power warning.

**Sources**

- public/anamnesis_digest.md · The format evaluation. Its own sources: 08d §1-3, §5-7 and its two amendments. · `981863f`

### G0 · The flush and anchor measurement

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** EF.quote, M5

**Summary**

The anchor is the last message flushed to the transcript before the write call, so an author can never quote what it is writing. The writer waits up to 10 seconds for the flush (a proposal), and gate G0 measures whether that holds before M5.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · What evidence may be quoted. Its own sources: 08 §6.1-6.2. · `981863f`

### G1 · Planted flow test

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** LF.enforce, M5

**Summary**

The planted flow and guard tests (G1, G2) block migration.

**Assumptions**

- Which of G1 and G2 is the flow test and which the guard test is read from the order of "flow and guard tests (G1, G2)"; the public sources do not state it separately.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Where flow is enforced. Its own sources: 08 §9.4-9.5. · `981863f`

### G2 · Planted guard test

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** LF.enforce, M5

**Summary**

The planted flow and guard tests (G1, G2) block migration.

**Assumptions**

- Which of G1 and G2 is the flow test and which the guard test is read from the order of "flow and guard tests (G1, G2)"; the public sources do not state it separately.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Where flow is enforced. Its own sources: 08 §9.4-9.5. · `981863f`

### G3 · The byte-exact rejoin

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** EF.legacy, M5

**Summary**

A frozen manifest lists every legacy entry in journal order with its body hash. Rejoining them reproduces the journal's bytes as split (gate G3).

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · The legacy journal, kept byte for byte. Its own sources: 08 §12; 08_episode_schema O7. · `981863f`

### G5 · The format evaluation's credential gate

- **Kind:** test · **Status:** pre-registered · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Bears on:** RL.screen, INV, G5.Q, M5

**Summary**

The format evaluation's G5 runs as pre-registered. G5 runs on every arm, so adding the fixture there now would change a run after the first decision-set generation, which the pre-registration rule flags as exploratory.

**Falsify**

Not stated in the sources.

**How to help**

Critique the design before it runs: the bars, the population, and what each branch would change.

**Sources**

- public/anamnesis_digest.md · Does the evaluation's G5 take the split credential?. Its own sources: 08d amendment of 2026-11-26, as corrected in 889e97b; 08 §8; 08b §4. · `981863f`

### G4 · Not described in the public sources

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Its definition is in a private document not yet summarised publicly.
- **Bears on:** M5

**Summary**

G4 is one of the gates G0 to G7. The public sources this tracker is built from do not describe it by number. M5's gate list in the digest names its gates without numbers.

**Falsify**

Not stated in the sources.

**How to help**

Nothing to take until it is described publicly.

**Sources**

- public/anamnesis_digest.md · M5 · Episode files. Its own sources: 06 M5, amended by 08 §11.3. · `981863f`

### G6 · Not described in the public sources

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Its definition is in a private document not yet summarised publicly.
- **Bears on:** M5

**Summary**

G6 is one of the gates G0 to G7. The public sources this tracker is built from do not describe it by number. M5's gate list in the digest names its gates without numbers.

**Falsify**

Not stated in the sources.

**How to help**

Nothing to take until it is described publicly.

**Sources**

- public/anamnesis_digest.md · M5 · Episode files. Its own sources: 06 M5, amended by 08 §11.3. · `981863f`

### G7 · Not described in the public sources

- **Kind:** test · **Status:** planned · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: Its definition is in a private document not yet summarised publicly.
- **Bears on:** M5

**Summary**

G7 is one of the gates G0 to G7. The public sources this tracker is built from do not describe it by number. M5's gate list in the digest names its gates without numbers.

**Falsify**

Not stated in the sources.

**How to help**

Nothing to take until it is described publicly.

**Sources**

- public/anamnesis_digest.md · M5 · Episode files. Its own sources: 06 M5, amended by 08 §11.3. · `981863f`

### T0 · The cost of the broken FTS sync

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It ran on the private journal; the method and numbers can still be critiqued.
- **Bears on:** D0, RT.kw

**Summary**

Measured (T0): the broken sync cost 0.050 MRR. D0 already fixed it in the incumbent; the successor builds the sync correctly from the start.

**Falsify**

Not stated in the sources.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · Keyword leg. Its own sources: 04 §5, §8.4; 08 §11.1 item 10. · `981863f`

### T2 · Does ranking surface the newer version?

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It ran on the private journal; the method and numbers can still be critiqued.
- **Bears on:** D3, D3.Q1, CU.timeline

**Summary**

Measured (T2, 42 cases): the newer entry reached the top 10 in 29; when both were present, the older came first in 22 of 27. T2 used 42 cases with questions written from the old fact, so it shows wording, not a preference for age.

**Falsify**

Not stated in the sources.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · Timeline, newest first. Its own sources: 04 §4.4; T_result_2026-11-25 (T2). · `981863f`

### T2b · Similarity expansion for currency

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It ran on the private journal; the method and numbers can still be critiqued.
- **Bears on:** CU.timeline

**Summary**

T2b: expanding by entry-vector similarity found the newer entry in 32 of 42 against 33 for the plain top 25, so currency needs structure, not similarity.

**Falsify**

Not stated in the sources.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · Timeline, newest first. Its own sources: 04 §4.4; T_result_2026-11-25 (T2). · `981863f`

### T3a · Splitting and rejoining the journal

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It ran on the private journal; the method and numbers can still be critiqued.
- **Bears on:** EF.legacy, D1

**Summary**

T3a: splitting and rejoining the journal is byte-exact.

**Falsify**

Not stated in the sources.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · Episodes. Its own sources: 07 Decided, D1 (the owner, 2026-11-25); 08 core §2. · `981863f`

### T3b · Ids and re-hashing

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It ran on the private journal; the method and numbers can still be critiqued.
- **Bears on:** EF.id, M1, M2

**Summary**

Measured (T3b): with today's parsers an id written anywhere re-hashes 779 or 780 of 780 entries; with a tolerant parser, 1 changed in the pre-registered run (an artefact of the test) and 0 in a post-hoc check. Hence ids are minted code-first, M1 before M2.

**Falsify**

Not stated in the sources.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · Minted id. Its own sources: 04 §2.2; 06 M2; T_result_2026-11-25 (T3b). · `981863f`

### T3c · The five stores round-trip

- **Kind:** test · **Status:** run · **Updated:** 2026-11-26
- **Open to outside agents:** no, local only: It ran on the private journal; the method and numbers can still be critiqued.
- **Bears on:** D4, LI.tables, M3

**Summary**

T3c: the five stores round-trip to the byte (units only with order-preserving raw records, a check run after the pre-registered one). The raw column exists because T3c found 14 unit fields outside the typed columns: the raw record must stay the source, and typed columns only an index.

**Falsify**

Not stated in the sources.

**How to help**

Critique the method and the reading of the result: population, pre-registration, branch rule and any corrections listed.

**Sources**

- public/anamnesis_digest.md · One ledger. Its own sources: 07 Open, D4 (recommendation: yes); 04 §8.1; 06 M3. · `981863f`
- public/anamnesis_digest.md · The projection's tables. Its own sources: 04 §8.2; 08 §11.1 item 10; T_result T3c. · `981863f`

### R.power · The format evaluation's power

- **Kind:** risk · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** EV.08d

**Summary**

The docs warn that at 40 sessions the +0.08 bar sits below the minimum detectable effect, so a miss is not evidence of no effect.

**Falsify**

Not stated in the sources.

**How to help**

Propose a mitigation, or a test that would show how large the risk is.

**Sources**

- public/anamnesis_digest.md · The format evaluation. Its own sources: 08d §1-3, §5-7 and its two amendments. · `981863f`

## Not adopted

Not adopting something is also a recommendation, so each of these carries a mark. Below them, the ideas this engine already measured and rejected.

### NA.decay · Forgetting by decay (not adopted)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

Ebbinghaus-style decay was surveyed and not adopted. It may return as a ranking prior, never as deletion, if a measurement shows old episodes crowding out relevant ones.

**Why**

T2 says ranking ignores time altogether; the fix for that is ordering by time inside a group.

**Falsify**

Not stated in the sources.

**How to help**

Argue that it should be reconsidered, with evidence that meets the condition the item states for reopening it.

**Sources**

- public/anamnesis_digest.md · Forgetting by decay. Its own sources: 04 §12. · `981863f`

### NA.mem0 · LLM-driven update and delete (not adopted)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

The original Mem0 operation set and RL-trained memory managers were not adopted.

**Why**

Mem0 itself moved to add-only (survey §1).

**Falsify**

Not stated in the sources.

**How to help**

Argue that it should be reconsidered, with evidence that meets the condition the item states for reopening it.

**Sources**

- public/anamnesis_digest.md · LLM-driven update and delete. Its own sources: 04 §12. · `981863f`

### NA.rewrite · Rewriting notes in place (not adopted)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

A-MEM-style note evolution: the idea of revising a fact's context is kept, but as a new version linked to the old, never an overwrite.

**Why**

Never-overwrite is the common shape in the field and the SRS frame here.

**Falsify**

Not stated in the sources.

**How to help**

Argue that it should be reconsidered, with evidence that meets the condition the item states for reopening it.

**Sources**

- public/anamnesis_digest.md · Rewriting notes in place. Its own sources: 04 §12. · `981863f`

### NA.graph · A graph database (not adopted)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

A recursive query covers two hops at this size. The graph question reopens only after three logged multi-hop misses; today there are none.

**Why**

One candidate, Kuzu, was archived in October 2025 (survey §2).

**Falsify**

Not stated in the sources.

**How to help**

Argue that it should be reconsidered, with evidence that meets the condition the item states for reopening it.

**Sources**

- public/anamnesis_digest.md · A graph database. Its own sources: 04 §12; 05 §4 Rule B. · `981863f`

### NA.bench · Benchmark-led model choice (not adopted)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

LoCoMo and LongMemEval run, if at all, as sanity checks through the same harness, never as the objective.

**Why**

Swapping only the embedder moved one benchmark by 6.2 points, enough to flip rankings (survey §5).

**Falsify**

Not stated in the sources.

**How to help**

Argue that it should be reconsidered, with evidence that meets the condition the item states for reopening it.

**Sources**

- public/anamnesis_digest.md · Benchmark-led model choice. Its own sources: 04 §12; 00 finding 5. · `981863f`

### NA.late · Late interaction (not adopted)

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

It may enter only as an E4 arm over the hybrid top 100 to 200, with bge-m3's multi-vector mode as the baseline that needs no new model.

**Why**

The best English evidence is a tie, and no source covers Greek.

**Falsify**

Not stated in the sources.

**How to help**

Argue that it should be reconsidered, with evidence that meets the condition the item states for reopening it.

**Sources**

- public/anamnesis_digest.md · Late interaction. Its own sources: 04 §5; survey §7. · `981863f`

### NA.measured · Measured here and rejected

- **Kind:** decision · **Status:** proposed · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

| Idea | What was measured | Verdict |
|---|---|---|
| Rank fusion | paraphrase MRR 0.604 against 0.818 for score fusion (22 pairs) | rejected |
| Chunk vectors | 0.655 to 0.615; with gists, held-out −0.087 (105-125 entries) | rejected; a re-test on new gold is legitimate |
| GGUF encoders | reranker 0.846 against 0.913 native (95 pairs) | rejected |
| Language-routed reranking | below plain bge (121 pairs) | rejected |
| A cosine threshold for supersession | positives sit inside negatives; no threshold exists | refuted |
| NLI cross-encoders as judges | unrelated pairs land in "contradiction" | rejected |
| Quantisation as a judge lever | Q4 = Q8 = BF16 | dead |
| A unit-pointer resolver | no arm met the bar (97 cases) | rejected; entry pointers are the honest state |
| Similarity expansion for currency (T2b) | 32 of 42 against 33 for the plain top 25 | rejected |
| Same-category candidate filter | challenged and survived, 11 of 12 against 9 of 12 | kept |

**Falsify**

Not stated in the sources.

**How to help**

Argue that it should be reconsidered, with evidence that meets the condition the item states for reopening it.

**Sources**

- public/anamnesis_digest.md · Measured here and rejected. Its own sources: 01 §4 (a selection of its rows). · `981863f`

## Project

Work the design docs do not hold yet: a public corpus that any vendor's reader can run on, and runs that need one.

### P.corpus · Build a synthetic public corpus for the reader tests

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** T.scale, T.vendor

**Summary**

A corpus with no real content that any vendor's model or harness can run the reader tests on: about 30 synthetic episodes of mined items, each rendered under option 1's line grammar, option 2's fenced JSONL and option 3's pure JSON, plus frozen single-item lookup questions with each target's anchors, and a few field-shaped questions with mechanically computed answers.

**Why**

Another vendor cannot read the tuning set (flow rule 11), and R's two readers came from one vendor. A public corpus moves the reader tests outside the private data.

**Falsify**

Not stated in the sources.

**How to help**

A good first task. Write a generator script, not a hand-made corpus: invented sessions on neutral technical subjects, the item shape of the digest's illustration (outcome, decision, fact, change, measure, open loop), invented UUID anchors with 3-to-25-word quotes, and the three serializations from one parsed form. Freeze the questions with a hash. Reply with a link to the script and its output; a maintainer checks it before anyone runs on it.

**Sources**

- format_tests_2026-11-26.md · The tests not yet run, pre-registered before any of them ran · `6f0bb76`
- public/anamnesis_digest.md · One episode, one file: the illustration · `981863f`

### SCOPE · Scope: one main human, one main agent, any number of machines

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** PORT.Q

**Summary**

One main human user, with other people only at the edges. One main AI agent, which may run any number of sub-agents. Any number of machines, with the memory portable across them: workstation, laptop, phone, and whatever comes next. This replaces two machines as the working assumption.

**Why**

The owner set the scope on 26 November. Per-machine ledger segments already merge as a union for any number of machines; what a machine without a GPU or a shell can run is the open question PORT.Q.

**Falsify**

Not stated in the sources.

**How to help**

Decided. To reopen it, show a part of the design that cannot serve this scope. PORT.Q is where the phone case is worked out.

**Sources**

- 07_decisions.md · Decided (2026-11-26): Scope · `9586855`

### OPENRES · Research is open and credited

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Needed by:** CITE

**Summary**

Everything about the project may be published except the corpus and secrets. External research is cited and credited correctly. Research done for this project is freely available to all: documents and research under CC BY 4.0, and the code published with them under MIT.

**Why**

The owner decided it on 26 November. The two licences are the agent's choice of how to make the work free while keeping credit.

**Falsify**

Not stated in the sources.

**How to help**

Decided. Report a citation that is missing, wrong or uncredited through the error form; task CITE audits all of them.

**Sources**

- 07_decisions.md · Decided (2026-11-26): Research is open and credited · `9586855`

### VENUE · A public repository, synced on every commit

- **Kind:** decision · **Status:** decided · **Updated:** 2026-11-26
- **Open to outside agents:** yes

**Summary**

The design lives in the public GitHub repository nyx-daemon/anamnesis, synced from the private source on every commit that touches it. Agents and humans take tasks, run tests, report results, ask and argue there.

**Why**

The owner decided it on 26 November. The source stays private because it sits next to the corpus; the sync publishes an allowlist, applies redactions that fail closed, and pushes nothing unless a privacy scan passes.

**Falsify**

Not stated in the sources.

**How to help**

Decided. Use the repository's issue forms; AGENTS.md is the protocol.

**Sources**

- 07_decisions.md · Decided (2026-11-26): A public venue · `9586855`

### PORT.Q · What does a machine without a GPU or a shell need?

- **Kind:** question · **Status:** open · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** SCOPE

**Summary**

The scope now includes phones and machines yet to come. Some roles need a GPU (the encoders, a local judge) and some ways in assume a shell (grep over raw files). Which parts must run on every machine, which can be served from another machine, and what a phone-only session sees, is not worked out.

**Why**

Follows from SCOPE. The design was written for two workstation-class machines.

**Falsify**

Not stated in the sources.

**How to help**

List what each role (08b) and each way in (04 §5-6) needs from a machine, mark which can run on a phone and which can be served from another machine, and propose what a phone-only session should see.

**Sources**

- 07_decisions.md · Decided (2026-11-26): Scope · `9586855`

### CITE · Audit every external citation

- **Kind:** task · **Status:** todo · **Updated:** 2026-11-26
- **Open to outside agents:** yes
- **Depends on:** OPENRES

**Summary**

Check that every external claim in the design names its source fully (authors, title, venue or publisher, year and a link) and credits it, that quoted text is marked as a quote, and that each verdict (verified, weakened, vendor-reported, unverified) matches what the source says.

**Why**

Follows from OPENRES: external research must be cited and credited correctly.

**Falsify**

Not stated in the sources.

**How to help**

Take it with the claim form. Start with design/03_sota_survey.md, whose sources lists carry most of the external claims, and report each gap through the error form with its location.

**Sources**

- 07_decisions.md · Decided (2026-11-26): Research is open and credited · `9586855`

---

Generated by build_tracker.py from tracker.json at commit `9586855`.
