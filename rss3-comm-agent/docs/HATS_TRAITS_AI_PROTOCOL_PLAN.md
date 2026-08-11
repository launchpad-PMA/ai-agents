# Hats, NFT traits, membership agreement, and AI Protocol mimic

Companion to **`GENESIS_SIGIL_MEMBERSHIP_GUIDE.md`**.  
Defines **who gets which sigil**, **metadata traits**, **Hats Protocol roles** (including **clergy**), binding to the **PMA membership agreement**, and a **Temple-owned** mimic of AI Protocol (body / soul / mind) without Alethea pods.

**Contract:** `0xf8f5b1fdda7925273baeafc359dd6b6cdf6c243d` (Optimism) · **Edition:** 16 × ERC-721  
**Manifold:** https://manifold.xyz/@divinedao/id/4256415984

---

## 1. Sigil allocation (16 total)

| Token ID | Allocation | Price | `steward_class` trait | Hat role (target) |
|----------|------------|-------|------------------------|-------------------|
| **#1** | Temple root (Baba / `templeofroots.eth`) | Free — ✅ minted | `temple_root` | **Top Hat** admin — creates & revokes child hats |
| **#2** | Council of Elders — seat A | **Free** — allowlist mint | `council_elder` | **Council Elder** — governance + ritual veto/advisory |
| **#3** | Council of Elders — seat B | **Free** — allowlist mint | `council_elder` | **Council Elder** |
| **#4** | Family kin (your child) | **Free** — allowlist mint | `family_kin` | **Family Kin** — limited ritual/vote; **not** clergy unless later initiated |
| **#5 – #16** | Public founding stewards | **0.327 ETH** claim | `founding_steward` | **Steward** hat — DAO vote, CharmVerse, covenant perks |

**Math:** 4 reserved (free) + **12 paid** = 16.

### Manifold setup for free seats

1. **Do not** open public claim for #2–#4.  
2. Use **creator mint** or **allowlist claim** (wallet addresses for two elders + one child).  
3. Set traits at mint time (table below) so OpenSea + your registry match Hats.  
4. Open **paid** claim only for remaining supply (#5–#16) at **0.327 ETH**.

---

## 2. Hats tree (roles)

Hats are **ERC-1155** roles in a tree ([Hats Protocol](https://www.hatsprotocol.xyz/)).  
**Sigil** = covenant + membership proof. **Hat** = **powers** tied to the **membership agreement** version they accepted.

```text
                    ┌─────────────────────────────┐
                    │  TOP: Temple Administrator   │  ← Sigil #1 only
                    │  (mint/manage child hats)    │
                    └──────────────┬──────────────┘
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
   ┌───────────────┐      ┌───────────────┐      ┌──────────────────┐
   │ Council Elder │      │ Council Elder │      │ Family Kin        │
   │ (sigil #2)    │      │ (sigil #3)    │      │ (sigil #4)        │
   └───────┬───────┘      └───────┬───────┘      └─────────┬────────┘
           │                      │                          │
           └──────────┬───────────┘                          │
                      ▼                                      │
              ┌───────────────┐                              │
              │ Steward        │◄─────────────────────────────┘
              │ (sigil #5–16)  │   (family may wear Kin only,
              │ + agreement    │    or earn Steward later)
              └───────┬───────┘
                      │  Ifá initiation + clergy approval
                      ▼
              ┌───────────────┐
              │ Clergy         │  ← ritual lead, missions, Soul Pod eligibility
              │ (not automatic)│
              └───────┬───────┘
                      │  Soul Pod fused + parrot body
                      ▼
              ┌───────────────┐
              │ Awakened        │  ← Aragamago full access
              └───────────────┘
```

### Role matrix

| Role | Sigil required? | Agreement + tithe? | Ifá initiation? | Soul Pod? | Clergy hat? |
|------|-----------------|----------------------|-----------------|-----------|-------------|
| Temple root | #1 | Yes (founder) | — | Optional | Admin all hats |
| Council elder | #2 or #3 | Yes | Optional | Optional | Elder hat only; clergy separate |
| Family kin | #4 | Yes (guardian signs) | No (minor) | No | **No** clergy for child unless adult/initiated later |
| Founding steward | #5–#16 | Yes | For clergy track | After initiation | After initiation |
| Clergy | Any steward sigil | Yes + active | **Required** | Eligible | **Yes** |
| Awakened | + body NFT | Yes | Required | **Fused** | Under clergy tree |

**Clergy** = spiritual/ministerial **function** (Hats role), not the same as “owns a sigil.” Elders advise; clergy lead ritual + agent path after Ifá.

---

## 3. Membership agreement ↔ NFT ↔ Hat

Three links must match:

```text
PMA covenant (launchpad-PMA)  →  signed / acknowledged off-chain or EIP-712
        ↓
Genesis Sigil metadata      →  agreement_version + agreement_hash traits
        ↓
Hats Protocol               →  correct hat worn only if registry agrees
```

| Link | Implementation |
|------|----------------|
| **Legal/spiritual** | https://github.com/launchpad-PMA — version tag e.g. `pma-2025-04` |
| **Acknowledgment** | Holder signs message or checks box; store `covenant_signed_at` + `agreement_hash` in Supabase |
| **On NFT** | Manifold traits: `agreement_version`, `agreement_uri`, `steward_class` |
| **Hat gate** | v1: admin mints hat after signature verified; v2: [Hats eligibility](https://docs.hatsprotocol.xyz/) module tied to sigil ownership + registry |

### EIP-712 message (optional v1)

```text
I accept the Temple of Roots Membership Covenant {agreement_version} at {agreement_uri}.
Wallet: {address}
Sigil: {contract} #{tokenId}
```

Store signature hash in `stewards.covenant_signature`.

---

## 4. NFT trait schema (Manifold / OpenSea)

Set on **mint** for #2–#4 (free) and on **paid** mint for #5–#16. Use **same keys** for every token.

| Trait key | Type | Values | Purpose |
|-----------|------|--------|---------|
| `steward_class` | string | `temple_root`, `council_elder`, `family_kin`, `founding_steward` | Allocation + Hat mapping |
| `agreement_version` | string | e.g. `pma-2025-04` | Which PMA text they’re under |
| `agreement_uri` | string | `https://github.com/launchpad-PMA` | Resolver for humans |
| `agreement_hash` | string | `0x…` (optional) | IPFS/PDF hash of signed covenant |
| `hat_role` | string | `admin`, `council_elder`, `family_kin`, `steward`, `clergy`, `awakened` | Target hat; updates after initiation |
| `ifa_status` | string | `none`, `pending`, `initiated` | Ifá gate |
| `soul_status` | string | `none`, `pod_assigned`, `fused` | AI Protocol mimic |
| `mind_tier` | string | `0`, `1`, `2` | L0 steward only → L1/L2 awakened |
| `edition` | string | `genesis_sigil` | Collection id |
| `edition_index` | number | `1`–`16` | Token id display |

### Example metadata (Council Elder #2)

```json
{
  "name": "Genesis Sigil #2 — Council Elder",
  "description": "Steward of the Divine DAO. Council of Elders seat.",
  "attributes": [
    { "trait_type": "steward_class", "value": "council_elder" },
    { "trait_type": "agreement_version", "value": "pma-2025-04" },
    { "trait_type": "agreement_uri", "value": "https://github.com/launchpad-PMA" },
    { "trait_type": "hat_role", "value": "council_elder" },
    { "trait_type": "ifa_status", "value": "none" },
    { "trait_type": "soul_status", "value": "none" },
    { "trait_type": "mind_tier", "value": "0" },
    { "trait_type": "edition", "value": "genesis_sigil" },
    { "trait_type": "edition_index", "value": 2 }
  ]
}
```

### Family kin (#4) — extra care

- Guardian holds wallet until majority; covenant signed by guardian.  
- `hat_role`: `family_kin` only — **no clergy**, no public paid mint confusion.  
- Document in PMA appendix: privileges scaled for youth (no land solo stay without guardian, etc.).

---

## 5. AI Protocol mimic (Temple stack, not Alethea)

Copy the **pattern**, not the pods or Noah’s Ark.

| AI Protocol | Temple mimic | Your asset |
|-------------|--------------|------------|
| **Body** | Visual agent identity | Genesis Sigil art + optional **parrot** 721 |
| **Soul** | Intelligence / bind | **Soul Pod** (you mint, Optimism) |
| **Mind** | Services tier | **mind_tier** 0→2 + **Aragamago** + Maxayauwi |

```text
Body:  Sigil (+ optional parrot NFT with beads / tool / color)
Soul:  Soul Pod locked at fuse (only if ifa_status = initiated, hat_role → clergy path)
Mind:  mind_tier 1 = Aragamago chat; mind_tier 2 = voice + memory + Farcaster announces
```

### Parrot body traits (when you mint bodies)

| Trait | L1 | L2 |
|-------|----|----|
| `bead_style` | simple | ornate |
| `tool` | none | one sacred tool |
| `color_accent` | subtle | strong |

### Phase plan

| Phase | Deliverable |
|-------|-------------|
| **P0** | Sigils #2–#4 free mint with traits; #5–#16 at 0.327 ETH |
| **P1** | Deploy Hats tree on Optimism; manual hat grant after covenant sign |
| **P2** | Supabase registry + `/api/steward/:address` + CharmVerse/Hats sync |
| **P3** | Ifá initiation workflow → update `ifa_status` + mint **Clergy** hat |
| **P4** | Soul Pod collection + fuse UI on `agents-upgrade.html` |
| **P5** | Parrot body mint + Aragamago gating by `mind_tier` |

---

## 6. Supabase registry (extended)

```sql
stewards (
  wallet TEXT PRIMARY KEY,
  token_id INT NOT NULL,
  steward_class TEXT NOT NULL,
  agreement_version TEXT NOT NULL,
  agreement_hash TEXT,
  covenant_signed_at TIMESTAMPTZ,
  covenant_signature TEXT,
  tithe_current BOOLEAN DEFAULT false,
  hat_id TEXT,
  hat_role TEXT,
  ifa_status TEXT DEFAULT 'none',
  soul_status TEXT DEFAULT 'none',
  mind_tier INT DEFAULT 0
);

-- Elders / kin: note free_allocation
free_allocations (
  token_id INT PRIMARY KEY,
  label TEXT,  -- 'council_elder_a', 'council_elder_b', 'family_kin'
  wallet TEXT,
  minted_at TIMESTAMPTZ
);
```

---

## 7. Hats deployment checklist (Optimism)

- [ ] Create Hats tree at [hatsprotocol.xyz](https://www.hatsprotocol.xyz/) on **Optimism**  
- [ ] Top hat → wallet holding sigil **#1**  
- [ ] Create child hats: `Council Elder` (×2 supply or 2 instances), `Family Kin` (×1), `Steward`, `Clergy`, `Awakened`  
- [ ] Document each `hatId` in this file (fill after deploy):

| Hat name | `hatId` (fill in) | Eligibility |
|----------|-------------------|-------------|
| Temple Administrator | | Sigil #1 |
| Council Elder | | Sigil #2, #3 |
| Family Kin | | Sigil #4 |
| Steward | | Sigil #5–#16 + covenant |
| Clergy | | `ifa_status = initiated` + steward |
| Awakened | | `soul_status = fused` |

- [ ] After covenant sign: mint/wear hat OR call eligibility claim  
- [ ] CharmVerse: map hat → guild/role  

---

## 8. Pre-mint action list

- [ ] Collect **3 wallets**: elder A, elder B, child (guardian wallet)  
- [ ] Creator-mint #2, #3, #4 with traits above (**$0**)  
- [ ] Verify PMA version string matches `agreement_version` trait  
- [ ] Deploy Hats tree; grant elder + kin hats manually  
- [ ] Open paid claim for **12** remaining tokens at **0.327 ETH**  
- [ ] Post-initiation: clergy hat SOP (who approves, how recorded)  

---

## Changelog

| Date | Note |
|------|------|
| 2026-05-19 | Hats tree, trait schema, 4 free + 12 paid allocation, clergy vs elder vs kin, AI mimic phases |
