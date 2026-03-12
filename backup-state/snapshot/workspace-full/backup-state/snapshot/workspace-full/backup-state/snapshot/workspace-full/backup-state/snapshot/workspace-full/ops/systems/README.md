# Ops Systems v1 (Python + SQLite)

Production-oriented local automation package under `ops/systems` with graceful fallback when API keys are missing.

## Includes (v1)

1. **Personal CRM ingestion** (Gmail + Google Calendar stubbed collectors for now):
   - 60-day backfill + daily cron mode
   - Two-stage filtering + scoring
   - `crm/learning.json` adaptive config
   - SQLite WAL persistence
   - Query commands
2. **Personal KB RAG**
   - Ingest: web / youtube / x / pdf / text (fallback chain)
   - Validation + dedup (`normalized_url + content_hash`)
   - Chunking + embedding provider abstraction
3. **Content idea pipeline**
   - Semantic + keyword dedup gate (`>40 => reject`)
   - Brief assembly
   - Task creation abstraction: todoist/asana/linear/notion
4. **Social research tool**
   - Tiered retrieval architecture (t1/t2/t3)
   - Cost logging + query cache
5. **Nightly business council**
   - Multi-persona review
   - Weighted ranking formula
6. **Natural-language CRM interface**
   - HubSpot/Salesforce-like adapters
   - Object support: contacts/companies/deals/owners/associations
   - Intent classification: lookup/create/update/list/associate
   - Required-field checks
   - Human-readable output
7. **Text rewrite tool**
   - AI-artifact detection + rewrite
   - Channel tuning (X/LinkedIn/blog/email)
   - Optional rationale
8. **Image generation workflow**
   - Context memory by session key
   - Variant generation + accept/revise loop
   - Edit flow abstraction ready (img2img/inpaint via provider abstraction)
   - Saves final assets in configured folder
9. **Action-item extraction + approval-to-task**
   - Inputs: transcript-like text / notes / direct command
   - Field schema enforcement
   - Rejects vague items
   - CRM enrichment using module #1 DB
   - Approval gates before task creation
   - Direct “Remind me to ... by ...” path
   - Retry queue for failed task creation

---

## Setup

```bash
cd /home/bernard/.openclaw/workspace/ops/systems
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Initialize DB

```bash
python -c "from common.db import init_db; init_db(); print('db ready')"
```

---

## Commands

### CRM
```bash
python -m crm.ingest --backfill-days 60 --run-type backfill
python -m crm.ingest --run-type daily
python -m crm.query recent --limit 20
python -m crm.query search "follow up"
```

### NL CRM interface
```bash
python -m crm.crm_nl "create contact firstname:Jane lastname:Doe email:jane@acme.com" --provider hubspot
python -m crm.crm_nl "list deals" --provider salesforce
```

### KB RAG
```bash
python -m kb.ingest "https://example.com/article" --type web
python -m kb.ingest "notes/meeting.txt" --type text
python -m kb.retrieve "What was agreed with the client?" --topk 5
```

### Content ideas
```bash
python -m content.pipeline "How buyers evaluate ROI in 2026" --notes "from recent sales calls" --keywords roi,buyers,gtm --create-task
```

### Research
```bash
python -m research.tool "Latest mortgage trend France" --tier t1
python -m research.tool "Deep competitor positioning analysis" --tier t3
```

### Nightly council
```bash
python -m council.nightly --context "Weekly pipeline + close rate + churn"
```

### Rewrite
```bash
python -m rewrite.tool "In conclusion, let's leverage this..." --channel linkedin --rationale
```

### Image workflow
```bash
python -m image.workflow hero-banner "Modern luxury real-estate hero shot, sunset" --variants 4
python -m image.workflow hero-banner "Modern luxury real-estate hero shot, sunset" --revise "less orange, more neutral" --accept 2
```

### Action-item extraction + approval
```bash
python -m actions.extract_approve extract --source fathom --text "- Send proposal to jane@acme.com\n- think about strategy"
# review pending in DB, then approve
python -m actions.extract_approve approve --mode all
# or approve only selected ids + edit text before confirm
python -m actions.extract_approve approve --mode some --ids 1,3 --edits "1:Send final proposal to jane@acme.com"
python -m actions.extract_approve create --provider todoist

# direct flow
python -m actions.extract_approve direct --text "Remind me to call Paul by Friday 14:00"
```

### Retry queue
```bash
python -m tasking.queue --limit 25
```

---

## OpenClaw Cron (examples)

> If your OpenClaw version uses different flags, run `openclaw help` and adapt.

```bash
# Daily CRM ingestion
openclaw cron add --name crm-daily --schedule "0 6 * * *" --command "cd /home/bernard/.openclaw/workspace/ops/systems && . .venv/bin/activate && python -m crm.ingest --run-type daily"

# Nightly council analysis
openclaw cron add --name council-nightly --schedule "30 22 * * *" --command "cd /home/bernard/.openclaw/workspace/ops/systems && . .venv/bin/activate && python -m council.nightly"

# Retry failed tasks every 30 min
openclaw cron add --name task-retry --schedule "*/30 * * * *" --command "cd /home/bernard/.openclaw/workspace/ops/systems && . .venv/bin/activate && python -m tasking.queue"
```

---

## Telegram-first notifications

Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.
When missing, scripts degrade to stdout logs.

---

## Notes on graceful fallback

- Missing API keys never crash core flows.
- Embeddings fall back to deterministic local vectors.
- CRM API/task adapters return dry-run/stub responses when credentials are unavailable.
- Image generation provider defaults to local placeholder artifact files.

