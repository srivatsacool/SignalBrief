# SignalBrief System Architecture Overview

SignalBrief is designed with a strict phased development philosophy:
1. **Research & Experimentation**: Jupyter Notebooks (`notebooks/00_` to `10_`).
2. **Reusable Python Engine**: Clean, typed modules (`src/signalbrief/`).
3. **Cloudflare Backend**: Serverless edge compute (Workers, D1, R2).
4. **Subscriber Interface**: Astro + React web dashboard and email briefings.

## Architectural Boundaries

- **Separation of Concerns**: Data collection is decoupled from NLP analytics; experimentation is decoupled from production inference.
- **Traceability**: All synthesized facts maintain pointers to source articles.
- **Privacy & Security**: Reports in Cloudflare R2 are private and served through authenticated Workers endpoints. No credentials or subscriber identities are checked into git.
- **Free-Tier Sustainability**: All chosen components run reliably within free tier limits.
