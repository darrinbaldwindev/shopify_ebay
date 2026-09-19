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

## Owner batch reconciliation — 2026-09-15

Current default `c68883f24fb3711fce567a35b1a80db74933b82a`; mapper lineage `02087f3c1b6fa4c6b9406b7cd39698c52a72ab6a` (CI 34913579897 SUCCESS). Earlier active-head statements above are historical. Candidate branch: `agent/chatgpt/owner-batch-identity-2026-09-15`.

W-EBAY-01: implements strict Shopify Product/ProductVariant IDs, non-coerced SKU/event/order/tracking IDs, inconsistent caller replay evidence denial, and preservation of original input hash in conflict receipts. Local baseline 41 tests; candidate 47 tests passed. Candidate CI must be read from its exact PR head, not predecessor results.

EBY-VB-04: BLOCKED_STABLE for restart durability; canonical upstream store/caller remains unidentified across the previous discovery and this inspection. No persistence added. EBY-VB-05 remains HOLD: commercial evidence inputs not supplied.

Next: (1) exact candidate CI and independent Green review; (2) test malformed inventory revision/latest revision types; (3) bind product/variant association to an authenticated upstream caller when available; (4) identify canonical replay caller before restart tests. S2 bounded source/tests/docs only; SG-09/10/14/20 apply. Independent security disposition PENDING. No live listing/network, production, credential, merge, deployment or owner-device action.

## Work-mode repeat checkpoint — 2026-09-19
Fresh default main c68883f24fb3711fce567a35b1a80db74933b82a; active #3 465d54c824734dca00ba115615728040d361e463, exact Fixture validation 35415025055 SUCCESS. Earlier inventory-only/empty portfolio status is stale: this branch has mapper/sync implementation and tests.
This cycle consumes owner #54 through shared Overseer #56 guidance (draft), without claiming portfolio-wide adoption.

WORK_MODE_QUEUE (existing task IDs only):
- W-EBAY-01 revision/tracking validation: DONE on #3; do not duplicate. Authenticated product/variant association still BLOCKED.
- EBY-VB-02 finite economics: reproduced four false admissions (NaN/+infinity in price or contribution) at #3 source. Add finite float checks at existing gate, preserve valid integers/floats, no new policy/persistence.
- EBY-VB-03: local full suite 51 tests PASS including six nonfinite subcases and four finite controls. Candidate exact-head CI/readback required before claiming CI PASS.
- EBY-VB-04 restart durability: BLOCKED_STABLE; canonical upstream replay owner absent.
- EBY-VB-05 real SKU: HOLD; required authenticated commercial bundle absent.

Branch work/finite-economics-20260919 is stacked on #3 to avoid competing edits to its sync_contract lineage. Changed source/test only channel_gate.py and test_finite_economics.py; no connector/network/publication authority. S2; SG-09/10/14/20 retained. Independent Green/security pending, not self-certified.
Next exact action: verify candidate CI; upstream canonical caller/evidence before any association or restart-durability widening. Remaining mapper-input shape/serialization behavior requires separate inventory before accepting more work.
