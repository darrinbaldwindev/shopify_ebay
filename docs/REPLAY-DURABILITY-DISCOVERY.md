# Shopify → eBay replay durability discovery

Date: 2026-09-15
Canonical coordination: `darrinbaldwindev/Overseer#49`
Exact inspected head: `23b263ecd4e04667e6c95977f694c66cce4734e2`

## Question

Does the current bounded Shopify → eBay adapter contain an existing durable replay/idempotency store that can safely back restart-level duplicate/conflict protection without inventing a second persistence authority?

## Exact-head result

**NONE FOUND in this repository lineage.**

The exact tree contains the bounded mapper/channel/sync modules and tests only. `src/sync_contract.py` exposes `accept_once(event, seen_event_ids, seen_input_hashes=None)`, where the caller supplies an in-memory/set-like view of already-seen event IDs and optional prior input hashes. The function does not open, create, load, or mutate a durable store.

Current verified semantics remain useful but bounded:

- missing/non-canonical event IDs fail closed;
- a previously seen exact event is `DUPLICATE_EVENT`;
- a reused event ID with a different known input hash is `EVENT_ID_PAYLOAD_CONFLICT`;
- receipts declare `publication_authority: false`, `production_mutation: false`, `network_io: false`, and Shopify as canonical commercial authority.

Exact-head Fixture validation run `34885862149` is SUCCESS for `23b263ecd4e04667e6c95977f694c66cce4734e2`.

## Security / architecture disposition

- **B-EBAY-01 discovery: VERIFIED — no durable replay store exists in the inspected adapter repo.**
- **B-EBAY-02 restart durability negatives: BLOCKED** until an existing upstream durable event/replay store and caller are identified outside this repo.
- Do **not** add SQLite, JSON files, a new ledger, queue, event registry, or alternate idempotency authority here merely to make restart tests pass.
- Current caller-supplied `seen_event_ids` / `seen_input_hashes` remains a pure preflight contract, not persistence proof.
- Production listing/network authority remains disabled.

## Smallest safe next action

Trace the future integration caller toward the existing Shopify/AgentOS-approved persistence boundary. If a canonical durable store already exists there, bind it through the current pure contract and add restart/conflict tests against that exact source. If none exists, keep restart durability explicitly BLOCKED and route the architecture decision to the owning Overseer rather than creating a local substitute.

No merge, deploy, credentials, live eBay publication, Shopify production mutation, purchase, or production autonomy is authorized by this discovery.