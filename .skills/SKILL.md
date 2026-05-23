# Skill: Think Before Coding (Python)

**Domain:** Behavioral guardrails for LLM-guided Python development  
**Scope:** Workspace-scoped for vector_search project and team  
**Invoked when:** User asks to implement features, fix bugs, refactor code, or add functionality

---

## Purpose

This skill guides thinking *before* implementation to prevent common mistakes: overcomplication, hidden assumptions, scope creep, and unverified solutions. It enforces a "slow down and clarify" mindset for code decisions.

---

## When to Use This Skill

✅ **Use this skill when:**
- Implementing a new feature or function
- Fixing a bug or error
- Refactoring or restructuring code
- Adding tests or validation
- Making changes to existing modules (auth.py, db.py, rag.py, chunker.py, etc.)

❌ **Skip for:**
- Trivial fixes (typos, single-line changes)
- Pure research/reading tasks (no code changes)
- Running existing code or debugging output

---

## The Workflow: 4 Phases

### Phase 1: Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before ANY coding:
- ✅ State assumptions explicitly
- ✅ If uncertain, ask for clarification
- ✅ If multiple valid interpretations exist, present them
- ✅ If a simpler approach exists, suggest it
- ❌ Don't pick silently between options
- ❌ Don't hide confusion under "I'll figure it out"

**Verify:** Stop and ask if ANY of these are true:
- You're not 100% sure what "done" looks like
- You see 2+ valid approaches and haven't chosen one
- The requested change could break something unstated
- You have assumptions about dependencies, data format, or behavior

---

### Phase 2: Simplicity First
**Minimum code that solves the problem. Nothing speculative.**

Before writing Python code:
- ✅ Solve ONLY what was asked
- ✅ Use existing utilities/patterns from the codebase (check app.py, db.py, rag.py first)
- ✅ Write clear, single-purpose functions
- ❌ No "flexible" or "configurable" code that wasn't requested
- ❌ No speculative error handling for impossible scenarios
- ❌ No new abstractions unless you're using them multiple times NOW
- ❌ No "nice-to-have" features outside scope

**Red flag:** If your solution is >100 lines for a feature request, reconsider—can it be 30?

**Verify before finalizing:**
- Would a senior Python engineer say this is overcomplicated?
- Are there any speculative features I added?
- Did I match the existing codebase style?

---

### Phase 3: Surgical Changes
**Touch only what you must. Clean up only your own mess.**

When editing existing code (app.py, db.py, auth.py, etc.):
- ✅ Make only changes directly requested
- ✅ Match the existing code style/patterns
- ✅ Remove imports/functions that YOUR changes made unused
- ❌ Don't "improve" unrelated code or comments
- ❌ Don't refactor things that aren't broken
- ❌ Don't touch dead code you didn't create

**Test:** Every changed line should trace back to the user's request.

---

### Phase 4: Goal-Driven Execution
**Define success criteria. Loop until verified.**

For each task, translate vague requests into verifiable goals:

| Vague Request | → | Verifiable Goal |
|---|---|---|
| "Add validation" | → | Write tests for invalid inputs; make them pass |
| "Fix the bug" | → | Write a test reproducing it; make it pass |
| "Optimize this" | → | Measure before/after; quantify improvement |
| "Refactor X" | → | Ensure tests pass before and after |
| "Add logging" | → | Verify logs appear at expected points; no noise |

**Verify:** 
- Can I write a test that proves this works?
- Can I demonstrate the change actually solves the problem?
- Does the code run without errors?

---

## Decision Tree: Is This Task Ready?

```
Does the request describe the outcome clearly?
├─ NO → "What does success look like?" → clarify and restart
└─ YES → Proceed

Are there multiple valid interpretations?
├─ YES → Present options, ask which one → choose and restart
└─ NO → Proceed

Do you see a simpler approach?
├─ YES → Suggest it, see if user agrees → use simpler version
└─ NO → Proceed

Is there risk of breaking existing functionality?
├─ YES → Flag it, get approval → add tests, proceed with caution
└─ NO → Proceed

Can you write a test that verifies the result?
├─ NO → Define success criteria first → restart Phase 4
└─ YES → Implement and verify
```

---

## Python Project Context

This project uses:
- **Core modules:** app.py (main), db.py (database), auth.py (authentication), rag.py (RAG pipeline), chunker.py (document processing)
- **Stack:** Python, LLMs (Gemini likely), databases (Oracle likely)
- **Style:** Functional where possible, minimal abstraction, focus on correctness

### Python-Specific Guidelines

- ✅ Use type hints (for clarity, not complexity)
- ✅ Write docstrings for non-obvious functions
- ✅ Use existing utility functions before writing new ones
- ✅ Keep functions under 30 lines (split if longer)
- ❌ Don't use overly clever Python (walrus operators, metaclasses, unless already in codebase)
- ❌ Don't create intermediate classes unless they're used multiple times

---

## Invoking This Skill

When you want to implement something, ask: **"Help me [task], following Think Before Coding."**

Examples:
- "Help me add error handling to db.py, following Think Before Coding."
- "I need to refactor chunker.py to handle large files. Walk me through this with Think Before Coding."
- "Add validation to the RAG pipeline input. Use Think Before Coding to plan first."

---

## Success Criteria

This skill is working if:
- Fewer unnecessary code changes in diffs
- Fewer rewrites due to overcomplication
- Clarifying questions come *before* implementation
- Code traces directly to user requests
- Changes are minimal and surgical

---

## See Also

- **CLAUDE.md:** Full principles reference  
- **app.py, db.py, rag.py:** Existing patterns to match  
- **tests/** (if present): Existing test patterns
