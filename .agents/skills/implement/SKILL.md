---
name: implement
description: >-
  Execute the automated 3-stage implementation workflow for a roadmap task.
  Use this whenever the user invokes /implement, /implement <task_id>, /implement task <task_id>,
  or asks to implement a specific task from ROADMAP.md.
---

# `/implement` Task Implementation Command & Skill

This skill triggers the automated 3-stage roadmap task implementation workflow for the HSE Easy Mock MCP Server.

---

## 1. Syntax & Invocation Examples

The command accepts flexible task identifier formats:

| Invocation | Matched Task ID | Target Artifact Folder |
| :--- | :--- | :--- |
| `/implement 1.2` | Task `1.2` | `.agents/tasks/task-1.2/` |
| `/implement task 1.2` | Task `1.2` | `.agents/tasks/task-1.2/` |
| `/implement Task 2.1` | Task `2.1` | `.agents/tasks/task-2.1/` |
| `/implement Phase 1 Task 2` | Task `1.2` | `.agents/tasks/task-1.2/` |

---

## 2. Workflow Execution

When this skill is invoked, immediately load and execute the complete implementation workflow defined in:

👉 **[`.agents/workflows/implement_task.md`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/workflows/implement_task.md)**
