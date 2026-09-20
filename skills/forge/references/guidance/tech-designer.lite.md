Craft guidance — `5_Tech Note.md` (lite)

Build the storage table before anything else in this file — walk files 1 and 2 for every persisted value (scores, unlocks, owned items, settings, linked-account state) and give each exactly one row before you draft a sentence of prose around it.

Write one statement per data decision — never both "add alongside the existing value" and "replace it" for the same field; pick one and say only that.

When the brief doesn't name an SDK product, recommend one yourself, tagged `(proposal)`, with one or two alternatives in Open Decisions — this is not a GAP, since the choice is reversible and local to this file.

The same goes for local architecture calls (where a gate is enforced, snapshot vs. join, client vs. server counter): write them as proposals with a one-line trade-off, not questions — unless the choice would change a gameplay rule file 2 already states, in which case it's a GAP, not a proposal.

List existing tooling once, and keep the risk list engineering-only — a business or design risk belongs in file 4, not here.
