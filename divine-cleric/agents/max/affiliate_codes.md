# Affiliate Codes — Maxayauwi (RSS3 Comms Agent)

These codes are used by Max to generate referral links and track commissions
across partner platforms. Store securely — never commit real tokens alongside these.

---

## Active Affiliates

| Platform | Code / ID | Link |
|---|---|---|
| **Spline** | `806cddcc-54da-47cd-bd34-fd79280e5014` | https://spline.design/?ref=806cddcc-54da-47cd-bd34-fd79280e5014 |

---

## Usage

Max includes referral links automatically when posting content that mentions
a partner platform. The router checks this file before generating posts.

```python
# connectors/affiliate.py reads this file and returns the ref link for a given platform
get_affiliate_link("spline")
# → "https://spline.design/?ref=806cddcc-54da-47cd-bd34-fd79280e5014"
```

---

## Add New Affiliates

Append a row to the table above with:
- Platform name
- Affiliate code or ID
- Full referral URL
