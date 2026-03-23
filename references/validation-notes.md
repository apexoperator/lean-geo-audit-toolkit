# Validation Notes

This project now has a lightweight validation pass across multiple real sites.

## Current validation set

- https://stripe.com
- https://developer.mozilla.org
- https://www.shopify.com
- https://www.notion.so

## What the validation pass is for

The goal is not to crown winners. It is to expose heuristic failures quickly.

Use the validation set to catch problems like:
- scoring that is too flattering
- scoring that is too harsh on strong sites
- bad page-selection logic
- schema recommendations that over-guess
- title/description checks that confuse JS/rendering quirks with true quality issues
- repetitive or low-value recommendations

## Findings from the first real validation pass

1. **Title-quality scoring was too harsh**
   - Strong sites still produced low-confidence title warnings because some fetched pages returned weak titles like `MDN`, `Stripe logo`, or `Play video`.
   - This suggests a mix of real issues and lightweight-fetch limitations.

2. **Schema inference was over-guessing**
   - Early heuristics inferred types like `LocalBusiness` too freely from weak contact-page cues.
   - This was tightened so type suggestions rely more on path intent and stronger textual evidence.

3. **Cross-domain canonicals need nuance**
   - Sites like Notion legitimately canonicalize between closely related domains.
   - Canonical checks now allow same-family host/path matches instead of treating all domain differences as broken.

4. **The report is more useful when it prioritizes actions**
   - Executive summary + prioritized actions improved readability substantially.
   - The tool should continue to prefer operator-grade recommendations over diagnostic clutter.

## Current caution

The tool is still a lightweight, non-browser pass.
It should be explicit when a weak signal may reflect rendering limitations rather than a definite site flaw.

The first validation extension also exposed a harder boundary:
- some sites can return HTTP 403 to the current fetch path
- some sites return nav-heavy shell content that weakens signal quality without a browser/rendered pass

That boundary should be handled explicitly in reporting and validation summaries.
It should not be hidden behind fake confidence.

## Next validation direction

Good next targets:
- one strong docs-heavy product site with likely good machine-readable structure
- one weaker SMB/local-business marketing site
- one content-heavy publication/blog
- one ecommerce/product-led site with obvious schema opportunities

The next step is not adding more modules blindly.
The next step is continuing to tighten heuristics against real outputs.
