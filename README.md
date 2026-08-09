# PCNA Assistant

A Streamlit-based PCNA sales workspace for verified product lookup, spec sample orders, decorated quote lookup, virtual requests, Perfectly Packaged concepts, design concepts, and saved customer projects.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data behavior

The repository includes a small **verified starter catalog** so the application can boot and be tested without exposing full company master files in a public repository.

For broad production lookup, open **Data Sources** in the app and load all three current PCNA masters:

- `PCNA_Product_Master_CLEAN.csv`
- `PCNA Decoration Master.csv`
- `PCNA Product Pricing Master 8.03.csv`

The application validates required columns before replacing the active dataset. Product/color and decoration values are never fabricated. Standard quote lookup defaults to **USD list decorated pricing**, not blank pricing.

When a connected live PCNA / PromoStandards Product Data service is configured, live PCNA data should supersede conflicting CSV values.

## AI assistant

The deterministic product/order tools work without an AI key. To enable conversational PCNA Assistant, add `OPENAI_API_KEY` to Streamlit secrets or enter a key in the assistant workspace.

## Validation

Every push to `main` runs GitHub Actions that:

1. installs dependencies,
2. compiles all application modules,
3. runs deterministic PCNA workflow tests,
4. boots Streamlit and verifies its health endpoint.

The tests cover known verified product resolution, decoration options, decorated-pricing selection, laser/deboss imprint behavior, and spec-order formatting.

## Security

Do not commit proprietary full PCNA master files or API credentials to this public repository. Use Streamlit secrets for credentials and the in-app Data Sources loader for local/session master data.
