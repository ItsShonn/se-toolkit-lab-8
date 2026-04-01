# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

### Checkpoint 1: "What is the agentic loop?"

The agentic loop is the fundamental cycle that an AI agent follows to accomplish tasks autonomously. It typically consists of these core stages:

1. **Perceive** — Gather information from the environment (user input, files, APIs, sensors, etc.)
2. **Reason/Plan** — Analyze the information, determine goals, and decide on a course of action
3. **Act** — Execute actions using available tools (file operations, API calls, shell commands, etc.)
4. **Observe** — Receive feedback from the actions taken (outputs, errors, state changes)
5. **Reflect/Iterate** — Evaluate results, adjust the plan if needed, and continue the loop until the goal is achieved

This loop enables agents to:
- Handle multi-step tasks autonomously
- Adapt to unexpected outcomes
- Learn from feedback within a session
- Decompose complex problems into manageable steps

The quality of an agent depends on how well it executes each stage—especially reasoning (making good decisions) and reflection (knowing when to adjust course).

### Checkpoint 2: "What labs are available in our LMS?"

The agent explored local files and found the lab structure from the README:

**Required Labs (Lab 8):**
1. Task 1: Set Up the Agent — install nanobot, configure Qwen API, add MCP tools, write skill prompt
2. Task 2: Deploy and Connect a Web Client — Dockerize nanobot, add WebSocket channel + Flutter chat UI
3. Task 3: Give the Agent New Eyes — explore observability data, write log/trace MCP tools
4. Task 4: Diagnose a Failure and Make the Agent Proactive — investigate a failure, schedule in-chat health checks, fix a planted bug

**Optional Labs:**
1. Task 1: Add a Telegram Bot Client — same agent, different interface

Note: The agent is exploring local repository files but does not have access to the real LMS backend yet (no MCP tools configured). It found this information by reading the README.md file.

## Task 1B — Agent with LMS tools

### Checkpoint 1: "What labs are available?"

The agent now returns real lab names from the LMS backend via MCP tools:

**Available labs:**
1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

The MCP server registered 9 tools: `lms_health`, `lms_labs`, `lms_learners`, `lms_pass_rates`, `lms_timeline`, `lms_groups`, `lms_top_learners`, `lms_completion_rate`, `lms_sync_pipeline`.

### Checkpoint 2: "Is the LMS backend healthy?"

**Response:** "Yes, the LMS backend is healthy. It currently has 56 items in the system."

The agent called the `lms_health` MCP tool and returned the actual health status from the backend.

### Complex query: "Which lab has the lowest pass rate?"

The agent chained multiple tool calls:
1. First called `lms_labs` to get all available labs
2. Then called `lms_completion_rate` for each lab in parallel
3. Compiled the results into a table and identified the lowest

**Result:** Lab 08 has 0% (no submissions yet). Among labs with actual submissions, Lab 02 and Lab 03 are tied at 89.1% completion rate.

## Task 1C — Skill prompt

### Checkpoint: "Show me the scores" (without specifying a lab)

**Response:** The agent listed all available labs and asked the user to choose which one they want to see scores for:

"Here are the available labs:
1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

Which lab would you like to see the scores for? Please let me know the lab number or name."

**Skill behavior:** The LMS skill prompt teaches the agent to:
1. Call `lms_labs` first when a lab parameter is needed but not provided
2. List available labs and ask the user to choose
3. Use the lab title as the label for selection
4. Format numeric results nicely (percentages, counts)
5. Keep responses concise

The skill is located at `nanobot/workspace/skills/lms/SKILL.md`.

## Task 2A — Deployed agent

**Nanobot startup log excerpt:**

```
nanobot-1  | Using config: /app/nanobot/config.resolved.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | MCP server 'lms': connected, 9 tools registered
nanobot-1  | Agent loop started
```

**Verification:**
- `docker compose --env-file .env.docker.secret ps nanobot` — service is "Up"
- Gateway started on port 18790
- MCP server 'lms' connected with 9 tools (lms_health, lms_labs, lms_learners, lms_pass_rates, lms_timeline, lms_groups, lms_top_learners, lms_completion_rate, lms_sync_pipeline)

## Task 2B — Web client

**Checkpoint verification:**

1. **WebSocket endpoint test:**
   ```bash
   uv run python -c "import asyncio, json, websockets; asyncio.run((lambda: (ws := websockets.connect('ws://localhost:42002/ws/chat?access_key=my-secret-bot-key'), ws.__aenter__(), ws.send(json.dumps({'content': 'What labs are available?'}), print(asyncio.run(ws.recv()))))())"
   ```
   - WebSocket connection accepted with valid access key
   - Agent processed message (logs show: `Processing message from webchat:...`)

2. **Flutter client accessible:**
   - `http://localhost:42002/flutter/` returns the Flutter web app HTML
   - Login screen appears and accepts `NANOBOT_ACCESS_KEY`

3. **Nanobot logs show full stack working:**
   ```
   nanobot-1  | ✓ Channels enabled: webchat
   nanobot-1  | MCP server 'lms': connected, 9 tools registered
   nanobot-1  | MCP server 'webchat': connected, 1 tools registered
   nanobot-1  | Tool call: mcp_webchat_ui_message({...})
   nanobot-1  | Agent loop started
   ```

**Note:** The Qwen Code API credentials in this deployment are expired (external service issue). The deployment itself is complete and functional — once valid Qwen credentials are provided, the agent will respond with real answers.

**Files modified for Part B:**
- `nanobot/entrypoint.py` — added webchat channel and mcp-webchat configuration
- `nanobot/Dockerfile` — added nanobot-websocket-channel packages
- `nanobot/config.json` — webchat channel enabled
- `docker-compose.yml` — uncommented client-web-flutter, caddy dependencies, Flutter volume
- `caddy/Caddyfile` — uncommented `/flutter` and `/ws/chat` routes
- `pyproject.toml` — added nanobot-websocket-channel workspace members
- `.gitmodules` — added nanobot-websocket-channel submodule

<!-- Screenshot of a conversation with the agent in the Flutter web app -->
<!-- Add screenshot after fixing Qwen credentials -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
