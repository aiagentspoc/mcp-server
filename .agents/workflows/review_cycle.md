# Parallel Review Cycle Workflow Runbook

**Trigger**: Invoked automatically after Stage 2 (Implementation) completes.

---

## 1. Review Loop Architecture (Max 3 Iterations)

```mermaid
sequenceDiagram
    autonumber
    actor Main as Main Agent
    participant Arch as Subagent: architect (Pro)
    participant QA as Subagent: qa (Pro)
    participant Fixes as .agents/tasks/task-xx/FIXES.md

    loop Review & Fix Cycle (Max 3 Iterations)
        Main->>Fixes: Initialize / Reset .agents/tasks/task-xx/FIXES.md
        Main->>Arch: invoke_subagent(architect, model='pro')
        Main->>QA: invoke_subagent(qa, model='pro')
        
        par Parallel Review Pass
            Arch->>Fixes: Append Architecture & Conventions Fixes
            QA->>Fixes: Append QA, Schema & Test Fixes
        end
        
        Note over Main: Both Subagents Complete Pass
        Main->>Fixes: Read .agents/tasks/task-xx/FIXES.md
        
        alt No Fixes Needed (All Passed)
            Main->>Main: Sign off and complete task!
        else Fixes Requested (Iteration < 3)
            Main->>Main: Implement all fixes in a unified pass
            Main->>Fixes: Clean up .agents/tasks/task-xx/FIXES.md
            Note over Main: Re-invoke architect & qa for next iteration
        else Iteration == 3 and Unresolved Issues Exist
            Main->>Main: Create .agents/tasks/task-xx/unresolved_review.md (4-part Question Convention)
            Main->>Main: Await human decision
        end
    end
```

---

## 2. Temporary Feedback File Specification (`.agents/tasks/task-xx/FIXES.md`)

In each review pass, `architect` and `qa` write their requested changes into `.agents/tasks/task-<task_id>/FIXES.md` using this structure:

```markdown
# Review Feedback & Required Fixes (Iteration X/3)

---

## 🏛️ Architecture & Code Conventions (`architect`)
* **Status**: Passed / Fixes Required
* **Items**:
  1. `models.py` (Lines 45–52): Add missing Field constraints.
  2. `server.py` (Line 180): Refactor sorting to use `operator.attrgetter`.

---

## 🧪 Quality Assurance & Test Verification (`qa`)
* **Status**: Passed / Fixes Required
* **Items**:
  1. `tests/test_server.py`: Missing test case for repealed citation `D.Lgs. 626/94`.
  2. Latency benchmark: Optimize lookup table to satisfy <15ms response target.

---

## ❓ Items Requiring Human Approval
*(Formatted using the 4-part Question Convention if architectural/product decisions are needed)*
```

---

## 3. Review Subagent Execution Protocol & Permissions

### Permissions & Access Scope for Review Subagents
- **Workspace-wide (Non-Edit)**: Pre-approved for all non-edit actions across the repository (viewing files, reading docs, searching via grep, listing directories) plus read-only test running (`pytest`) and latency benchmarking for `qa`. Editing workspace code outside `.agents/tasks/` is prohibited.
- **Task Directory (`.agents/tasks/`)**: Full create, write, and edit permissions within `.agents/tasks/` (to write and manage `ARCHITECT_REVIEW.md`, `QA_REVIEW.md`, `FIXES.md`, and any review files).

### `architect` Subagent
1. Audits component boundaries, FastMCP lifecycle, Pydantic v2 schemas, and code conventions.
2. Writes comprehensive architectural review report to `.agents/tasks/task-<task_id>/ARCHITECT_REVIEW.md`.
3. Appends any actionable fix items to `## 🏛️ Architecture & Code Conventions` in `.agents/tasks/task-<task_id>/FIXES.md`.
4. Reports completion of review pass to main agent.

### `qa` Subagent
1. Executes `pytest` test suites, verifies acceptance criteria from [SPECIFICATIONS.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md), and benchmarks latency (<15ms).
2. Writes comprehensive QA verification report to `.agents/tasks/task-<task_id>/QA_REVIEW.md`.
3. Appends any actionable fix items to `## 🧪 Quality Assurance & Test Verification` in `.agents/tasks/task-<task_id>/FIXES.md`.
4. Reports completion of review pass to main agent.

---

## 4. Main Agent Re-Invocation & Loop Boundary
1. **Consolidated Fix Implementation**: The main agent waits until **both** subagents finish their pass, then applies all items from `.agents/tasks/task-<task_id>/FIXES.md` in one unified pass.
2. **Re-Invocation**: After implementing the fixes, the main agent clears `.agents/tasks/task-<task_id>/FIXES.md` and re-invokes `architect` and `qa` (`invoke_subagent` with `Model: 'pro'`).
3. **Termination Conditions**:
   - **Success**: Both subagents mark their status as `Passed` with 0 items $\rightarrow$ Task completed.
   - **Max Iterations (3)**: If issues persist after 3 iterations $\rightarrow$ Escalate to human via review file with the [Mandatory Question Convention](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/AGENTS.md#4-mandatory-question-convention).
