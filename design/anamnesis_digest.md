<!-- Generated from the public Anamnesis page. Same sanitized content as the page; each box is a level-4 heading with its status (Decided, Proposed or Open). -->

nyx-recall · successor design · public copy · status as of 26 November 2026

# Anamnesis ἀνάμνησις

The planned successor to the memory engine, on one page. The map comes first; below it, every part is explained: what it is, why it exists, and the decision or measurement behind it. Every box says whether it is decided, only recommended, or still an open question.

**Decided** (37 boxes): In the decided lists of 07 or the schema index, in the owner's words. A tag says when Nyx decided it, or when it was settled earlier, in the SRS.

**Proposed** (101 boxes): Recommended, not decided. This covers D3 to D9 and O19: the docs list them as open decisions, and each carries a recommendation.

**Open** (19 boxes): Nothing recommended yet: a question still being asked, or an alternative still on the table.

Measurements carry no mark. Each one sits inside the box it justifies, under "Why", with its source and the docs' own qualifier: measured, inferred, a hypothesis, or a check run after the fact. "Why" gives the owner's reason only where a decided list records one; otherwise it says it is the design's rationale.

**About this copy.** Prepared for outside review. It leaves out deployment-specific material: one Record item type, some label namespaces and flow-table rows, and the owner's own words. Where a decision matters to the architecture, it is stated neutrally.

## The whole engine

### Write path — how a memory is made

*Producers*

#### Transcript-first mining

*Decided · 07 · O4* — every in-scope session

**What** Every in-scope session with a transcript is mined into structured episodes, and its old prose stays byte-for-byte as their Reflection. Newest first, stopping when a batch fails its gate. Output waits in a quarantine outside git until the promotion gates pass.

**Why** The owner decided transcript-first (07). The design's rationale: an audit of 40 entries found the prose strong on decisions and corrections and weak on pointers: a SHA in 7 of 40, sourced numbers in 3 of 36, and 62 items omitted across 6 entries checked against their transcripts (08 §0).

**Source** 07 Decided (transcript-first back-fill); 08_episode_schema O4, O7; 08 core §10.5. The quarantine and promotion gates are spec, not separate decisions.

#### Producer

*Proposed · D9* — today: Opus through claude -p

**What** Turns transcript text into typed items as JSON, and code renders the file. It must produce from every register and subject, and declare what it will not process instead of skipping it. Its gate (set P) has not run.

**Why** Recommendation (D9): it is the only distiller that passed its accuracy bar here (07). The named cost: every writing stage hangs on one CLI login, and a dead login stalls silently (01 #14), so the audit warns after N nights with no facts. Measured on the mining prototype (08c §3): a 54-64K character job at medium effort took 68-77K tokens and 94-117 s, with every item passing L0.

**Source** 07 Open, D9 (recommendation: keep Opus); 08b §2; 08c §2-3.

#### Pass B producer

*Open · no filler chosen* — legacy prose with no transcript

**What** For legacy entries whose transcript is gone: it reads the screened prose and writes a companion record of items. No producer has been chosen for it.

**Why** Design rationale: some legacy entries have no transcript left, so the prose is the only source. Expect the old writer's unsupported rate until measured: 23 to 33%, a hypothesis (08 §12.2).

**Source** 08c §2; 08 core §12.2.

#### Refusal means deferral

*Decided · 07 · owner* — never dropped

**What** What the current producer refuses stays in the transcript and is queued for a freer producer. When one passes its gate, deferred jobs run first.

**Why** The owner decided it. Design rationale: a refusal is a property of one producer, not of the content, so the content waits for a freer producer. The rule is topic-blind.

**Source** 07 Decided (the exceptions); 08 core §9.6.

items, as JSON or by hand

#### The writer

*Proposed · 04 §2.2 · 08 §10* — draft, edit, append

**What** The one way an episode is born. Code drafts a skeleton and the author edits it. Append waits for the transcript to flush, screens, labels, checks every anchor and creates the file with O_EXCL. A failing item is withheld on its own; only a credential refuses the whole append.

**Why** Design rationale: today hand appends, a clock hook and a whole-file stamp rewrite all touch one file with no lock (01 #3), and 118 of 280 headers named a time ahead of the clock (02, theme 7). One writer with an atomic create removes both. Items fall back one at a time because a whole-append refusal at a pause produces dark sessions (08 §0.2).

**Source** 04 §2.2; 08 core §6.5, §10.2-10.4. Who writes which items is O9 (Nyx-decided).

through the roles below, into the ladder

### The ladder — what is kept, bottom up

L4

#### Canon

*Decided · SRS frame · O22* — the always-loaded canon files

**What** Curated, and loaded into every session. P3 promotes into it and may promote any label, because canon is not a public surface: the publishing guard checks the post instead (O22). Here editing is redacting, since nothing always-loaded can be made unreachable.

**Why** Design rationale (SRS frame): canon is what every session loads, so it stays curated. O22: canon is not a public surface, so the check belongs at the post. A gap the Colony found (02, theme 2): the always-loaded layer had no source links, dates or audit; the pointer audit and D8 answer it.

**Source** Ladder: SRS §1, decided before this package (07 lists the SRS frame as "decided already"; 04 §0). O22: 08_episode_schema, the owner, 2026-11-25. Editing is redacting: SRS §11, 04 §7.1.

P3 promotes

L2·L3

#### Facts

*Decided · D2 · owner* — keys into episodes, never beliefs

**What** A fact carries a subject, a slot, a kind, an event time, a mode and an anchored quote. It exists to get the right episode retrieved, and recall always answers with that episode and its evidence. A wrong fact costs a miss, not a false memory. E8 switches the fact lane off to check this.

**Why** The owner decided it (D2). The design's reasons: raw episodes are a strong baseline and extraction and update are where memory goes wrong (survey, cited in 04 §0); today 2,961 distilled facts are served though no one has read them (01 #7). As keys, a wrong fact costs a miss, not a false memory. If recall drops with the fact lane off (E8), D2 is revisited.

**Source** 07 Decided, D2 (the owner, 2026-11-25); 04 §3; 08 core §11.

extracted as keys

L1

#### Episodes

*Decided · D1 · owner* — one immutable file each

**What** Each episode is its own file, created atomically and never rewritten by a machine. Two machines merge through git, and two new files never collide where two appends to one file do.

**Why** The owner's reason for D1 (07): two machines merge through git, and two new files never collide where two appends to one file do. The design adds that three of the five high-severity fragilities had the single 2 MB file at their root: identity by position, lost updates between five writers, and dirty-file holds that left 9 of 18 nights with nothing distilled (01 #2, #3, #12). T3a: splitting and rejoining the journal is byte-exact.

**Source** 07 Decided, D1 (the owner, 2026-11-25); 08 core §2.

mined or written

L0

#### Transcripts

*Decided · SRS frame* — the only ground truth

**What** Written by the harness and never edited. Everything above them is derived and can be rebuilt from them. They are not in git today, and whether they should be is D10, which is open. The SRS excludes them from purge; the successor docs do not restate that, though the migration leaves them untouched throughout (06 I5).

**Why** Design rationale (SRS): the transcript is the only lossless record. Every quote anchor and every mined episode points back into it, so it is what verification checks against.

**Source** SRS §1 (the ladder) and §11 (the owner, 2026-08-31); reasserted as "the only ground truth" in 04 §0. Decided before this package, not in the 2026-11-25 list. Git: 04 §1 and 07 D10.

*L2·L3 · records every derived decision*

#### One ledger

*Proposed · D4* — replaces five stores

**What** Append-only JSONL, one segment per month per machine, so a merge is a union. It replaces the units JSON, the cursor, the old chain file and both supersession logs, and every current view becomes a projection of it. Recommended after a 14-night shadow period with byte-identical re-exports; the incumbent stays canonical until that gate.

**Why** Design rationale: five JSON and JSONL stores plus a separate hash chain share no write lock outside the nightly (01 #4, from an audit, not reproduced), and 86% of the chain is session-sync noise. One stream gives every record two clocks, merges two machines as a union of per-host files, and makes every view rebuildable. T3c: the five stores round-trip to the byte (units only with order-preserving raw records, a check run after the pre-registered one).

**Source** 07 Open, D4 (recommendation: yes); 04 §8.1; 06 M3.

Hash-chained ledger (*Decided*)

#### Projection

*Proposed · 04 §8.2* — SQLite in the cache, rebuilt in minutes

**What** Indexes and current-state views, rebuilt from episodes and the ledger. It is never the only copy of anything, and recall writes nothing outside it.

**Why** Design rationale: indexes must be disposable, so nothing in the cache is the only copy of anything. Today the read path writes the journal itself to refresh its index (01 #5, from an audit).

**Source** 04 §1, §5, §8.2.

#### Audit

*Proposed · 04 §8.4* — every check has a planted fault

**What** Recast onto the ledger: links resolve, anchors hold, validity per producer, P3 lines, the committed prefix, FTS integrity and event schemas. Each check prints what it covered and what it did not.

**Why** Design rationale: Colony critics found checks narrower than their names and checks that never fired (02, theme 6). A check that prints its population and opportunity count cannot pass silently.

**Source** 04 §8.4.

### Ways in — how memory reaches a session

#### SessionStart pack

*Proposed · 04 §6.1* — budgeted, with its size logged

**What** One function builds the injection: the newest episode, open proposals touching facts that canon cites, held entries, the nightly status and the sessions that went dark. An accepted update to a fact a P3 line cites is announced at the next start.

**Why** Design rationale: delivery is half the system. In October recall ran about 21 times in some 1,800 prompts while about 260 KB loaded unconditionally (01 #16, from Colony threads and an audit). Nobody knows what the pack costs, so its size is logged.

**Source** 04 §6.1-6.2; 08 core §13.

#### Recall

*Proposed · 04 §5-6* — recall · now · when · asof · trace

**What** Hybrid keyword, vector and reranker search over episodes, plus a fact-key lane that stays only if E4 shows a gain. Each hit shows its evidence, date, age, badges and a one-line rope to the transcript. A fact appears only as a note on its episode (D2, decided). Federation by register carries over from the SRS frame; the incumbent encoders stay until a challenger beats them.

**Why** Design rationale: it keeps the measured core and fixes what is broken. Score fusion beat rank fusion (paraphrase MRR 0.818 vs 0.604, 22 pairs), and chunk vectors lost at 105-125 entries (01 §4). Showing a date and age on every hit is what lets a reader see currency.

**Source** 04 §5, §6.5. D2: 07 Decided. Federation: SRS FR4.2, reasserted in 04 §0. The encoders: the 2026-08-09 bake-off, drawn as proposed.

#### Ambient prefetch

*Proposed · 04 §6.4* — log-only until its gate says inject

**What** It keeps its pre-registered gate. Its payload becomes a dated evidence pointer with a currency note, instead of an entry title.

**Why** Design rationale: the hook already has a pre-registered gate; only its payload changes, to something cheaper and more honest than an entry title.

**Source** 04 §6.4.

#### Raw files (grep)

*Proposed · D3 · question 2* — 36% of sessions grep; 7% call recall

**What** Over 30 days, 116 of 324 sessions grepped the raw journal and 22 called recall. Currency marks exist only in recall's rendering, so a grep sees none of them. Which door sessions should take is not decided; option C is the current lean.

**Why** Measured (the D3 panel brief): over 30 days 36% of sessions grepped the raw journal and 7% called recall, and recall use fell over the month. In a cold test, 2 of 3 fresh sessions opened the raw journal on their own. Marks only recall renders miss most readers.

**Source** D3_panel_2026-11-26 (the measurements); the D3 discussion, 2026-11-26 (the split).

#### Always-loaded layer

*Proposed · D8* — measure first, change nothing yet

**What** Two persona documents, about 260 KB, imported into every session. The figure of roughly 65,000 tokens is arithmetic on file sizes. Nothing is proposed until the real number exists.

**Why** Recommendation (D8). The design's reason: the layer is identity-critical, and the only figure is arithmetic on file sizes, so no change is worth proposing before a real number exists.

**Source** 07 Open, D8; 04 §6.1.

### Every write passes the roles

#### Roles, not models

*Decided · layering · owner* — a filler that passes the gate fills the role

**What** The core names roles, and a deployment profile names today's fillers. Every role has a gate on a frozen set, and a replacement passes it again. Until a filler passes, its output goes only to the quarantine. No gate has run yet, and most thresholds are proposals.

**Why** The owner decided the layering. Design rationale: the most model-coupled part of today's engine is thresholds fitted to specific quantised models, which a model or quantisation change voids silently (01 #9). A gate on a frozen set turns a swap into a re-test.

**Source** 08_episode_schema Decided ("Layering"); 07 Decided ("The design is generic"); 08b §1, §9.

#### Credential screen

*Decided · 07 · HARD law* — live credentials are always redacted — filler today signatures + entropy rule (*Proposed*)

**What** The one content that is never stored. Inputs are redacted before any author or producer sees them, and the writer refuses on a hit, reporting line numbers only. It fails closed if its signature list cannot load.

**Why** The owner decided it as one of the exceptions. Design rationale: exposure harms the owner, and pushed history is hard to take back. It refuses the whole append here only, because a guessed partial redaction can leave a usable fragment (08 §8).

**Source** 07 Decided (the exceptions); 08 core §8; 08b §4.

#### Verifier

*Proposed · 08b §3 · spec* — L0 mechanical, L1 judge — filler today none chosen (*Open*)

**What** L0 needs no model: quotes are substrings of the cited message, anchors exist, numbers match. L1 asks whether the evidence entails the claim. L1 never overrides an L0 failure and never promotes a fact on its own.

**Why** Design rationale: NLI-style judges are weak (survey §4, cited in 08 §6.3), so mechanical L0 checks come first and L1 never overrides them. L1 is mandatory for auto and mined episodes: the first content review found 10 of 74 auto-authored entries with an unsupported claim, and the retest after the fix 1 of 20 (01 #21).

**Source** 08b §3; 08 core §6.3. Roles with gates are decided ("Layering"), but no decision names the verifier or its L0/L1 design, so it is drawn as proposed spec.

#### Label classifier

*Decided · O12 · owner* — routes, never filters — filler today none chosen (*Open*)

**What** Adds labels and never removes one. Its gate set is labelled by the owner, locally; the persona neither labels it nor grades the router of her own memory.

**Why** The owner decided it (O12). Design rationale: it routes the persona's own memory, so the persona must not grade it. Over-labelling only narrows flow, so its gate is recall per flow class (a Wilson lower bound of 0.95, a proposal), not precision.

**Source** 08_episode_schema O12; 08b §5.

#### Signer

*Decided · O21 · owner* — a dedicated key from a pluggable source

**What** Signs daily roots and promotion batches, and nothing else. A rotation adds a key with validity dates, and old signatures keep verifying. On 2026-11-25 the self-test passed vectors 1 to 3 of the gate's 5.

**Why** The owner decided it (O21). Design rationale: a signed root makes an edit by anything without the key visible. It is not an origin control, because a session with a shell can sign (04 §7.3, 08 §16.4).

**Source** 08_episode_schema O21 and "Signing key in place"; 08b §7.

### Over all of it: labels

Open labels (*Decided*)

Labels decide where content may flow, never whether it is kept. Live credentials are the one content never stored. The flow table

### Doors out: the only ways anything leaves

#### Invalidate

*Decided · door 1 · SRS* — unreachable; the row is kept

**What** The default, and reversible. Wrong or poisoned content takes this door: a unit retrieval can never return cannot poison anything, and its row stays as the audit's evidence.

**Why** The owner decided the three doors on 2026-08-31 (SRS), reasserted in 04 §0 and 07. Poison takes this door, because hard-deleting buys nothing at inference time and costs the evidence the audit needs.

**Source** SRS §11 (the owner, 2026-08-31); 04 §4.2.

#### Redact

*Decided · door 2 · SRS* — a tombstone with reason, time and hash

**What** The content is replaced and the record's shape survives, so the chain still verifies. For the always-loaded files, editing is redacting.

**Why** Same decision. For anything always loaded, invalidate is meaningless: a sentence in a loaded file cannot be made unreachable, so the edit is the remedy and git keeps the audit trail.

**Source** SRS §11 (the owner, 2026-08-31); 04 §7.1.

#### Purge

*Decided · door 3 · SRS* — bytes gone from every copy

**What** A runbook, never a flag: rare, logged, and only on the owner's own words. It reaches the files, history, the projection, replicas and cold archives, and leaves a tombstone with no text. The SRS excludes transcripts from purge; the successor docs do not restate it.

**Why** Same decision. Purge is for content hazard: a secret, or a wrong claim that should not sit on disk at all. It stays a rare runbook so deletion is possible but never routine.

**Source** SRS §11 (the owner, 2026-08-31); 08 core §15.4.

#### Nothing is deleted silently

*Decided · SRS frame* — supersede is not delete

**What** Only these three doors remove anything, and each one is logged.

**Why** SRS frame, reasserted in 04 §0 and 07. A store that forgets because it ran out of room is the failure never-delete exists to prevent.

**Source** SRS §1 and §11; 07 ("never-delete, the three doors": decided already); 08 core §1 principle 10.

#### Six layers, and what lives in git

*Proposed · 04 §1* — L1, L2 and L4 are kept in git; whether L0 should be is open (D10)

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

**Source** 04 §1 as amended; 07 D10; 08 §2.

## D3, as of 26 November

Currency is not decided. On 26 November it split into two questions. The owner has decided neither.

### Q1 What is a reader shown?

#### What a reader is shown

*Proposed · D3 · question 1* — D3 as written

**What** A proposed update is marked as soon as it exists. Versions are ordered newest first and dated. An outdated fact stays visible beside its successor. Recommended in 07, parked by the owner on 25 November, reopened on 26 November.

**Why** Design rationale (07, T2): when both versions were retrieved, the older ranked first in 22 of 27, because ranking follows the question's wording. T2 used 42 cases with questions written from the old fact, so it shows wording, not a preference for age. Hiding stale facts does not fix that; ordering by time does. The owner parked it to rethink it.

**Source** 07 Open, D3 (recommendation: yes); the D3 discussion, 2026-11-26.

The parts are laid out under Currency.

### Q2 Which door do sessions take?

Over 30 days, 36 percent of 324 sessions grepped the raw journal and 7 percent called recall.

#### C · Rendered projection

*Proposed · Nyx's lean · not decided* — the journal path becomes a generated, read-only tree

**What** Canonical, immutable episodes live in a store sessions are not pointed at. The familiar journal path becomes a locally generated, read-only tree with the marks inline, regenerated from the store plus the ledger, kept out of git and never indexed. Any read sees the marks, whether a grep or a whole file. As a rendering, it also removes invisible characters and badges them (08 §6.7). A three-lab review panel proposed it independently. The owner has not decided. Because it is regenerated from the ledger, it presumably rests on D4 (an inference; the brief does not say so).

**Why** The reasons given, paraphrased: every reader sees the marks, grep or whole file, with no harness hook, and episodes stay immutable. The panel's own caveats: a ranged read can still miss a mark, the canonical store stays reachable, and the tree is plumbing to maintain.

**Source** The D3 discussion, 2026-11-26; D3_panel_2026-11-26. The panel file still records the earlier lean (A, with B as fallback).

#### A · Guard the door

*Open · alternative* — a hook redirects raw reads to a rendered grep

**What** A pre-tool hook in each harness blocks raw reads of the journal and points to a grep verb that renders date, mark and quote fence on every hit. It is a habit guard, not a wall: other readers pass, and a harness without hooks gets nothing.

**Why** Panel objections, paraphrased: blocking one tool leaves every other reader open, and failing open strips the marks exactly when the library breaks. Each harness needs its own adapter.

**Source** D3_panel_2026-11-26 (option A); the D3 discussion of 26 November.

#### B · Mark the bytes

*Open · alternative* — a marks file beside the journal

**What** One derived file, regenerated from the ledger, repeats each outdated line with what replaced it, so a grep for the old wording hits both. It carries currency only, with no quote fences, and a read of a single episode misses it.

**Why** Panel objections, paraphrased: a correction file is not a mark on the stale bytes. A read of one episode never sees it, and as specified it carries accepted links only, not proposed ones.

**Source** D3_panel_2026-11-26 (option B); the D3 discussion of 26 November.

*Not the same tree*

#### Migration view

*Decided · O1 · Nyx* — Reflection first, then Record; retired after

**What** While migration runs, a generated journal file keeps legacy readers working: the legacy bodies verbatim, then new episodes with the Reflection first. It lives in the pushed tree and is retired once nothing reads it. It is a different thing from option C's local tree.

**Why** Design rationale: the view keeps every legacy reader working until each reads the directory. The Reflection comes first because that is the human reading order (O1, Nyx).

**Source** 08_episode_schema O1 (Nyx-decided); 08 core §2.2.

## One episode, one file

memory/journal/2026/11/2026-11-25-0909Z-8a0f3d42.md

```
---
schema: 1
id: "0193a1b2-7c4e-7f10-9b2d-5c1e8a0f3d42"
recorded_at: "2026-11-25T09:09:41Z"
recorded_how: "clock"
origin: "in-session"
kind: "work"
title: "orders table moved to the new schema"
session: "…"
anchor: "…"
labels: ["topic:database"]
---
## Record
- o1 outcome: the orders table runs on the new schema
  status: done
- d1 decision: migrate in two batches, behind a read-only window
  why: "a single pass would hold the lock too long"
  rejected: ["one pass", "online dual writes"]
  status: in-force
  by: joint
  ev: m:… "do it in two batches, the window is fine"
- m1 measure: rows copied in batch one
  value: 48210
  unit: "rows"
  how: t:…
  label: "rows copied"
- l1 open: drop the old table after a week
  owner: persona
  until: "no reads of the old table for 7 days"

## Harvest
- c1 change: migration script committed
  kind: commit
  state: pushed
  ref: g:…@…
  by: code

## Reflection
Prose in the persona's voice.
```

*Illustration of the shape: placeholder text, no real content. The file name's last 8 hex are the id's random tail.*

#### Times in UTC

*Decided · O3 · owner* — every stored time ends in Z

**What** Every stored time is UTC with Z, and every claimed time carries an offset. That recorded_at is stamped from the clock by code is the writer's design, which is proposed. In the legacy journal, 118 of 280 headers named a time that had not yet come.

**Why** The owner decided it (O3). Design rationale: local time is ambiguous across DST changes, and date-and-time collisions are a measured problem in the legacy journal (08 §0.2).

**Source** 08_episode_schema O3; 08 core §2.1. The clock stamp: 04 §2.2 (the writer, proposed).

#### Minted id

*Proposed · 04 §2.2 · M2* — a UUIDv7 at birth

**What** Identity never comes from a position in a file. Every episode and fact gets a stable id at birth, and the legacy date.ordinal ids are frozen in an alias table at M2.

**Why** Measured (T3b): with today's parsers an id written anywhere re-hashes 779 or 780 of 780 entries; with a tolerant parser, 1 changed in the pre-registered run (an artefact of the test) and 0 in a post-hoc check. Hence ids are minted code-first, M1 before M2. Today identity is a file position: a two-machine merge renumbered a day and five units pointed at the wrong entry (01 #2).

**Source** 04 §2.2; 06 M2; T_result_2026-11-25 (T3b).

#### Record

*Proposed · the evaluation decides* — typed items, each anchored

**What** Outcomes, decisions, facts, changes, measures, asks, preferences, corrections, open loops, lessons and entities, each checkable line by line. Its details are settled (O5 and O9 by Nyx, O2 by the owner), but whether it ships is decided by the pre-registered format evaluation. Arm B was generated on 26 November and has not been read. If the Record loses, prose plus the Harvest ship instead.

**Why** Design rationale: the gap audit found pointer-shaped failures, not narrative ones: a SHA in 7 of 40 entries, sourced numbers in 3 of 36, an owner for 14 of 28 open loops (08 §0). Only a typed block can be checked line by line. Whether it wins is measured against the fairest prose control (08d).

**Source** 08 core §4-5; 08_episode_schema O2, O5, O9; 08d §6-7 and its amendments.

#### Harvest

*Proposed · kept in every branch* — written by code

**What** Commits, pushes, files, fetched URLs, report paths and run statistics, each checked for existence at write time. The author never edits it, and the evaluation keeps it whichever way the Record goes.

**Why** Design rationale: code knows commits, files and URLs exactly, so the author never types them, and separating code-written from author-written content is what verification needs.

**Source** 08 core §5.7; 08d §7 (kept in all three branches).

#### Reflection

*Decided · 07 · owner* — prose in the persona's voice

**What** Rationale and voice. Legacy prose stays byte-for-byte as the Reflection of its session's mined episodes, and a mined episode never gets a synthesised one. A fact the memory relies on must also be in the Record.

**Why** The owner decided it. Design rationale: prose already carries the strong classes (decision with reason in 39 of 40, corrections in 33 of 40, 08 §0) and the voice; the Record carries what must be checkable.

**Source** 07 Decided (transcript-first: the old prose stays as Reflection); 08_episode_schema Decided; 08 core §7.

#### Record first in the file

*Decided · O5 · Nyx* — truncation keeps the claims

**What** The stored order is Record, Harvest, Reflection, so a reader that stops early still has the claims. The migration view shows the Reflection first.

**Why** Nyx decided it (O5). Design rationale: truncation in the pack and the roughly 480-token rerank slice keeps claims rather than prose.

**Source** 08_episode_schema O5 (Nyx-decided).

*Record item types: proposed with the Record*

`o`outcome

`d`decision

`f`fact

`c`change

`m`measure

`a`ask

`p`pref

`x`correction

`l`open

`k`lesson

`e`entity

#### Front matter: birth values only

*Proposed · 08 §3* — what code writes at birth, and what it never writes

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

**Source** 08 §3.

#### The Record's item types

*Proposed · 08 §5.4* — each line typed, each claim anchored

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

**Source** 08 §5.1, §5.4, §5.6.

#### Evidence anchors

*Proposed · 08 §5.3* — every stored anchor is a full id, resolved at write time

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

**Source** 08 §5.3.

#### What evidence may be quoted

*Proposed · 08 §6.1-6.2* — the quote corpus, the anchor and human turns

- **The corpus:** human-typed spans of human turns, tool results, and assistant text. Never tool-call inputs, thinking, or anything after the anchor.
- **No circular evidence:** a tool result is excluded when its call read or wrote an episode, the draft, the generated view, canon or the quarantine. Otherwise memory could cite itself.
- **The anchor** is the last message flushed to the transcript before the write call, so an author can never quote what it is writing. The writer waits up to 10 seconds for the flush (a proposal), and gate G0 measures whether that holds before M5.
- **Human-typed** is an allowlist of real transcript record shapes. Hook output, notifications, command output, compaction summaries, tool results and cross-session messages are never human-typed, even in a user turn. Anything attributed to the owner must anchor a human-typed span.

**Source** 08 §6.1-6.2.

#### Verification: L0, L1, statuses, eligibility

*Proposed · 08 §6.3-6.5* — results are ledger events, never file edits

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

**Source** 08 §5.8, §6.3-6.5.

#### Additions, revisions and hand edits

*Proposed · 08 §10.6-10.7, §12.2* — the file stays immutable; history grows beside it

- **Companion records** hold later additions in their own files beside the episode, never matched by the episode glob: back-fill items from legacy prose, or a nightly pass's additions.
- **revise** edits in place, re-runs the screen and labels, and records the old and new hash. Items anchor to the transcript, not to the episode text, so a revision does not orphan them.
- **A hand edit outside the writer** is found by the integrity check as a mismatch and is never accepted automatically. Until someone accepts it with `revise --accept`, the episode leaves every index, and the edited bytes are kept aside, never deleted.
- **A materially wrong episode** gets a new episode that continues and supersedes it. The old one is marked by an event.

**Source** 08 §10.6-10.7, §12.2.

#### The legacy journal, kept byte for byte

*Proposed · 08 §12* — transcript first; old prose verbatim

- Each legacy entry becomes a file of new front matter plus its original text verbatim, exempt from every heading rule.
- Its recorded time comes from the marker if it has one, else from the header in the old time zone, else from the entry before it, and it says which.
- A frozen manifest lists every legacy entry in journal order with its body hash. Rejoining them reproduces the journal's bytes as split (gate G3).
- Every in-scope session with a transcript gets mined episodes; its legacy entries are their Reflection of record. A session whose transcript is gone keeps its prose plus Pass B companions (O7).
- The credential screen runs over legacy bodies and flags, never rewrites: a credential already in history is rotated, and removing it from history is purge's job.
- Acceptance: a blind sample of 60 items per pass, at most 2 unsupported (3.9%).

**Source** 08 §12; 08_episode_schema O7.

#### Size budget

*Proposed · 08 §14 · O8* — O8 decides only the 12 KB and 25-item starting caps

| Part | Typical | Cap |
|---|---|---|
| Front matter | about 0.6 KB | 1.5 KB |
| Record | 8 to 15 items, 1.5 to 3 KB | 25 items, 6 KB |
| Harvest | at most 2 KB | 3 KB, then overflow to the ledger |
| Reflection | 0.6 to 2 KB | 3,000 soft, 8,000 hard |
| Whole file | about 4 to 6 KB | 12 KB, then split |

(*Decided*) O8 (the owner) decides the starting caps of 12 KB per file and 25 Record items, to be tuned on evaluation data. The other caps are spec. The typical sizes and the author cost of 400 to 900 extra tokens per episode are hypotheses, measured in the format evaluation.

**Source** 08 §14; 08_episode_schema O8.

## Episode file type

Which bytes an episode is stored as is not decided, and nothing in this section is. Four options are on the table; a three-lab panel agreed on only one point, and the reader test found no reader-side difference that matters on its primary score, so the choice rests on archival terms and the owner's hand reading.

#### Two questions, not one

*Open · nothing here is decided* — the stored bytes, and what a reader is shown

1. **What are the canonical stored bytes?** D1 decided one file per episode, not its type, and none of O1 to O23 touches it.
2. **What is a reader shown?** That is D3's second question, still open: the raw files, a rendered tree with marks inline, or only recall's rendering.

Nyx's first lean coupled them: the Record's serialization would follow whichever reader door D3 picked. A three-lab panel **unanimously rejected that coupling**, and it is withdrawn. The stored bytes are an archive meant to last decades; the door is a rendering that can be retired or bypassed. So the bytes are chosen on archival terms. OpenAI's terms: lossless representation, unambiguous decoding, independent implementations, versioning, recovery from corruption, inspection without tools. DeepSeek's: one simple parser, minimal custom escaping, safe hand edits, long-term readability.

**Reversible until M5.** Options 1 and 2 encode the same parsed form, and no schema-1 file exists outside the quarantine, so the choice stays cheap to reverse until the journal is split.

**The trade the owner decides:** option 2 retires the custom grammar, its percent layer and its conformance suite, and costs hand-readability, because a JSON line is harder to read than an item line.

**Source** format_panel_2026-11-26 (1e6b326): the question, the synthesis, Nyx's position now.

#### Option 1 · Today's line grammar

*Open · specified and prototyped, not adopted* — markdown, typed item lines, a percent layer

**What** A markdown file: one-line JSON values in the front matter; Record and Harvest as item lines with two-space field lines; free text through a reversible percent layer so no value can start a line, open a heading or open a comment; two independent parsers that must agree under a conformance suite; the Reflection as prose. It costs the custom grammar, its percent layer and its conformance suite for as long as the store lives. A grep hit on an item line carries neither its anchors nor its quotes, which sit on separate field lines.

**Why** Measured on 1,452 mined items from 61 episodes: the percent layer changes 19 items (1.3%), all for a literal %, and in 16 of them a literal grep across the % fails ("36% of" is stored as "36%25 of"). Size is the 1.0x baseline. Test G: real sessions grep the journal with shell grep, and only 3.4% of line-mode greps carry 3 or more context lines, so a real hit almost never brings the anchor (a habit formed on a prose journal). The panel: OpenAI says two agreeing parsers can share a specification bug; DeepSeek calls the custom grammar an ongoing parser risk; Gemini says custom grammars rot, though its claim that the percent layer destroys greppability is overstated at 1.3%.

**Source** format_panel_2026-11-26 (1e6b326) M1, M2; 08 §3-5.

#### Option 2 · Fenced JSONL Record and Harvest

*Proposed · Nyx's lean, not decided* — one JSON object per item per line, under a rigid envelope

**What** A markdown episode whose Record and Harvest are fenced JSONL, one JSON object per item per line, under a rigid envelope specification: section and fence boundaries, duplicate sections, malformed lines, duplicate JSON keys rejected, and line length. Front matter and Reflection are unchanged. It drops the custom grammar, the percent layer and its conformance suite, and a grep hit carries the whole item. It costs about 1.2x tokens on the Record, a one-line pre-processor before jq, and hand-readability: the trade the owner decides.

**Why** Measured: 1.17-1.21x tokens on the Record (1.18x characters). JSON escaping would add to the text of 8 items (0.6%: 5 hold a quote mark, 3 a backslash) and drop the percent layer's 19, so it breaks literal grep on fewer items than option 1. The panel: OpenAI prefers it whichever door wins, at medium confidence, given the rigid envelope; DeepSeek leans the same way without naming an option; Gemini calls it the worst of both worlds.

**Source** format_panel_2026-11-26 (1e6b326) M2 and the check after the answers; synthesis.

#### Option 3 · One JSON document per episode

*Open · not measured as such* — the Reflection stored as a JSON string

**What** The whole episode as one JSON document, with the Reflection stored as a string. It removes more framing than option 2, and buries the Reflection and the legacy prose in escaped strings.

**Why** The nearest measurement is pretty-printed JSON of the same items: 1.40-1.45x tokens on the Record (1.50x characters). A compact one-document form was not measured. OpenAI: it removes more framing complexity but makes prose inspection worse.

**Source** format_panel_2026-11-26 (1e6b326) M2 and the answers.

#### Option 4 · A structured file beside a prose file

*Open · not measured* — records in one file, prose in another

**What** A record file (for example JSONL, YAML or TOML) beside a prose file for each episode. It splits the one-file episode that D1 made the unit, and doubles hashing and naming: more moving parts, where the owner prefers fewer.

**Why** Gemini's alternative. Its prior art (git, auditd, Datomic) separates prose from structured logs rather than embedding a grammar inside prose files.

**Source** format_panel_2026-11-26 (1e6b326): Gemini's answer and the synthesis.

#### The same items, options 1 and 2

*Open · illustration from the panel brief* — an outcome and a decision, side by side

*Option 1, today's line grammar*

```
## Record
- o1 outcome: The index runs in WAL mode and the nightly job passed.
  status: done
  ev: m:5f1c0d2e-.../9a2e44b1-... "nightly finished with rc 0"
- d1 decision: Use SQLite WAL mode instead of a file lock.
  why: "Readers no longer block the writer."
  rejected: ["flock around every write"]
  status: in-force
  by: joint
  ev: m:5f1c0d2e-.../7b10c3aa-... "go with WAL, the lock was the problem"
```

*Option 2, fenced JSONL*

~~~~
## Record
```jsonl
{"rid": "o1", "type": "outcome", "text": "The index runs in WAL mode and the nightly job passed.", "status": "done", "ev": [{"anchor": "m:5f1c0d2e-.../9a2e44b1-...", "quote": "nightly finished with rc 0"}]}
{"rid": "d1", "type": "decision", "text": "Use SQLite WAL mode instead of a file lock.", "why": "Readers no longer block the writer.", "rejected": ["flock around every write"], "status": "in-force", "by": "joint", "ev": [{"anchor": "m:5f1c0d2e-.../7b10c3aa-...", "quote": "go with WAL, the lock was the problem"}]}
```
~~~~

Synthetic items, as sent to the panel. A grep for "WAL" hits the item line in option 1, without its evidence; in option 2 it hits the whole item, evidence included.

**Source** format_panel_2026-11-26 (1e6b326): the brief.

#### What was measured

*Open · tuning set only, counts only* — 1,452 mined items from 61 episodes

| Serialization of the same items | Tokens, vocab A | Tokens, vocab B | Characters |
|---|---|---|---|
| Line grammar (option 1) | 159,619 | 181,422 | 491,367 |
| One JSON object per item per line (option 2) | 192,837 (1.21x) | 211,292 (1.16x) | 579,535 (1.18x) |
| Pretty-printed JSON | 223,012 (1.40x) | 262,332 (1.45x) | 737,172 (1.50x) |

- **Escape layer:** the percent layer changes 19 of 1,452 items (1.3%), all for a literal %; no newlines, no comment sequences. Neither pre-registered branch fired.
- **Tokens:** JSONL 1.17-1.21x, pretty JSON 1.40-1.45x, with two open-model tokenizer vocabularies. Both predictions were too high. Full-UUID anchors dominate every serialization; shorter keys would narrow the gap. The Reflection is unchanged by any option that keeps it as prose.
- **JSON escaping:** under option 2 it would add to the text of 8 items (0.6%) and drop the percent layer's 19. Quote and string fields are JSON strings under both options already.
- **Grep hits:** the grammar's item line carries no anchor or quote; a JSONL line carries the whole item. The episode's date is in the filename under every option. (An analytic point, not a measurement.)

**Source** format_panel_2026-11-26 (1e6b326): M1 and M2 (pre-registered), and the check made after the answers.

#### What the panel said

*Open · three labs, attributed* — unanimous only on decoupling

- **Unanimous:** the stored bytes must not follow the reader door. That is the only point all three agreed on. All three were told to attack the lean, so "nobody defends option 1" is partly the prompt.
- **OpenAI** backs option 2 whichever door wins, at medium confidence, provided the envelope is specified rigidly. It also notes that the front matter is YAML whose values are JSON, not line-by-line JSON as 08 §3 words it.
- **DeepSeek** leans the same way without naming an option: option 1's custom escaping is an ongoing parser risk, and option 2 handles invisible characters more defensibly.
- **Gemini** rejects both 1 and 2: custom grammars rot, and fenced JSONL is the worst of both worlds, because jq needs a pre-processor and dense JSON is hard on the eye. Its alternative is option 4.
- **The test it would take:** OpenAI's paired, held-out measure of correct answers with correct evidence under a fixed read and token budget, with real grep and read tools, several readers, and trials with the projection unavailable. Keep option 1 only if it wins by a margin declared in advance.

**Source** format_panel_2026-11-26 (1e6b326): the answers (verbatim there) and the synthesis.

#### The deciding tests

*Open · G done · mutation not run · R done: branch C* — no reader-side difference on the primary; weak support for option 2 on the secondary

**What** G is done: real sessions grep the journal with shell grep (642 calls, against 8 for the Grep tool), and only 3.4% of line-mode greps (14 of 410) carry 3 or more context lines, so under option 1 a real grep hit almost never brings the item's anchor (a habit formed on a prose journal). The mutation-robustness test was not run: both formats hold free text in quoted strings, the integrity layer catches any byte change, and it could not move the decision. R, the reader test (32 questions, haiku and sonnet readers, shell grep, 0.10 margin), is done. Primary, evidence surfaced within 12,000 characters of tool output: option 1 0.887, option 2 0.935, delta +0.048, 95% CI [−0.048, +0.143]. That is branch C as pre-registered: no reader-side difference that matters on the primary. Secondary, final-answer evidence correct under a strict oracle (the exact anchor of the one target item): 0.887 against 1.000, +0.113 [+0.048, +0.190]. Answer correct, by a blind judge: 64 of 64 in both arms, at ceiling; a planted check found the judge rejected all 12 swapped answers and accepted all 10 real ones. Cost: 1.07x tool output per run under option 2, with fewer tool calls (1.56 against 2.37 per run).

**Why** Branch C means the choice rests on archival terms and the owner's hand reading, and the lean stays option 2. A manual re-read of option 1's 7 misses on the secondary: 1 had the right anchor wrapped in a label; 2 or 3 cited valid evidence from a different item stating the same fact; 3 cited an item label instead of an anchor (m:4, c1, x1), all by haiku; 1 is unclear. So the residual is 3 small-reader runs out of 32 that confused a label with an anchor: weak support for option 2, nothing more. The observation, untested: the small reader cited the item's label in place of its anchor. A confound: arm 2's key was named "anchor", the word the prompt used, where arm 1 writes "ev:". Two predictions were wrong: option 2 was ahead on strict evidence by 0.11, and the cost was 1.07x, not 1.2-1.6x. Three voided runs were false positives of the containment check; restored, the primary is +0.031 [−0.062, +0.125] and the secondary +0.125 [+0.047, +0.203], and no conclusion changes. Limits: 32 questions, two readers from one vendor, fresh sessions, mined items only. The owner's own hand reading is not measured.

**Source** format_tests_2026-11-26, R: results (3162208); format_panel_2026-11-26 (1e6b326).

## The write path, explained

Every episode is born through one writer, in session or from a transcript. Code drafts what code can know; the author supplies judgement; every claim is checked against the transcript before the file exists. The boxes for each part are on the map above.

#### What the writer does, in order

*Proposed · 08 §10.2, §11.2* — draft, edit, append

1. **draft** (no model call) writes a complete Record skeleton and a digest: the front matter from the session, the whole Harvest, an outcome to edit, ask and preference candidates from human-typed turns, correction candidates, findings reported live but not recorded, numbers from tool results, open loops, and changes mirrored from the Harvest.
2. The author edits it. By O9 (Nyx), code pre-fills the mechanical items and the author writes the outcome, decisions, corrections, loops and the Reflection.
3. **append** waits for the transcript to flush, runs the credential screen, labels every unit, resolves every reference to a full id, runs L0 with per-item fallback, and creates the file atomically. A collision mints a new id and retries.
4. It records an `episode.recorded` event with enough to rebuild the projection row without reading the file.

Write at a closure, a topic switch, before compaction, or when the nudge's threshold is crossed. Never rely on a session-end event: the harness does not guarantee one. A prose-only path exists (O6), flagged so a later pass mines a real Record.

**Source** 08 §10.1-10.4, §11.2; 08_episode_schema O6, O9.

#### The mining path, step by step

*Proposed · 08 §10.5* — the steps are spec; transcript-first and the order are decided

1. **Prep, code only:** the quotable corpus of each in-scope transcript, credentials redacted, numbered by message and tool id, cut at human-turn boundaries, with the Harvest written by code. One job per segment, carrying its scope labels.
2. **Mining:** the producer returns JSON items; code renders them. Facts, decisions and corrections need a snapped quote or a commit anchor; inferred items are not allowed; machine authors cannot force items; no Reflection is ever synthesised.
3. **Labels and screens:** the label classifier adds labels, the credential screen runs on every value.
4. **Quarantine:** everything lands outside git and outside memory, never indexed or read by recall, extraction, P3, the pack or the publishing path.
5. **Promotion** goes through the writer only, after the credential fixture passes, the label classifier passes its gate, the format evaluation decides the format, and M5 is done. Each batch is signed.
6. **Order** is newest first, stopping when a batch fails its gate (Transcript-first mining (*Decided*)).
7. If the format changes, the quarantine is re-mined, not converted. Deferred jobs run first when a producer that accepts them passes its gate.

Scope: every session with a transcript of at least 30 KB, except two excluded directories. Work projects are in scope with work labels. A back-filled episode's recorded time is its promotion, so SessionStart never shows a mined episode as the newest.

**Source** 08 §10.5; 08c §7; 07 (scope).

#### Credential rules

*Proposed · 08 §8* — the rule is decided; these mechanics are spec

Credential screen (*Decided*) The decision is that live credentials are always redacted. How:

- **Two places:** inputs are redacted before any author or producer sees them, and the writer refuses any value that still matches, reporting line numbers only, never the match or its class.
- **Screened:** every free-text value: front matter, every item and field, the Reflection, digests and skeletons, companions, and every changed episode file at commit.
- **One signature list**, imported, never copied; if it cannot load, nothing is written.
- **An entropy rule** catches long mixed-case tokens; it is a proposal, tuned on fixtures, and its false-positive rate is reported.
- **URLs** lose their query strings, fragments and user info before screening and storage.
- **Invisible characters first** (a proposal): the screen reads text with them removed, so a credential split by a zero-width character still matches (Invisible characters removed first (*Proposed*)).
- **Legacy bodies** are flagged, not rewritten: the credential is rotated, and removal from history goes through purge on the owner's word.

**Source** 08 §8; 08b §4; 07 (the exceptions).

#### Nightly enrichment

*Proposed · 08 §10.6* — a completeness pass that only adds

A nightly pass compares a session's final reports and key tool results against the Record, and writes what is missing to a companion record, each item anchored, screened, labelled and verified. The episode's hash is untouched. Recall shows these as added later. The docs mark it a hypothesis that this is the highest-yield pass in the first month.

**Source** 08 §10.6.

## Roles and their gates

The core never names a model. It names roles, and anything that passes a role's gate may fill it: a cloud model, a local lane, a library. No gate has run yet.

#### Every role's gate

*Proposed · 08b* — roles are decided; their gates and thresholds are proposals

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

**Source** 08b §1-9; 08c §2; 08_episode_schema (signer self-test).

## Facts: keys, not beliefs

A fact exists to get the right episode retrieved and to carry structure: subject, slot, kind and event time. Recall never serves one on its own, so a wrong fact costs a miss and a vanished producer costs only keys.

#### What a fact record carries

*Proposed · 04 §3.1, amended by 08 §11* — a key with structure, never a belief

- **Where it points:** the episode, the episode's hash at extraction and, for schema-1 episodes, the item id and its hash.
- **The quote**, anchored with a prefix and suffix so it survives edits (a W3C text-quote selector, re-attached the way Hypothesis does).
- **Subject and slot**, owned by the extractor; the author's `about:` is only a hint, and E1 tests whether it helps.
- **Kind:** durable, state, event or plan. Only states and plans can be superseded; an event stays true as history.
- **Event time** with its granularity and how it was known. Relative dates resolve against the anchored message's time, by code.
- **Mode:** stated, reported, hedged or inferred, so a hedge stays a hedge.
- **Producer:** the model, the prompt version and the run.
- **Labels:** its source item's, so a fact flows no further than its item.

For schema-1 episodes, one Record item becomes at most one fact. The density rule of about one fact per 400 characters (cap 15) applies only to the legacy prose path.

**Source** 04 §3.1; 08 §11, §11.1 items 1-5.

#### From Record item to fact

*Proposed · 08 §11* — one item, at most one fact

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

**Source** 08 §11.

#### Anchors that survive edits

*Proposed · 04 §3.2 · 08 §11.1* — a ladder of five rungs

0. The item's stable id still has a matching item hash (schema-1 episodes).
1. The episode's hash is unchanged.
2. The exact quote is found.
3. The quote with its prefix and suffix is found approximately.
4. Otherwise the anchor is orphaned: an event is logged, the fact stays and is flagged, and the next extraction pass over the revised episode supersedes it.

The ladder needs a test on Greek text under both Unicode normalisations before it is trusted.

**Source** 04 §3.2; 08 §11.1 item 3.

#### Producers are replaceable

*Proposed · 04 §3.3* — a swap re-extracts; it never overwrites

Every fact names its producer. A new producer passes the validity gate and re-extracts, writing new facts linked to the old ones. Because facts are keys, removing the producer entirely costs only the keys: finding episodes does not depend on it. The model-swap drill E8 measures whether that holds.

**Source** 04 §3.3; 05 E8.

## Currency: links, marks and a timeline

Nothing outdated is hidden. A proposed update is marked at once, the hold only closes a validity interval, and the newest version is shown first.

*Illustration · how recall would render one slot*

subject: example/service · slot: port

2026-11-206 days ago listens on 9300**newest**, shown first

2026-10-028 weeks ago listens on 9292**possibly updated** by 2026-11-20 · link proposed, hold running

2026-08-143 months ago listens on 8080**updated** by 2026-10-02 · accepted after the hold, interval closed, still shown

listens on 7000

A fact its own quote does not support is wrong, not outdated: door 1 makes it unreachable, so it never appears here, and its row stays as the audit's evidence.

The mechanism

#### Links

*Proposed · 04 §4.1 · 08 §11.1* — five relations between facts

**What** updates: the same slot gets a new value. refines: it narrows or completes the older fact. contradicts: incompatible, and neither is known to be later. coexists: judged compatible, so the pair is not judged again. closes: ends an open loop (added by the episode spec).

**Why** Design rationale: today's "partial" verdict becomes refines, which answers a Colony critique that partials are compound facts (02, theme 5). coexists is recorded so the same pair is not judged twice.

**Source** 04 §4.1; 08 core §11.1 item 6 (closes).

#### Mark at proposal

*Proposed · D3* — "possibly updated by …" at once

**What** As soon as a link is proposed, recall shows the older fact as possibly updated, with the newer episode and its date.

**Why** Design rationale: critics found the old hold served a withdrawn claim, cleanly stamped, for seven days; marks began only after the agent's own read, and deferrals waited up to 285 minutes unmarked (02, theme 5).

**Source** 07 D3; 04 §4.2.

#### The hold

*Proposed · D3* — 7 days; it closes the interval only

**What** When the hold expires, the older fact's validity interval closes, and nothing leaves retrieval. A false positive now adds a wrong note beside a true fact instead of hiding it, so the judge can be tuned for recall.

**Why** Design rationale: today a false positive hides a true fact, so the judge was tuned for precision and recall paid: 6 of 15 real supersessions found on the 92-flag review (01 #8). With nothing hidden, the hold matters less.

**Source** 07 D3; 04 §4.2.

#### Timeline, newest first

*Proposed · D3 · 04 §4.4* — grouped by subject and slot, dated

**What** Questions about now, or about a date, take the temporal path, chosen by rules. Inside a group the order is by time, not by relevance. T2 measured the problem: when both versions were retrieved, the older one ranked first in 22 of 27.

**Why** Measured (T2, 42 cases): the newer entry reached the top 10 in 29; when both were present, the older came first in 22 of 27. T2b: expanding by entry-vector similarity found the newer entry in 32 of 42 against 33 for the plain top 25, so currency needs structure, not similarity.

**Source** 04 §4.4; T_result_2026-11-25 (T2).

#### Outdated is not wrong

*Proposed · D3* — wrong takes door 1

**What** Outdated is history: still shown beside its successor, with its interval closed. Wrong means unsupported, poisoned or rejected in review: it is invalidated, unreachable and influences nothing, and its row is kept as the audit's evidence.

**Why** Design rationale: today both end as valid = 0, which mixes history with error. Wrong content takes door 1 because a unit retrieval can never return cannot poison anything, and its row is the audit's evidence (the SRS routing rule).

**Source** 07 D3 row; 04 §4.2. Door 1 itself is decided (SRS §11).

#### One judge and a same-slot rule

*Proposed · D5* — only after E2

**What** One judge call per new fact, given all its candidates. Beside it sits a deterministic rule: two state facts in the same slot with different values propose an update for the later one. This retires the readout gates, the local adjudicator and the legacy judge lanes, but only if E2 shows it is no worse.

**Why** Design rationale: today's thresholds 0.5039772 and 0.0786287 sit inside 0.055-logit gaps fitted on about a dozen positives (01 #9), and the scan costs 141-363 s per entry (01 #13). One call per fact is the main cost cut. A latest-timestamp rule tied LLM judgment on one benchmark (small n, unverified), so it is an arm of E2, not a fact.

**Source** 07 Open, D5; 04 §4.3; 05 E2.

Exposed sessions

#### Social-only updates wait

*Proposed · D6* — never accepted by the clock alone

**What** An update whose newer side comes only from sessions that read a social network stays proposed until a session or a human decides. A poisoned update can add a note, but it cannot retire a true fact by waiting out the hold.

**Why** Design rationale: the poisoning literature says only provenance assigned at write time, with a hard cap on what untrusted content may do, has evidence behind it (survey §6, cited in 04 §7).

**Source** 07 Open, D6; 04 §7.2.

#### And web sessions?

*Open · shadow count* — does the same rule cover them?

**What** Web-exposed sessions are 37% of the total. The scope of the rule is fixed by a shadow-period count, in E2's pre-registration, before the rule is armed.

**Why** Why it is open: web sessions are 37% of the total, so the rule's cost is unknown until a shadow period counts the updates it would hold.

**Source** 07 D6; 04 §7.2.

Still to be measured

#### Consistent slots?

*Open · E1* — can an extractor assign them reliably?

**What** Currency as a join rests on it. If it fails, candidates come from entity plus cosine, and the judge carries more weight.

**Why** Why it matters: T2b showed similarity alone does not surface the newer fact, so the design rests on structure, and slots are that structure.

**Source** 04 §11 item 1; 05 E1.

#### Do readers act on it?

*Open · E6* — ordering is structure; acting is behaviour

**What** Ordering by time is built in. Whether a reader then answers from the newer fact is measured end to end, against a no-correction control.

**Why** Why it matters: the survey reports readers fail to act on updates they have retrieved (STALE, survey §4), so ordering by time is not proof that anyone uses it.

**Source** 04 §11 item 2; 05 E6.

#### Candidates and the judge, step by step

*Proposed · 04 §4.3 · D5* — rank narrow, judge wide

1. **Candidates** for each new state or plan fact: earlier facts with the same subject and slot first, then the top 8 by cosine on the same subject, filtered to the same category.
2. **One judge call per new fact**, given its candidates with dates and quotes, returning a relation for each.
3. **The deterministic rule:** two state facts in the same slot with different values propose an update for the later recorded one, whatever the judge says. Clock-stamped times make that safe.
4. **Author hints** (a supersedes key) add candidates and are never accepted automatically.
5. **Shadow logging:** every judge answer is an event with its prompt fingerprint, so a re-fit is a replay. A failed call leaves the candidate unjudged until the next night.

The same-category filter was challenged and survived: 11 of 12 positives kept against 9 of 12 without it (01 §4). Cosine recall at 5 is 10 of 19, which is why same-key candidates come first (08 §11.1).

**Source** 04 §4.3; 08 §11.1 items 6-7; 01 §4.

#### The temporal path

*Proposed · 04 §4.4* — chosen by rules, ordered by time

1. A question about now (now, still, currently, and the Greek ακόμα, πλέον, τώρα) or about a date or range takes this path. Intent comes from rules, not a model.
2. Retrieve as usual.
3. Collect the facts of the retrieved episodes, follow updates and refines links forward, and pull in later facts of the same subject and slot: at most 10 extra episodes.
4. Group by subject and slot, or by episode. Inside a group, order newest first, with each date and an age, and mark older items as superseded or possibly superseded with the link's state.
5. For a date, filter on event time where known and recording time otherwise, and say which clock was used.

**Source** 04 §4.4.

## Retrieval: how recall finds an episode

The read path keeps the measured core, fixes what is broken, and adds facts as keys. Every hit comes back as an episode with its evidence, date and age.

Keyword leg (*Proposed*)+Vector leg (*Proposed*)→Score fusion (*Proposed*)+Fact-key lane (*Proposed*)→Reranker (*Proposed*)→Timeline, newest first (*Proposed*)→Recall (*Proposed*)

#### Keyword leg

*Proposed · 04 §5* — FTS5, kept in sync by triggers

**What** FTS5 over the title, the body and a column of Record text, kept in sync by triggers that issue the FTS 'delete' command with the old values. The audit gains the integrity check it lacked.

**Why** Measured (T0): the broken sync cost 0.050 MRR. D0 already fixed it in the incumbent; the successor builds the sync correctly from the start.

**Source** 04 §5, §8.4; 08 §11.1 item 10.

#### Vector leg

*Proposed · incumbent · measured* — one bge-m3 vector per episode

**What** Dense vectors from bge-m3, one per episode, kept until a challenger beats it. Chunk vectors stay off until a gold set that covers today's corpus re-tests them.

**Why** Measured: a bake-off on 2026-08-09 chose bge-m3 with the reranker below (held-out MRR 0.934 on a 121-pair bilingual set). Chunk vectors lost at 105-125 entries (paraphrase MRR 0.655 to 0.615); the corpus is seven times larger now, so a re-test on new gold would be legitimate (01 §4).

**Source** 04 §0, §5. 07 lists "the incumbent encoders" as decided already, but the SRS records the choice as a bake-off result (2026-08-09) that superseded its own "keep nomic", not as a decision in the owner's words.

#### Score fusion

*Proposed · 04 §5* — vector weight 0.30 in English, 0.60 in Greek

**What** Min-max fusion of the keyword and vector scores, with the weight set by the query's language.

**Why** Measured: score fusion beat rank fusion, 0.818 against 0.604 paraphrase MRR on 22 pairs. The language weight is noise-level with the reranker but helps the degraded path.

**Source** 04 §5; 01 §4.

#### Fact-key lane

*Proposed · E4* — each fact hit maps to its episode

**What** Keyword and vector search over fact text. A fact hit returns its episode with the fact's score, never the fact alone.

**Why** Key expansion as in LongMemEval, recalled from the paper and not re-verified by the survey's skeptic, so a hypothesis until E4 shows a gain with a lower bound above zero.

**Source** 04 §5 step 2; 05 E4.

#### Reranker

*Proposed · incumbent · measured* — bge-reranker-v2-m3 over the top 25

**What** Reranks the union of episode hits and fact hits, kept until a challenger beats it. Its conclusions here are fragile, so a Qwen3-Reranker comparison on Greek waits for the new gold set.

**Why** The native reranker beat its GGUF build (0.913 vs 0.846) and language-routed reranking (01 §4).

**Source** 04 §0, §5. Chosen by the 2026-08-09 bake-off, which superseded the SRS's "defer reranker"; no decision in the owner's words was found.

#### Token-sized slices

*Proposed · E4* — about 480 tokens, not 3,000 characters

**What** The rerank slice becomes the Record plus the Reflection lead at about 480 tokens.

**Why** The service reads 512 tokens and the client sends 3,000-character slices, so Greek is likely truncated (inferred, 01 #17). E4 keeps the change only if the Greek bucket gains.

**Source** 04 §5; 08 §13; 05 E4.

#### Greek keyword search

*Open · E5* — BM25 scores 0.154 on Greek, 0.792 on English

**What** Candidates: unicode61 with remove_diacritics 2, a trigram tokenizer, and bge-m3's own sparse weights, which need no new model. If several pass, the cheapest wins.

**Why** unicode61 does not stem an inflected language, so Greek recall rides on the vector leg and the reranker today. Whether unicode61 folds Greek accents is unverified.

**Source** 04 §5; 05 E5; 01 #18.

#### Latency budget

*Proposed · 04 §5 · Rule A* — warm p50 under 0.5 s, cold p95 under 1.5 s

**What** Measured on 200 real prompts replayed from the prefetch log.

**Why** Today's warm median is 0.36 s, and the cold tail is the reranker loading. The fact lane adds one keyword query and one brute-force vector search, inside a 0.32 s simulated median at 6,000 episodes.

**Source** 04 §5; 05 §4 Rule A item 4.

#### Recall writes nothing

*Proposed · 04 §5 · Rule A* — checked under inotifywait

**What** Indexing runs under a lock into the projection. A recall never touches the episodes or the ledger.

**Why** Today a recall can stamp markers into the journal and rebuild synchronously (01 #5, from an audit).

**Source** 04 §5; 05 §4 Rule A item 3.

#### When a part fails

*Proposed · 04 §10* — what the reader gets, and the fallback

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

**Source** 04 §10. The embedder-down figure (about 0.72 MRR if the reranker is also down) was measured by the read-path audit, not re-measured here.

## Delivery: how memory reaches a session

The store is half the system. The other half is what a session actually loads: the pack at start, recall when asked, the files it greps, and the always-loaded canon. The pack, recall, prefetch, raw files and canon boxes are on the map; two more parts live here.

#### Canon currency

*Proposed · 04 §6.2* — an accepted update to a cited fact is announced

**What** When an updates link is accepted against a fact that a P3 line cites, the next SessionStart says so: the line, the fact and the update.

**Why** Audit check (g) already detects this case, but nothing tells a session. The Colony's top theme was marks with no reader that acts on them (02, theme 1).

**Source** 04 §6.2.

#### Pointer audit

*Proposed · 04 §6.3* — a weekly census of every path and command named

**What** Every path, flag and command named in the always-loaded files and the second-level indexes is resolved against the thing itself: exists, moved, dangling or retired. Pointers into notes only are marked unconfirmed. Identity prose is out of scope, because it has no source to resolve against.

**Why** Colony critics found 59 of 69 standing pointers led only to notes (02, theme 2).

**Source** 04 §6.3.

## Labels and flow

#### Open labels

*Decided · owner* — topic: · obligation: · and others

**What** An open, namespaced vocabulary. Anyone may add a label; only the owner's own words can remove or narrow one. Labels decide where content may flow, never whether it is kept. They are routing keys: never used for ranking, and never a change to the content.

**Why** The owner decided it. The design is invariant to what makes a subject sensitive (security, CVEs, politics and so on), so the vocabulary is open rather than a fixed scale.

**Source** 07 Decided; 08 core §9.1.

#### Flow table

*Decided · O23 · owner* — label → sink → allow or deny

**What** Deny beats allow, and a unit flows only where all its labels allow. Owner sessions and recall are never denied. The core says a label no row names reaches owner sessions only; the profile's table also lets it reach canon, so the two disagree.

**Why** The owner confirmed the table as shown (O23).

**Source** 08_episode_schema O23; 08 core §9.3 (rule 4); 08c §5 (last row).

#### Exposure relative to origin

*Decided · O23 · rule 11* — no new exposure comes free

**What** Content may always go back to the provider it came from, and to local models. Every other provider is decided by the label row. The trusted-provider set is empty.

**Why** The owner decided it (O23). Design rationale: sending content back to the provider it came from exposes nothing new, so mining a transcript with the model that produced it is free by origin, not by a special case.

**Source** 08_episode_schema O23; 08 core §9.3 rule 11; 08c §5.

#### Any label may reach canon

*Decided · O22 · owner* — the guard acts at the post

**What** Canon is not a public surface, so the publishing guard checks outgoing text at the post instead of blocking labels at canon.

**Why** The owner's decision (O22).

**Source** 08_episode_schema O22.

#### Publishing guard

*Decided · O22 · core §9.5* — refuses posts that quote memory

**What** It reads every store, whatever the labels, and refuses a post that quotes or paraphrases any of it. It fails closed. Its paraphrase threshold is a proposal.

**Why** Design rationale: a guard that cannot see something cannot refuse to quote it, so it reads every store whatever the labels, and fails closed when a store is unreadable.

**Source** 08_episode_schema O22 (the guard checks outgoing text at the post); 08 core §9.5, within the labels-and-flow mechanism the schema lists as decided (§9.1 to §9.5).

#### Obligations

*Decided · owner* — partition, export, purge

**What** For a real duty to a third party: a local-only, encrypted partition, export by label, and purge through door 3. None is registered today.

**Why** The owner decided the mechanism. No obligation is registered today, so the machinery stays in the core for a real duty.

**Source** 08_episode_schema Decided; 08 core §15; 08c §6.

#### Partition encryption

*Proposed · O19 · moot today* — a LUKS2 container is recommended

**What** Listed as open in the schema index. It is moot while no obligation exists.

**Why** Recommendation: a LUKS2 container, its key in the credential store. Moot until an obligation exists.

**Source** 08_episode_schema Open, O19.

*Where each kind of label may go, today*

Flow table (*Decided*)

| Label | Owner sessions and recall | SessionStart pack | Public surfaces | Other providers | Local models | Private remote | Export | Canon |
|---|---|---|---|---|---|---|---|---|
| Unlabelledthe default row | ✓ | ✓ | ✓1 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `topic:*`subjects such as security or a CVE | ✓ | ✓ | ✕2 | ✓ | ✓ | ✓ | ✓ | ✓ |
| `rights:employer:*`work material | ✓ | ✓ | ✕ | ✕ | ✓ | ✓ | ✓ | ✓ |
| `obligation:*`none registered today | ✓ | ✓3 | ✕ | ✕ | ✓ | ✕ | ✓ | ✓ |
| A label no row namesuntil a row names it | ✓ | ✕ | ✕ | ✕ | ✕6 | ✕4 | ✕ | ✓5 |

✓ allow · ✕ deny. Deny beats allow, and a unit flows only where every one of its labels allows.

1 Only through the publishing guard, which refuses any post that quotes or paraphrases memory. 2 Unless the owner overrides one specific post. 3 While the partition is open. 4 The push stops and names the label; nothing is lost. 5 The profile allows canon here, while core rule 4 says such a label reaches owner sessions only: the docs disagree. 6 The profile denies local models here, while core rule 11 makes a flow to a local provider free of the label policy: the docs disagree.

"Other providers" means any provider the content did not come from, that is not local and not trusted. Some label namespaces and rows of the deployment's policy are left out of this copy.

To its origin provider**Free** The content was already exposed there; sending it again exposes nothing new.

To local models**Free, by rule 11** The owner's own hardware. The profile's Local models column still denies a label no row names (note 6). The trusted-provider set is empty.

To any other provider**The label row decides** The "Other providers" column above.

#### Injection exposure

*Proposed · D6* — clean · web · social · unknown

**What** A separate axis from flow: how far content can be trusted, computed by code from the session's tool calls. Since September: 59% clean, 37% web, 4% social. A P3 line must cite a fact from a clean episode.

**Why** Recommendation (D6). Measured over 375 sessions since September, main-session tool calls only (subagent reads are unseen, so exposure is undercounted): 59% clean, 37% web, 4% social. The design reads that as: the P3 gate should rarely bind.

**Source** 07 Open, D6; 04 §2.4, §7.1. The episode spec (08 core §9.7) already applies these gates "unchanged".

A second, separate axis. Flow labels say where a memory may go; injection exposure says how far it can be trusted, given what the session read. It gates canon and currency, never flow. The provider rule above is decided; these tiers are not.

#### Sinks: where content can go

*Decided · 08 §9.2 · owner* — the core names the kinds; the profile names instances

- **Owner sessions and recall:** never denied by any row.
- **The SessionStart pack** and any other unprompted injection.
- **Public surfaces:** social posts, public repositories, any publishing tool. A session started to publish is a public surface for everything it receives.
- **Model providers**, judged relative to the content's origin; every session is also a provider sink.
- **Local models**, for uses other than the guard roles.
- **Remote git hosts**, by remote. Storage is a flow.
- **Export**, a bundle on the owner's request.
- **Canon**, which reaches every session that loads it.

**Source** 08 §9.2; 08c §5; decided with labels and flow (08_episode_schema).

#### The flow rules

*Decided · 08 §9.3 · O23* — eleven rules, deny beats allow

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

**Source** 08 §9.3; 08c §5; 08_episode_schema O23.

#### Where flow is enforced

*Decided · 08 §9.5* — in code, never in a prompt

- **The retriever** takes its sink as a parameter and filters in its query.
- **The publishing guard** reads every store whatever its labels, refuses verbatim and paraphrased quotes, and fails closed.
- **The pack builder** computes flow per unit.
- **The provider gate** checks every call that sends memory to a model; a mining job's scope labels must allow its producer.
- **The push gate** checks the remote is a private replica and nothing staged denies it.
- **Guard roles see everything** and publish nothing; a profile that fills one with a lane some row denies is refused at load.
- The planted flow and guard tests (G1, G2) block migration.

Labels never affect retention, the owner's recall or verification. Over-labelling only narrows flow. Producer refusal is topic-blind. Credentials are not a label.

**Source** 08 §9.4-9.5.

#### Obligations in full

*Decided · 08 §15 · owner* — storage, export and purge beyond flow

- An obligation label marks material under a duty to a third party. It narrows flow like any label, and adds three semantics: export by label, purge on request, and a default storage place.
- **The partition:** one per obligation, local only, encrypted at rest with its own key, never pushed. Everything derived from it stays inside: facts, vectors, projection rows, digests, P3 candidates. The pushed ledger carries nothing about it, not even counts.
- **Recall** works while the partition is open; a closed partition is reported, never skipped silently.
- **Purge** reaches every copy, leaves a text-free tombstone, and destroys the partition key for copies that cannot be edited in place.
- Today the registry is empty. How a partition is encrypted is O19 (Partition encryption (*Proposed*)).

**Source** 08 §15; 08c §6.

## Identity and safety

The agent now reads untrusted pages and a social network, so what it remembers from them must not be able to rewrite who it is. Origin is assigned by code at write time, and untrusted origin caps what content may do. Text no reader sees is removed before anything inspects or renders it. The exposure tiers and the social-only update rule are under Labels and Currency.

#### P3 gates

*Proposed · D6 · 04 §7.1* — a clean citation, and no open update

**What** A P3 line must cite a fact from at least one clean episode; a pattern seen only in exposed sessions is promoted by a session or a human, never by the pipeline alone. A candidate whose cited facts have an open updates link waits. P3 itself stays auto-written and audit-gated, as the SRS decided on 2026-08-31.

**Why** This is the hard cap on what untrusted content may do (survey §6). P3 already needs two entries on two days and 59% of sessions are clean, so the gate should rarely bind; the shadow period counts how often.

**Source** 04 §7.1; 07 D6; 08 §11.1 item 8 (promotion is a flow to the canon sink).

#### Signed writes as an origin control

*Proposed · rejected · 04 §7.3* — a session with a shell can sign

**What** HMAC-signed writes need a key the model cannot read. Here the agent runs a shell as the user, so origin is enforced by code paths instead: only the writer and the classifier set it, and the audit checks it.

**Why** An architecture where the shell cannot reach a secret was measured dead on this machine on 2026-08-25. A signature the signer's adversary can make defends nothing.

**Source** 04 §7.3; 08 §11.2 keeps the rejection and adopts a signature only for integrity roots.

#### External quotes are fenced

*Proposed · 08 §6.7* — web and social quotes are data, never instructions

**What** Quotes from web or social anchors render inside a block labelled as quoted external data: at most 25 words each and two per hit, both proposals.

**Why** A quote from an untrusted page must never read as an instruction to the session that recalls it.

**Source** 08 core §6.7; 04 §5 step 5.

#### Persona probe set

*Proposed · 04 §7.4 · E7* — about 40 scenarios, run on every model swap

**What** Scenarios drawn from canon, with conduct-level rubrics rather than checklist items, run on every model or substrate swap and at long-session checkpoints. A smoke alarm, not a proof of identity.

**Why** A checklist score proves nothing about conduct (02, theme 8), and fidelity decays over 100+ turns (survey §6). E7 checks it detects anything: canon loaded against canon withheld.

**Source** 04 §7.4; 05 E7.

#### Invisible characters removed first

*Proposed · 08 §5.1 · proposal* — text no reader sees

**What** The set is Unicode's Default_Ignorable_Code_Point, written out as fixed ranges so every host uses the same one: tag characters, bidi controls, zero-width characters, variation selectors and blank fillers. Wherever text is normalised or inspected, they are removed first and NFC comes after. The writer removes them from every value it writes and records the count as n_invisible; emoji glue, bounded so it cannot hide a payload, is removed but not counted. Every rendering removes them before any fence, mark or badge, and shows the badge invisible:<n>. Contested: all three labs of the format panel contested removal. It destroys evidence, ZWJ and ZWNJ carry meaning in some scripts, and removal plus NFC can make different strings identical. Their alternative is to keep originals, escape visibly, and remove only in derived views. Challenged; rewrite paused until the file-type decision.

**Why** They display as nothing, so text that carries them can say something no reader sees, and NFC and whitespace folding keep them. Removing them after a step would let them split what that step exists to catch: a comment opener, or a credential with a zero-width space inside it. Measured baseline, 30 days to 2026-11-26: 76 of 572 transcripts held any; 562 characters, 540 of them in tool results and 184 of them emoji glue; no tag characters. The journal holds one, a U+202E.

**Source** 08 §5.1, §5.2, §6.3, §6.7, §8 rule 4 and §18 (769f298); 08b §4; 08d amendment of 2026-11-26. Added at the owner's request on 26 November; every part is marked proposal.

#### Does the evaluation's G5 take the split credential?

*Open · 08d G5 · the owner's call* — the format evaluation's credential gate

**What** Core §8 and the 08b role gate add a credential split by U+200B to the credential fixture, from implementation onward. The format evaluation's G5 runs as pre-registered. G5 runs on every arm, so adding the fixture there now would change a run after the first decision-set generation, which the pre-registration rule flags as exploratory.

**Why** It is the owner's call, and it has no answer yet. Until it does, G5 runs as pre-registered. The docs make no recommendation.

**Source** 08d amendment of 2026-11-26, as corrected in 889e97b; 08 §8; 08b §4.

#### Where the invisible-character rule applies

*Proposed · 08 §5.1 and across* — removal first, everywhere text is inspected

**Contested.** All three labs of the format panel contested removal: it destroys evidence, ZWJ and ZWNJ carry meaning in some scripts, and removal plus NFC can make different strings identical. Their alternative: keep originals and escape visibly, removing only in derived views. Challenged; rewrite paused until the file-type decision.

- **The set:** `U+00AD, U+034F, U+061C, U+115F–1160, U+17B4–17B5, U+180B–180F, U+200B–200F, U+202A–202E, U+2060–206F, U+3164, U+FE00–FE0F, U+FEFF, U+FFA0, U+FFF0–FFF8, U+1BCA0–1BCA3, U+1D173–1D17A, U+E0000–E0FFF`. General category Cf is not the set: it includes visible characters and misses unassigned ones.
- **Order:** removal comes before every other step, and NFC after it: in quote folding, the credential screen, the escape layer and every rendering.
- **The writer** removes them from every value, and from the Reflection and raw body of every non-legacy episode, and records `n_invisible` in `episode.recorded`. It removes rather than refuses because emoji are built from some of them. **Emoji glue** is removed too and not counted, and it is bounded so that no glue form can carry a payload uncounted: one ZWJ between two pictographs (a skin-tone modifier counts with the character before it); one VS15 or VS16 per base, or before a keycap; a subdivision flag of 2 to 7 tag letters or digits, then its terminator. Anything longer is counted: a run of joiners, a second selector on one base, a tag run that is not a flag.
- **Legacy bodies** stay verbatim. At M5 a legacy body holding any character other than glue is recorded as `episode.flagged {reason: "invisible", count}`, and every rendering removes them.
- **The commit step** counts them in every changed episode and companion file, because hand edits bypass the writer. It flags and never blocks.
- **L0** folds both sides after removal. That nearly always turns a failing quote into a passing one rather than the reverse; the exception is where a U+034F had kept two characters from composing under NFC, so that a quote of one of them alone now fails. The format evaluation's runs keep their recorded L0: changing it would alter which arm-B items are withheld and make the decision run exploratory.
- **Rendering:** recall, the pack, ambient recall and any rendered projection of the journal remove them and badge `invisible:<n>`, so option C inherits the rule. The generated view's legacy part is the one exception, because it must stay byte-identical.
- **The credential screen** reads text after removal, so a credential split by a zero-width character still matches. The spec's fixture and the role gate add one split by U+200B from implementation onward; the format evaluation's G5 runs as pre-registered, and whether it takes the new fixture is open (Does the evaluation's G5 take the split credential? (*Open*)).

Every part of the rule is marked proposal in the spec. A new risk row tracks it through `n_invisible`, the flags and the badge counts.

**Source** 08 §2.2, §5.1-5.2, §6.3, §6.7, §8 rule 4, §13, §17, §18; 08b §4; 08d amendment of 2026-11-26.

## Ledger and integrity

Detect, attest, repair. The chain, the signed root and the repair are decided; the single ledger they are drawn on is still a proposal (D4).

*Ledger lines, one chain per machine · illustration*

seq 18229 · data_sha256 9f2c… · prev 41ab…

seq 18230 · data_sha256 07de… · prev e3c9…

seq 18231 · data_sha256 c3a7… · prev 5b62…

**Daily Merkle root** over every file and ledger segment

**Signature** a dedicated key, used for nothing else

**Replicas** a damaged file heals from a copy that matches

#### Hash-chained ledger

*Decided · integrity · owner* — every file's expected hash

**What** Each ledger line carries the hash of its data and of the line before it, one chain per machine. Every file's expected hash is recorded, so a silent change is found. The chain covers the hash of the data, not the data, so a purge tombstone does not break it.

**Why** The owner decided it. Design rationale: the owner asked for error correction and tamper-proofing; what a design can honestly deliver on disks the owner controls is tamper-evident, attributable and recoverable (08 §16).

**Source** 07 Decided ("Integrity is layered"); 08 core §16.1. It is drawn on the D4 ledger, which is only proposed.

#### Signed daily root

*Decided · integrity · O21* — one Merkle root per machine per day

**What** Each day a machine computes a Merkle root over its files and ledger segments and signs it. Once a signed root sits on replicas an editor does not control, rewriting history shows.

**Why** Design rationale: one leaf per file and per segment, so a past root can be recomputed from the ledger alone. Prefixes keep a leaf from posing as a node, as in RFC 6962.

**Source** 07 Decided; 08 core §16.1-16.2; O21.

#### Repair from replicas

*Decided · integrity · owner* — parity only for cold archives

**What** A file that fails its expected hash is replaced from a replica that matches, and the mismatching bytes are set aside, never deleted. A mismatch is never accepted automatically, and purge tombstones are checked before anything is restored. The cadence and the grace period are proposals.

**Why** The owner decided it. Design rationale: the filesystem's checksums detect corruption, but a single device cannot repair it, and parity on a live, often-written tree costs more than it saves.

**Source** 07 Decided; 08 core §16.3; 08c §8.

#### Tamper-evident, not tamper-proof

*Decided · the honest limit* — on disks the owner controls

**What** Anything running with the key holder's rights can sign. The signature catches edits by anything without the key, and history rewritten after a signed root reached other replicas. It is not an origin control.

**Why** Stated as part of the decided integrity design, so nobody reads more into the signature than it gives.

**Source** 08_episode_schema Decided (integrity "with the honest limit stated"); 08 core §16.4.

#### Every ledger event

*Proposed · 04 §8.1 · 08 §17* — a closed, versioned list

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

**Source** 04 §8.1; 08 §16.1, §17.

#### The projection's tables

*Proposed · 04 §8.2 · 08 §11.1* — rebuilt from episodes and the ledger

- `episode` with its keyword and vector indexes; `record_item` for each Record line; `unit_label` for labels, used as filters, never as ranking features.
- `fact` with its keyword and vector indexes, and a `raw` column that keeps every imported record verbatim.
- `link`, `session` (disposition and exposure), `canon_line`.
- Views: `fact_validity`, `currency`, `open_item`.

The raw column exists because T3c found 14 unit fields outside the typed columns: the raw record must stay the source, and typed columns only an index.

**Source** 04 §8.2; 08 §11.1 item 10; T_result T3c.

#### Concurrency, stated plainly

*Proposed · 04 §8.3* — who can collide with whom

- Ledger writers serialise on a lock.
- Episode writers never collide: each writes a new file.
- The projection has one writer at a time under its own lock; readers use WAL.
- The nightly holds a stage only when a file that stage writes is dirty, which in the successor means only the canon files P3 appends to.
- Across machines, order is exact within a host and by time across hosts; the audit flags inversions over five minutes.

**Source** 04 §8.3, §10.

#### What the audit checks

*Proposed · 04 §8.4* — each check has a planted fault in its test

- source links resolve; anchors hold or are flagged;
- validity per producer; P1 coverage; P3 lines by hash;
- every committed ledger segment is a byte prefix of its working copy;
- the FTS integrity check with rank = 1, today's missing check;
- every event is of a known type and schema version;
- the integrity verify of 08 §16.2.

Every check prints its population, its opportunity count and what it did not cover, and its planted-fault test runs every time, not once.

**Source** 04 §8.4; 08 §13.

#### Statements, keys and verification

*Decided · integrity · O21* — detect and attest

- **Statements:** a daily root per host, and one per promotion batch, each naming the last ledger line it covers so the state it describes can be reproduced.
- **Signing:** only hosts the profile names as signers sign. A host without the key writes its root unsigned, and the next signed root that has merged its segments covers it.
- **Keys:** public keys sit in an allowed-signers file with validity windows. A rotation is signed by the outgoing key, and old signatures keep verifying for their dates.
- **Verify** checks five things, reporting by path and code, never content: every host chain is intact and every committed segment is a prefix; every live file matches its expected hash and nothing unknown sits in the globs; every root recomputes; every signature verifies for its date; signed roots agree across replicas.

**Source** 08 §16.1-16.2; 08b §7; 07 (integrity is layered).

#### Repair and cold archives

*Decided · 07 · owner* — heal from a replica; parity only for cold media

- A file that fails its expected hash and is still unaccepted after one verify cycle is replaced from a replica copy that matches. The bad bytes are moved aside, never deleted.
- Purge tombstones are checked first, so a purged file is never restored.
- A broken ledger segment heals the same way.
- With no matching replica the file is reported unrecoverable, the cold archive is tried, and the damaged copy is kept.
- Cold archives are snapshots at a signed root with about 10% Reed-Solomon parity, for media where no replica may exist. A restore runs parity repair, then checks the signature, each file's hash and the tombstones.

The replicas are decided: the private corpus remote, a NAS mirror (not yet set up) and the existing backup. The verify cadence, the grace period and a monthly archive are proposals.

**Source** 08 §16.3; 08c §8; 07.

## Doors out, explained

Nothing is deleted silently. Invalidate, redact and purge are three different operations, and which one applies depends on how a layer reaches the model. The three door boxes are on the map.

#### Which door, by layer

*Decided · SRS §11 · owner* — the remedy depends on how the layer reaches the model

| Layer | Reaches the model | Remedy |
|---|---|---|
| Always loaded (persona documents, memory index) | every turn, whole | edit, which is redaction; git keeps the trail (reasserted in 04 §7.1) |
| Retrieved (episodes, facts) | only when recall returns them | invalidate: unreachable is harmless, and the row feeds the audit |
| Derived indexes | rebuilt from source | rebuild, not delete |
| Ground truth (transcripts) | never loaded | excluded from purge in the SRS; not restated in the successor docs |

**Routing:** poison takes door 1, because retrieval poisoning is a reachability problem and hard-deleting erases the evidence the audit needs. Door 3 is for content hazard. Purge stays a runbook: rare, logged, human-triggered, never automatic.

**Source** SRS §11 (the owner, 2026-08-31); 04 §0, §4.2, §7.1.

## Migration: eight reversible stages

Identity before data, shadow before cutover, measurement before retirement. Every stage has a check that it worked, a check that it can be undone, and a gate for the next. All of it is proposed.

#### M0 · Preconditions

*Proposed · 06* — the FTS fix (done as D0) and gold set v2

**What** Two incumbent tasks: fix the FTS sync and add the integrity check (decided and live as D0), and build gold set v2, which every later gate needs.

**Why** Every stage after it is judged on the new gold set; the FTS fix belongs to the incumbent, so no gain from it may be credited to the successor (05 §4).

**Source** 06 M0; 07 D0.

#### M1 · One grammar, code first

*Proposed · 06* — one module owns every header and marker grammar

**What** Every consumer imports one parser instead of carrying its own regex. Works when the old and new parsers agree on every entry. Gate: T3b's post-hoc check reproduced on the live file, with no hash changing.

**Why** About nine copies of the header grammar and four of the marker grammar exist today, three of them commented "keep in lockstep" (01 #10).

**Source** 06 M1.

#### M2 · Mint ids

*Proposed · 06* — one commit; ids frozen in an alias table

**What** Adds an id to the first session marker of every entry and writes a frozen alias table from the old position ids. Works when all 780 content hashes are unchanged and the next nightly re-distils nothing.

**Why** Identity by position re-points everything downstream on any insertion (01 #2).

**Source** 06 M2.

#### M3 · The ledger, in shadow

*Proposed · 06 · D4* — import raw, then dual-write for 14 nights

**What** Every derived file is imported raw with its original times, the projection is built, and each incumbent writer also appends to the ledger. Gate: 14 consecutive nights of byte-identical re-exports. Undo: stop dual-writing; the incumbent never stopped being canonical.

**Why** T3c showed the import can be lossless to the byte; the shadow period proves it on live writes.

**Source** 06 M3; 07 D4.

#### M4 · The read path, behind a flag

*Proposed · 06* — the new recall runs beside the old

**What** The new recall indexes from the projection and adds temporal assembly. The prefetch hook logs both rankings and injects neither. Consumers switch one at a time once Rule A holds on the sealed held-out split.

**Why** Shadow before cutover: every consumer can point back to the old library until the gate.

**Source** 06 M4; 05 §4.

#### M5 · Episode files

*Proposed · 06 · D1* — split the journal; the writer becomes the only path

**What** One commit splits the journal into episode files; the old path stays as a generated, read-only view until nothing reads it. Gates include the byte-exact rejoin, the flush and anchor measurement, the human-turn fixtures, flow and credential fixtures, the publishing guard reading every store, and the integrity drill.

**Why** D1 is decided. The risk the docs name: a split the publishing guard does not follow would silently switch the guard off, so the guard must read the directory before the view can retire.

**Source** 06 M5, amended by 08 §11.3.

#### M6 · Facts v2

*Proposed · 06* — re-extract with anchors, slots and event time

**What** Additive: new facts link to the units they succeed, and the old units stay raw in the ledger. For schema-1 episodes the input is the Record, one item to at most one fact.

**Why** Gated on E1 and E3; E4 decides whether the fact lane is on.

**Source** 06 M6; 08 §11.3.

#### M7 · Currency v2

*Proposed · 06 · D3 · D5* — links, marks and the hold

**What** The 42 applied supersessions and 26 stale marks are imported as accepted links with their original times. New candidates come from slots and cosine, with one judge per new fact plus the same-slot rule.

**Why** Only after E2 shows the new judge is no worse do the old readouts and adjudicator retire.

**Source** 06 M7.

#### M8 · Retirement

*Proposed · 06* — one commit per retired part, quoting its measurement

**What** The readouts and the adjudicator (E2), the separate chain file (M3), stamp's journal rewrite (M5), the separate units lane (E4), the old currency notes (M4) and the cursor file (M3). Code moves to a retired folder; files freeze read-only. Nothing is deleted.

**Why** Each part survives or retires on a measurement, never on taste.

**Source** 06 M8. "The hash chain" there is the separate file; the in-band chain of 08 §16 stays.

#### Five invariants for every stage

*Proposed · 06* — what no stage may break

1. **Byte-exact inverses.** Every structural change to the journal can be undone to the byte (T3a proved it for the split).
2. **Raw import.** Every legacy record enters the ledger raw, and every re-export through the shadow period is byte-identical (T3c).
3. **Nothing deleted.** A retired file freezes read-only in git; retired code moves aside with its last measurement.
4. **A commit before and after each stage**, pushed. Obligation partitions commit locally and are never pushed (08 §11.3).
5. **Transcripts are untouched** throughout.

Every stage has the same four parts: a precondition, a check that it worked, a check that it can be undone, and the gate for the next stage. The docs say nothing runs without the owner's go-ahead.

**Source** 06, invariants I1 to I5 and its opening.

## Evaluation: how "better" is decided

Written before anything is built, so the bars cannot be chosen after a result. Each experiment gets its own full pre-registration, with both branches written first, before it runs.

#### How the successor is judged

*Proposed · 05 §1* — each principle answers a measured failure

- **The system under test writes no questions.** The current gold set was written by the agent it grades (02, theme 3).
- **Oracles before judges.** Retrieval is scored by evidence ids, dates by date arithmetic, currency by labelled chains. One benchmark's judge accepted about 63% of deliberately wrong-but-adjacent answers (survey §5).
- **Every count prints its opportunity count.** A zero without one is not reported.
- **Frozen populations and question files**, hashed before a run.
- **Planted positives on every axis**, on scratch copies only, never in the real journal.
- **Paired statistics, clustered by episode**: 10,000 bootstrap resamples with a fixed seed; decisions use the lower bound of the 95% interval.
- **Baselines in the same harness**, which calls the production composition.

**Source** 05 §1.

#### Gold set v2

*Proposed · 05 §2* — eight question types, across the whole corpus

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

**Source** 05 §2.

#### Rule A: what it takes to ship

*Proposed · 05 §4* — all four, on the sealed held-out split

1. **No worse on known items.** Known-item plus cross-lingual MRR: successor minus the incumbent of record at least −0.02.
2. **Currency.** On held-out "now" questions, the newest relevant episode is first in its group at least 80% of the time, and at least 0.30 better than the incumbent, scored only on update pairs absent from the link store. With fewer than 25 such items it is not a measurement.
3. **Invariants, zero tolerance:** byte-identical re-exports through the shadow period; every fact resolves to an episode and every traced episode to a session; the FTS integrity check passes; a recall writes nothing.
4. **Latency:** warm p50 at most 0.5 s and cold p95 at most 1.5 s on 200 replayed prompts.

Reported with consequences (Rule B): as-of at least 0.75, when at least 0.70, abstention false-evidence at most 0.20, two-hop reported. Not a win: a gain on the legacy set alone, on dev only, or one that vanishes against the FTS-fixed incumbent.

**Source** 05 §4.

#### E1 · The slot test

*Proposed · 05* — the test for the open question "Consistent slots?"

**What** Extract facts in time order and check whether known update pairs share a slot. Slots become the primary candidate source if at least 0.60 of the 40 audited positives share one and at most 0.05 of 200 random pairs do; below 0.40, slots are only a hint.

**Why** T2b ruled out similarity alone; E1 tests the structure meant to replace it. The question itself stays open until it runs.

**Source** 05 §5 E1.

#### E2 · Is one judge enough?

*Proposed · 05* — the gate for retiring the old stack

**What** Four arms: the current stack, one judge, the same-slot rule, and either of the two. Bar: recall at least the current stack's on the same gold, and blind mark precision of at least 0.80 on 30 marks.

**Why** If it fails, the readouts and the adjudicator are not retired.

**Source** 05 §5 E2.

#### E3 · Density and time

*Proposed · 05* — more facts per long entry; anchored dates

**What** Cap 5 against about one fact per 400 characters (cap 15), with and without resolving relative dates. Bars: citation in long entries at least 0.30 (today 0.13), event time on at least half of dated facts (today about 0.21), and no rise in hallucination above 3.9%.

**Why** The five-fact cap starves long entries and dates rarely reach a fact (01 #15).

**Source** 05 §5 E3.

#### E4 · Do fact keys and slices help?

*Proposed · 05* — the fact lane, and token-sized slices

**What** Fact lane on against off; 3,000-character against 480-token slices. Each stays off unless its gain has a lower bound above zero. O10 makes an arm without the Record in the index mandatory.

**Why** Both are hypotheses until measured here.

**Source** 05 §5 E4; 08_episode_schema O10.

#### E5 · The Greek keyword test

*Proposed · 05* — the test for the open question "Greek keyword search"

**What** The Greek-only keyword leg must improve with a lower bound above zero while English falls by no more than 0.02. If several arms pass, the cheapest wins.

**Why** Greek BM25 scores 0.154 today. The question itself stays open until the test runs.

**Source** 05 §5 E5.

#### E6 · The reader test

*Proposed · 05* — the test for the open question "Do readers act on it?"

**What** A fixed reader answers "what is X now" from the old render and the new, with no-change controls; then the same contested card goes through every loading path against a no-correction control. Bar: the successor beats the incumbent by at least 0.20.

**Why** Proposed by a Colony critic as the end-to-end test (02, theme 1). The question itself stays open until it runs.

**Source** 05 §5 E6.

#### E7 · Does the probe set detect anything?

*Proposed · 05* — canon loaded against canon withheld

**What** The probe set must separate the two with a lower bound above zero, or it is not used as an alarm.

**Why** A smoke alarm that never sounds proves nothing.

**Source** 05 §5 E7.

#### E8 · The model-swap drill

*Proposed · 05 · D2* — the fact lane switched off

**What** Recall with the producer gone must stay within 0.03 MRR of the full successor. Otherwise "facts are keys, not answers" is false and D2 is revisited.

**Why** It is the check D2 itself names.

**Source** 05 §5 E8; 07 D2.

#### The format evaluation

*Proposed · 08d* — does a Record beat the fairest prose?

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

**Source** 08d §1-3, §5-7 and its two amendments.

## Surveyed and not adopted

Not adopting something is also a recommendation, so each of these carries a mark. Below them, the ideas this engine already measured and rejected.

#### Forgetting by decay

*Proposed · not adopted · 04 §12* — no evidence that stale salience is the problem

**What** Ebbinghaus-style decay was surveyed and not adopted. It may return as a ranking prior, never as deletion, if a measurement shows old episodes crowding out relevant ones.

**Why** T2 says ranking ignores time altogether; the fix for that is ordering by time inside a group.

**Source** 04 §12.

#### LLM-driven update and delete

*Proposed · not adopted · 04 §12* — nothing is deleted by construction

**What** The original Mem0 operation set and RL-trained memory managers were not adopted.

**Why** Mem0 itself moved to add-only (survey §1).

**Source** 04 §12.

#### Rewriting notes in place

*Proposed · not adopted · 04 §12* — kept only as new linked versions

**What** A-MEM-style note evolution: the idea of revising a fact's context is kept, but as a new version linked to the old, never an overwrite.

**Why** Never-overwrite is the common shape in the field and the SRS frame here.

**Source** 04 §12.

#### A graph database

*Proposed · not adopted · 04 §12* — links are an edge table

**What** A recursive query covers two hops at this size. The graph question reopens only after three logged multi-hop misses; today there are none.

**Why** One candidate, Kuzu, was archived in October 2025 (survey §2).

**Source** 04 §12; 05 §4 Rule B.

#### Benchmark-led model choice

*Proposed · not adopted · 04 §12* — public benchmarks are weak instruments

**What** LoCoMo and LongMemEval run, if at all, as sanity checks through the same harness, never as the objective.

**Why** Swapping only the embedder moved one benchmark by 6.2 points, enough to flip rankings (survey §5).

**Source** 04 §12; 00 finding 5.

#### Late interaction

*Proposed · not adopted · 04 §5* — no evidence it beats dense plus a cross-encoder on Greek

**What** It may enter only as an E4 arm over the hybrid top 100 to 200, with bge-m3's multi-vector mode as the baseline that needs no new model.

**Why** The best English evidence is a tie, and no source covers Greek.

**Source** 04 §5; survey §7.

#### Measured here and rejected

*Proposed · 01 §4* — not to be re-proposed without a new pre-registration

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

**Source** 01 §4 (a selection of its rows).

## Decisions board

#### D0 · FTS ghost postings fixed

*Decided* — MRR 0.775 → 0.825

The keyword index carried ghost postings because build() deleted the content row before the FTS row. It is fixed and live, and the integrity check passes over 779 entries.

**Source** 07 Decided, D0 (debcc20); 00_INDEX finding 1.

#### D1 · Episodes

*Decided* — one immutable file each

#### D2 · Facts

*Decided* — keys into episodes, never beliefs

#### D3 · Q1 · What a reader is shown

*Proposed* — D3 as written

#### D3 · Q2 · Raw files (grep)

*Proposed* — 36% of sessions grep; 7% call recall

#### D4 · One ledger

*Proposed* — replaces five stores

#### D5 · One judge and a same-slot rule

*Proposed* — only after E2

#### D6 · Injection exposure

*Proposed* — clean · web · social · unknown

#### D7 · Held-out questions

*Proposed* — about 30, written by the owner and sealed

Run only at milestones; everything else is written by local models and blind agents. It answers the critique that the system grades itself. Optional.

**Source** 07 Open, D7.

#### D8 · Always-loaded layer

*Proposed* — measure first, change nothing yet

#### D9 · Producer

*Proposed* — today: Opus through claude -p

#### D10 · Whether transcripts are kept in git

*Open* — about 3,600 files and 5.45 GB, measured

Whether L0, the transcripts, is kept in git. 04 §1 said it was; it is not, because the corpus repository's ignore file excludes the transcript directories. In git, transcripts would be versioned and reach the other machine, and they would also carry whatever passed through a session, credentials included, into a pushed repository: the credential screen redacts what writers see, not L0 itself. Out of git, L0 exists only where the harness wrote it, and the design names no other copy.

**Source** 07 Open, D10 (the owner, 2026-11-26: undecided, no recommendation); 04 §1 as amended.

#### G5 · Does the evaluation's G5 take the split credential?

*Open* — the format evaluation's credential gate

#### O1–O23 · The episode-format decisions

*Decided* — the owner; O1, O5 and O9 by Nyx

O1 view renders the Reflection first (Nyx). O2 a labelled Record stays fully usable. O3 UTC with Z. O4 transcript first, newest first, stop on a failed batch. O5 Record first in the file (Nyx). O6 the prose-only path stays, flagged needs_reparse. O7 sessions without a transcript keep their prose plus Pass B. O8 caps start at 12 KB and 25 items. O9 code pre-fills the mechanical items (Nyx). O10 an evaluation arm without the Record is mandatory. O11 superseded. O12 the owner labels the classifier's gate set. O13 one transcript directory is excluded. O14 temporary and scratchpad sessions are in scope. O15 Pass B scope. O16-O18 and O20 closed: no obligation applies. O21 a dedicated signing key. O22 any label may reach canon. O23 the flow table.

**Source** 08_episode_schema, Decided and "Decided by the owner, 2026-11-25 (late)".

#### O19 · Partition encryption

*Proposed* — a LUKS2 container is recommended

#### Format · Record

*Proposed* — typed items, each anchored

#### File type · Two questions, not one

*Open* — the stored bytes, and what a reader is shown

#### 40 mechanisms instead of 50

*Proposed · 04 §9* — counted part by part

**What** Supersession and currency fall from 13 parts to 6, and stores, identity and provenance from 10 to 6. Delivery and control gain 3. Each part that survives does so on a measurement.

**Why** Design rationale: each mechanism today is defended by a measurement, but their sum is not: about 5,600 lines of pipeline code, at least nine decision documents, and no tests for the core parsers (01 #23).

**Source** 04 §9.

today

successor

50 → 40

Episode writing: 6 today, 4 in the successor

Provenance, sessions: 3 today, 3 in the successor

Identity: 2 today, 1 in the successor

Stores: 5 today, 2 in the successor

Extraction: 2 today, 3 in the successor

Supersession, currency: 13 today, 6 in the successor

P3: 1 today, 1 in the successor

Read path: 9 today, 8 in the successor

Delivery: 4 today, 6 in the successor

Control: 5 today, 6 in the successor

#### First implementation step

*Proposed · 07* — M0 · M1 · M2

**What** M0: the FTS fix and gold set v2. M1: one grammar, code first. M2: minted ids. Small, reversible, and useful whatever else is decided.

**Why** Recommendation (07): small, reversible and useful whatever else is decided.

**Source** 07 (closing paragraph); 06.

#### All 40 mechanisms, one by one

*Proposed · 04 §9* — where each is explained, or that the docs say no more

| # | Group | Mechanism | Box | Note |
|---|---|---|---|---|
| `1` | Episode writing | the writer library (clock, id, origin) | The writer (*Proposed*) | replaces hand appends, the clock hook and stamp's rewrite |
| `2` | Episode writing | the P1 author | Transcript-first mining (*Decided*) | writing from a transcript is now origin mined (08 §11.2) |
| `3` | Episode writing | P1 review | Verifier (*Proposed*) | becomes claim-verification events; it never edits a file (08 §13) |
| `4` | Episode writing | mining | Transcript-first mining (*Decided*) |  |
| `5` | Provenance, sessions | the transcript map, into the ledger | no box | keeps its logic and four tiers; writes episode.traced, never the file (04 §2.3) |
| `6` | Provenance, sessions | the P1 watcher, without the chain noise | no box | only a session's disposition is an event (04 §8.1) |
| `7` | Provenance, sessions | the session classifier, now with exposure | Injection exposure (*Proposed*) |  |
| `8` | Identity | minted ids with the frozen alias table | Minted id (*Proposed*) |  |
| `9` | Stores | the ledger library (lock, append, committed prefix) | One ledger (*Proposed*) |  |
| `10` | Stores | the projection builder, holding the unit-vector cache | Projection (*Proposed*) |  |
| `11` | Extraction | the extractor | What a fact record carries (*Proposed*) |  |
| `12` | Extraction | the validity gate per producer | Producer (*Proposed*) | kept as today (04 §3.3) |
| `13` | Extraction | anchor re-attachment | Anchors that survive edits (*Proposed*) |  |
| `14` | Supersession, currency | candidates (slot plus cosine) | Candidates and the judge, step by step (*Proposed*) |  |
| `15` | Supersession, currency | one judge | One judge and a same-slot rule (*Proposed*) |  |
| `16` | Supersession, currency | the deterministic same-slot rule | One judge and a same-slot rule (*Proposed*) |  |
| `17` | Supersession, currency | the link lifecycle (propose, mark, hold, accept, reject, restore) | Links (*Proposed*) |  |
| `18` | Supersession, currency | intent rules | The temporal path (*Proposed*) |  |
| `19` | Supersession, currency | temporal assembly | Timeline, newest first (*Proposed*) | replaces the old currency notes and belief lookups |
| `20` | P3 | P3 with its origin and currency gates | P3 gates (*Proposed*) |  |
| `21` | Read path | FTS with correct sync | Keyword leg (*Proposed*) |  |
| `22` | Read path | vectors | Vector leg (*Proposed*) |  |
| `23` | Read path | fusion | Score fusion (*Proposed*) |  |
| `24` | Read path | voice rewrite | no box | kept; the docs say nothing more about it |
| `25` | Read path | the reranker service | Reranker (*Proposed*) |  |
| `26` | Read path | the fact-key lane | Fact-key lane (*Proposed*) |  |
| `27` | Read path | federate | Recall (*Proposed*) | federation by register, from the SRS frame |
| `28` | Read path | the miss logger | no box | kept; three logged multi-hop misses would reopen the graph question (04 §12) |
| `29` | Delivery | the budgeted SessionStart pack | SessionStart pack (*Proposed*) |  |
| `30` | Delivery | canon currency | Canon currency (*Proposed*) |  |
| `31` | Delivery | the pointer audit | Pointer audit (*Proposed*) |  |
| `32` | Delivery | the prefetch hook | Ambient prefetch (*Proposed*) |  |
| `33` | Delivery | the post-compact reload | no box | kept; the docs say nothing more about it |
| `34` | Delivery | MEMORY.md L1/L2 | no box | kept; the docs say nothing more about it |
| `35` | Control | the audit | Audit (*Proposed*) |  |
| `36` | Control | the nightly orchestrator, with narrower holds | Concurrency, stated plainly (*Proposed*) |  |
| `37` | Control | the autonomy switch | no box | kept; autonomy is earned by an audit that catches seeded faults (04 §0) |
| `38` | Control | the stop-commit hook | Credential rules (*Proposed*) | it also runs the credential screen on every changed episode (08 §8) |
| `39` | Control | the second machine's transcript mirror | no box | kept; it copies transcripts, and is not a corpus replica (08c §7-8) |
| `40` | Control | the persona probe set | Persona probe set (*Proposed*) |  |

A mechanism is a distinct moving part with its own code path and failure mode; a group that combines roles counts once on both sides. The migration-time generated view is not counted.

**Source** 04 §9; the notes cite where the docs say more.

Sources: `nyx-recall/docs/successor-2026-11/` (00 to 08d, T_result and the D3 panel) and the earlier SRS spec, plus the state of D3 on 26 November. Each box names the line it rests on. "Survey" means 03_sota_survey as cited by the design; it was not re-read for this page.

Prepared for outside review: no journal content and no deployment-specific names.
