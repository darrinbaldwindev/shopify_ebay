# Shopify → eBay Vertical Execution Batch

**Repository:** `darrinbaldwindev/shopify_ebay`
**Canonical portfolio coordination:** `darrinbaldwindev/Overseer#49`
**Portfolio doctrine:** `darrinbaldwindev/Overseer/.overseer/doctrine/VERTICAL-BATCH-EXECUTION.md`
**Lane owner:** Commerce / Lane B (`:15` execution schedule)
**Last fresh scan:** 2026-09-14 Brisbane
**Default branch:** `main@f4214f6995af3b9a05f501c12b9bfe9b0af86b7c`
**Active bounded work branch observed:** `agent/chatgpt/ebay-mapper-receipts@9aea8a6859221eb4a80da5afef3bc042322aad15`
**Status:** ACTIVE / AMBER — synthetic non-production only

## Standing execution rule

When the owner says `cont`, `continue`, `continue autonomously`, or `continue autonomously vertically`, run the complete project cycle:

**fresh scan → reconcile this batch → execute the fullest safe coherent work → verify exact changed state → fresh scan again → replenish this same batch → durable checkpoint to Overseer #49.**

The batch is a hypothesis, not authority. Exact repository/CI/runtime evidence wins. Do not overwrite newer concurrent evidence.

## Governing boundaries

- Shopify remains the canonical commercial/inventory authority.
- This repository remains mapping/validation/receipt work until explicitly widened.
- No live eBay network calls, listing publication, credentials, account mutation, spend, supplier contact, merge, deployment, or production autonomy.
- UNKNOWN supplier permission, freight, fee, seller identity, stock, or marketplace eligibility remains HOLD.
- No model decides its own authority.
- Functional success does not imply security or production readiness.

## Current evidence

### EBY-VB-01 — contradiction precedence baseline
**State:** VERIFIED — predecessor exact synthetic scope only.

Exact commit `c18784ba3cf7c3d3f3d4df9719203cf1a76b9812` added fail-closed contradictions for source identity, marketplace permission and inventory. Canonical portfolio evidence records Fixture validation `34837426789` SUCCESS for that exact state. Do not transfer this PASS to successor heads automatically.

### EBY-VB-02 — active commercial-conflict successor
**State:** PENDING / AMBER.

Current observed active branch head `9aea8a6859221eb4a80da5afef3bc042322aad15` adds conflict precedence around trade cost, freight, channel fees and fulfilment identity. Fresh scan returned no exact-head workflow run for this head.

**Acceptance:** exact-head tests/CI must independently prove each contradictory favourable+unfavourable case fails closed, with no production/network/publication authority.

**Next action:** inspect branch diff and canonical test surface; obtain exact-head deterministic test/CI evidence. Do not inherit `c18784ba…` PASS.

### EBY-VB-03 — zero-network / zero-publication guard
**State:** PENDING RECHECK.

Preserve deterministic proof that mapping/validation cannot perform network IO, publish a listing, use credentials, or mutate a marketplace account.

**Negative cases:** network/SDK invocation, publication flag, credential access, seller/account mutation.

### EBY-VB-04 — replay / idempotency boundary
**State:** PENDING.

Assess current `accept_once` / receipt lineage for durable atomic idempotency before any connector widening.

**Negative cases:** same event ID with conflicting payload hash; restart replay; crash after side-effect but before receipt; duplicate/out-of-order tracking/result.

If durable exactly-once semantics are absent, record the exact gap and remain BLOCKED for live connector widening rather than inventing a second persistence or authority layer.

### EBY-VB-05 — real SKU evidence handoff
**State:** BLOCKED / HOLD on upstream evidence.

Only consume exact GlobalShopCo candidate evidence when supplier marketplace permission, wholesale/trade cost, freight/landed cost, eBay fees, seller-of-record, inventory identity/freshness, returns/warranty and Shopify variant identity are evidenced. Missing material fields remain HOLD.

## Replenishment rule

After any VERIFIED gate, add 2–5 homogeneous adjacent tests/evidence cases where useful. If a top item blocks, record the blocker and immediately advance the next independent safe item. Never stop the whole project because live marketplace evidence is unavailable.

## Required durable checkpoint

Each substantive cycle must record: pre/post exact head, work performed, tests/CI, failures and repair, functional/security disposition, remaining UNKNOWNs/HOLDs, next batch, and confirmation that no protected action occurred.

**No overall GREEN.**