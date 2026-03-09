# Ops State (Source of Truth)
_Last updated: 2026-03-09 UTC_

## 1) Authority & Communication Rules
- Instruction authority: **Cyril directly in this chat**.
- For Elisa communications: use **professional colleague tone**.
- Default signature on outgoing messages:
  - Bernard
  - Team Cyril Texier
  - NGU Real Estate

## 2) Gmail Integration Status
- Status: **CONNECTED**
- Token path: `~/gmail-oauth/token.json`
- Verified scopes:
  - `https://www.googleapis.com/auth/gmail.readonly`
  - `https://www.googleapis.com/auth/gmail.send`
- Security rule: token/secret values are never echoed in chat.

## 3) Email Actions Log (Verified)
- Sent to: `teamcyril@ngurealestate.com.au`
- Subject: `Elisa guide: full assistant kit`
- Gmail message ID: `19cd0668b9318968`
- Status: **SENT**

## 4) Web Assets Status
### Local/internal live (server HTTP)
- Elisa portal: `http://100.79.0.8:8090/ops/elisa-client-acquisition-kit/`
- Pauleauz site: `http://100.79.0.8:8090/pauleauz-landing/`

### Public Cloudflare status
- Pauleauz public URL: `https://164b14dd-ngu-client-sites.cyriltexier1.workers.dev/pauleauz-landing/` (**live**)
- Elisa public path on same domain: currently **404** (not publicly exposed yet)

## 5) Deployment Notes
- Latest workspace changes were pushed to `main`.
- Cloudflare deploy from this host is currently blocked without `CLOUDFLARE_API_TOKEN` in environment.

## 6) Operating Protocol (Mandatory)
For all future status claims:
1. Verify first via file/tool/command.
2. Report status as: **verified / pending / blocked**.
3. Include proof reference (path or command output).
4. For outbound actions, require confirmation phrase before send.

## 7) Locked Daily Command Center (CEO/CFO/Prospector)
Status: **LOCKED ACTIVE**

- CEO focus (daily): top 3 decisions, priority alignment, execution discipline.
- CFO focus (daily): activity & conversion targets, red-flag detection, pipeline hygiene checks.
- Prospector focus (daily): high-intent first, structured follow-up blocks, reactivation block, EOD KPI log.

Daily cadence:
1. Morning: set targets and top 3 decisions.
2. Midday: check execution vs targets.
3. EOD: KPI review + blockers + next-day top 3.

Continuous improvement rule:
- Iterate dashboard + scripts from real daily feedback.
- Keep what improves conversion; remove what adds friction.

## 8) Status-Answer Guard (Locked)
Before any status answer, run:
`python /home/bernard/.openclaw/workspace/scripts/status_guard.py --status "<status>" --proof-cmd "<live command>" --next "<next step>"`

Reply format is mandatory:
- Status
- Proof
- Next

Never claim completion without both:
1) `ops/STATE.md` check
2) one live command proof
