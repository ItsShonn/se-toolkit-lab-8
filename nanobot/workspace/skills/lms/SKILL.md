---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use LMS MCP tools to query live course data from the LMS backend.

## Available Tools

- `lms_health` — Check if the LMS backend is healthy and report the item count
- `lms_labs` — List all labs available in the LMS
- `lms_learners` — List all learners registered in the LMS
- `lms_pass_rates` — Get pass rates (avg score and attempt count per task) for a lab
- `lms_timeline` — Get submission timeline (date + submission count) for a lab
- `lms_groups` — Get group performance (avg score + student count per group) for a lab
- `lms_top_learners` — Get top learners by average score for a lab
- `lms_completion_rate` — Get completion rate (passed / total) for a lab
- `lms_sync_pipeline` — Trigger the LMS sync pipeline

## Strategy

### When the user asks about lab data without specifying a lab

If the user asks for scores, pass rates, completion, groups, timeline, or top learners **without naming a lab**:

1. Call `lms_labs` first to get all available labs
2. Use the `mcp_webchat_ui_message` tool with `type: "choice"` to let the user pick a lab
3. Use each lab's `title` field as the label and `id` as the value
4. Once the user selects a lab, call the appropriate tool with the selected lab ID

### When the user asks about general LMS status

- For "Is the backend healthy?" or similar → call `lms_health`
- For "What labs are available?" → call `lms_labs`
- For "How many learners?" → call `lms_learners`

### Formatting responses

- Format percentages with one decimal place (e.g., "89.1%")
- Show counts as integers
- When comparing multiple labs, present data in a table format
- Keep responses concise — state the answer first, then offer to show more details

### When the user asks "what can you do?"

Explain your current capabilities clearly:

- You can query the LMS backend for lab information, pass rates, completion rates, timelines, group performance, and top learners
- You can check if the LMS backend is healthy
- You can trigger the LMS sync pipeline
- You need a lab identifier for most detailed queries (scores, timeline, groups, etc.)

## Response Style

- Use `mcp_webchat_ui_message` for lab selection when multiple labs are available
- Fall back to plain text if the channel doesn't support interactive messages
- Be concise — give the answer first, then offer follow-up options
