# CRM Lead Workflow Spec (NGU)

## 1) Lead Intake Fields (Required)

### Contact
- Full name
- Email
- Phone (with country code)
- Preferred contact channel (call / WhatsApp / email / SMS)
- Time zone

### Lead Context
- Lead source (website form / referral / event / outbound / social)
- Campaign / UTM (if digital)
- Service interest (primary + secondary)
- Budget range
- Timeline to buy (immediate / 30d / 90d / >90d)
- Location (city, country)

### Qualification (BANT-lite)
- Need/problem statement (free text)
- Decision maker? (yes/no/unknown)
- Estimated budget fit (fit / stretch / unknown)
- Urgency score (1–5)

### Ownership & Compliance
- Assigned owner
- Consent to contact (yes/no + timestamp)
- Notes / call summary

---

## 2) Routing Rules

1. **Default owner assignment**
   - Inbound web leads: round-robin among SDR pool.
   - Referrals/VIP: route directly to Account Executive (AE) queue.
   - Existing customer upsell: route to Customer Success owner.

2. **Geography / language override**
   - If region-language match exists, assign to matching rep.

3. **Capacity safeguard**
   - If rep has >40 open leads in Active stages, skip in round-robin.

4. **No owner fallback**
   - Route to `Unassigned - Triage` queue; auto-alert Ops.

---

## 3) SLA (Service Levels)

- **First response**: within **15 minutes** during business hours; **next business day by 10:00** if after hours.
- **First qualification attempt**: within **4 business hours**.
- **Post-call CRM update**: within **30 minutes** of interaction.
- **Manager escalation**: if no activity logged for **48 hours** on Active leads.

Business hours: Mon–Fri, 09:00–18:00 (local market time).

---

## 4) Follow-Up Cadence (First 14 Days)

### Day 0–2 (hot window)
- Day 0: Immediate response + discovery call booking link.
- Day 1: Call attempt #1 + follow-up message.
- Day 2: Call attempt #2 + value email (case study / offer).

### Day 3–7
- Day 4: Personalized touchpoint (pain-point based).
- Day 6: Call attempt #3.
- Day 7: “Still interested?” checkpoint.

### Day 8–14
- Day 10: Nurture content (FAQ, ROI, testimonial).
- Day 14: Breakup message + move to Nurture if no engagement.

Channel sequence priority: preferred channel → phone → email.

---

## 5) Stage Definitions (Pipeline)

1. **New**
   - Entry: lead captured and required fields present.
   - Exit: first outreach attempted.

2. **Contacted**
   - Entry: at least one successful outbound touch.
   - Exit: two-way response received.

3. **Qualified**
   - Entry: need + timeline + decision path confirmed.
   - Exit: meeting/demo scheduled.

4. **Proposal/Offer**
   - Entry: scoped solution and commercial terms shared.
   - Exit: verbal yes/no or negotiation started.

5. **Negotiation**
   - Entry: active commercial/legal discussion.
   - Exit: closed won/lost.

6. **Closed Won**
   - Entry: agreement confirmed and handoff packet complete.

7. **Closed Lost**
   - Entry: explicit no, unqualified, or inactive after cadence.
   - Required close reason (price, timing, competitor, no need, no response).

8. **Nurture**
   - Entry: not ready now but fit exists.
   - Exit: re-engagement response received.

---

## 6) QA Checklist (Weekly Spot Audit)

- [ ] Required intake fields complete (no placeholders)
- [ ] Correct source/campaign attribution present
- [ ] SLA met for first response
- [ ] Activity log current (calls/emails/notes timestamped)
- [ ] Stage matches latest interaction evidence
- [ ] Next step + due date set on every Active lead
- [ ] Lost leads have valid close reason
- [ ] Nurture leads have reactivation date
- [ ] Owner assignment follows routing rules
- [ ] Consent/contact compliance recorded

Owner: Ops (Pierre) with Sales Manager review every Friday.
