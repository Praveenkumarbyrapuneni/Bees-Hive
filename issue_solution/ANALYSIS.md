# Deep Technical Analysis: Aden Hive Context Overflow Bug

**Analysis Date:** February 9, 2026  
**Analysts:** Praveen Kumar & AI Cofounder  
**Framework:** Aden Hive (github.com/adenhq/hive)  
**Severity:** Critical - Production Impact

---

## Table of Contents

1. [Discovery Process](#discovery-process)
2. [Architecture Analysis](#architecture-analysis)
3. [Root Cause Analysis](#root-cause-analysis)
4. [Failure Modes](#failure-modes)
5. [Solution Design](#solution-design)
6. [Impact Assessment](#impact-assessment)
7. [Lessons Learned](#lessons-learned)

---

## Discovery Process

### Context

Researching Aden Hive's self-improving agent architecture to understand competitive advantages for our quantitative trading agent project.

### Timeline

**12:00 PM** - Analyzing 4 pillars (BUILD, DEPLOY, OPERATE, ADAPT)
**12:15 PM** - Found Issue #929 (ADAPT missing) - already reported
**12:20 PM** - Shifted to core execution engine (EventLoopNode)
**12:25 PM** - Discovered token estimation in conversation.py
**12:30 PM** - Found Issue #3546 (closed as "not planned")
**12:35 PM** - **KEY INSIGHT:** #3546 dismissed as CJK edge case, but affects ALL structured data

### Critical Realization

Maintainer closed #3546 thinking "CJK languages = niche market."

**But the code path is:**
```
EventLoopNode → NodeConversation.estimate_tokens() → chars // 4
                    ↓
            Used for ALL content types:
            - English text ✓
            - JSON responses ✗ (GitHub, APIs)
            - Code snippets ✗ (files, search)
            - CJK text ✗
```

**Insight:** Bug isn't about language support - it's about **structural density of data**.

---

## Architecture Analysis

### Component Interaction Flow

```
┌─────────────────────────────────────────┐
│ EventLoopNode (event_loop_node.py)     │
│                                         │
│  Main Loop (iterations 0..max):        │
│  1. Drain injection queue               │
│  2. Pre-turn compaction check ──┐      │
│  3. Run LLM turn                 │      │
│  4. Execute tools                ↓      │
│  5. Post-turn compaction ────► needs_  │
│  6. Judge evaluation            compac- │
│  7. Write cursor                tion()  │
│                                  │      │
│  Pre-send Guard (line 889):     │      │
│  if usage_ratio() >= 1.0: ◄─────┘      │
│      compact()                          │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ NodeConversation (conversation.py)     │
│                                         │
│  needs_compaction():                   │
│    return usage_ratio() >= 0.8         │
│                                         │
│  usage_ratio():                        │
│    return estimate_tokens() / max      │
│                                         │
│  estimate_tokens(): ◄─── BUG HERE     │
│    if _last_api_input_tokens:          │
│        return _last_api_input_tokens   │
│    return sum(chars) // 4  ◄─── WRONG │
│                                         │
│  update_token_count(actual):           │
│    _last_api_input_tokens = actual     │
│    (only runs AFTER successful call)   │
└─────────────────────────────────────────┘
```

See README.md for full analysis.

---

**Analysis Complete:** February 9, 2026