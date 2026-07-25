# CounterGuard — Finalized Multi-Agent Architecture
Autonomous Counterfeit & Grey-Market Intelligence Network

This is the build-ready spec. It supersedes the earlier version by replacing
the linear pipeline with **bounded agent-to-agent querying**, making the
**Evidence Timeline** the actual shared state (not a UI layer), and locking
**human-in-the-loop legal escalation** as a design decision, not a gap.

---

## 1. Core Design Principle

Every agent does two things now, not one:
1. **Runs its own analysis** as a pipeline stage (same as before)
2. **Can call other agents mid-investigation** with a specific question, the
   way a human investigator would say "hey, can you double-check this for me?"

This is what turns "9 agents reporting to an orchestrator" into "9 agents
reasoning together." Judges notice the difference immediately in the demo.

---

## 2. Shared State = Evidence Timeline

```python
class InvestigationState(TypedDict):
    listing_id: str
    listing_data: Dict[str, Any]
    evidence_timeline: List[Dict[str, Any]]  # <- this IS your dashboard feed
    agent_findings: Dict[str, Any]
    confidence_score: float  # running total, updated live
    cross_query_count: int  # bounded, see below
    status: str
    legal_notice_draft: Optional[str]
```

Every agent action — a finding, a question, an answer — appends one entry:

```json
{"timestamp": "09:14", "agent": "scout", "action": "discovered_listing",
 "detail": "...", "confidence_delta": 0}
```

**Why this matters beyond aesthetics:** your Streamlit dashboard doesn't need
separate rendering logic for "agent findings" vs. "investigation log" vs.
"confidence chart" — it's all one list you stream and re-render. Build the
state schema right and the demo UI is nearly free.

---

## 3. The Collaborative Query Pattern

```python
def cross_query(state, asking_agent, target_agent, question) -> str:
    if state["cross_query_count"] >= MAX_CROSS_QUERIES:  # cap = 5
        return "cap_reached"
    log_event(state, asking_agent, "asks", f'→ {target_agent}: "{question}"')
    answer = AGENT_QUERY_HANDLERS[target_agent](question, state)
    log_event(state, target_agent, "answers", f'→ {asking_agent}: "{answer}"')
    state["cross_query_count"] += 1
    return answer
```

**Why bounded at 5:** without a cap, two agents could in principle keep
querying each other indefinitely. The cap isn't just a safety rail — it's a
good answer if a judge asks about cost or latency at scale ("we bounded
inter-agent reasoning to keep token spend predictable in production").

**Confirmed working examples (see `orchestrator.py`):**
- Graph Agent → Visual Agent: *"These three sellers appear related, compare
  logos across all three"* → Visual returns a similarity score → Graph
  updates its own confidence based on the answer.
- Mystery Shopper → Price Agent: *"If an invoice existed, would price still
  be suspicious?"* → Price Agent answers → Mystery Shopper's evasiveness
  finding stands, now cross-validated instead of asserted in isolation.

---

## 4. Agent Roster (Finalized)

| Agent | Pipeline role | Can be queried by others? | Can query others? |
|---|---|---|---|
| **Scout** | Detects new/changed listings | No | No |
| **Visual Forensics** | Image similarity vs. golden reference | **Yes** — answers logo/packaging comparison requests | No |
| **Text Consistency** | Spec/description vs. canonical catalog | No | No |
| **Seller Network Graph** | Community detection across seller registration data | No | **Yes** — queries Visual to confirm network hypotheses |
| **Price Anomaly** | Statistical pricing/discount outlier detection | **Yes** — answers conditional "what-if" pricing questions | No |
| **Mystery Shopper** | Poses as a buyer, requests authenticity proof from seller | No | **Yes** — queries Price to cross-validate evasiveness signal |
| **Confidence Fusion** | Aggregates evidence_timeline deltas into a labeled verdict | No | No |
| **Legal Escalation** | Drafts takedown notice, **never auto-files** | No | No |
| **Orchestrator** | Graph wiring / routing (LangGraph itself) | — | — |

---

## 5. Human-in-the-Loop Legal Escalation (Locked Decision)

The Legal Agent's job ends at:

> `"DRAFT TAKEDOWN NOTICE — awaiting human approval"`

It never calls a marketplace takedown API directly. Reasons, in priority order:
1. Takedown processes differ per marketplace/jurisdiction — a wrong auto-filed
   notice has real legal and reputational cost
2. Fully autonomous enforcement invites exactly the "what stops this from
   wrongly taking down a legitimate seller?" question — better to have
   already answered it in your design than get caught defending it live
3. It's a smaller, more honest scope for a 1-week build

**Pitch it as a feature, not a limitation.** Auto-filing goes in the future
roadmap slide only.

---

## 6. Routing Logic

```
scout → visual → text → graph → price → mystery_shopper → fusion
                                                              │
                                          confidence ≥ 70 ────┼──→ legal (draft only)
                                          confidence < 70 ────┘──→ end (human review queue)
```

The 70% threshold is a placeholder — tune it once you have a few labeled
test cases. It's easier to defend a chosen threshold than an unexplained one,
so have a one-line reason ready ("optimized for recall over precision since
a human reviews every escalation anyway").

---

## 7. Swapping Mocked Calls for Real Ones

Every stub in `orchestrator.py` is marked `# TODO: replace with real ...`.
Priority order for your 1-week build (matches the plan from earlier):

| Day | Replace this stub | With |
|---|---|---|
| 1–2 | `scout_agent` | Real scrape of a chosen marketplace category or a seeded dataset |
| 1–2 | `visual_forensics_agent` / `visual_answer` | CLIP embedding distance vs. a golden reference image set |
| 3–4 | `seller_network_agent` | networkx community detection over seller metadata |
| 3–4 | `price_anomaly_agent` / `price_answer` | Isolation Forest over price/discount/stock features |
| 5 | `mystery_shopper_agent` | Claude API conversation loop messaging the seller, response evasiveness scored by the LLM itself |
| 5 | `confidence_fusion_agent` | Replace the flat running sum with a small trained classifier once you have a few labeled cases |
| 6 | `legal_escalation_agent` | Real jurisdiction-aware notice template (keep the human-approval stop) |

---

## 8. Demo Script (matches your "cinematic" evidence timeline)

Run `orchestrator.py` as-is first — it already produces the exact kind of
timeline you described, end to end, with real cross-agent questions and
answers logged in order. Use that terminal output (or the Streamlit version
of it) as your live demo instead of static slides. Judges watching an
investigation unfold in real time, including one agent second-guessing
another, is the moment that sells the "genuine multi-agent system" claim.
