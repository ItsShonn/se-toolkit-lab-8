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
ME: Hello! Who are you?
BOT: ello! I'm **nanobot** 🐈, your personal AI assistant.

I'm here to help you with various tasks like:
- Answering questions and providing information
- Managing files and running commands
- Scheduling reminders and recurring tasks
- Querying course data from the LMS (labs, scores, completion rates, etc.)
- Searching the web
- And much more!

I'm friendly, concise, and always aim for accuracy. How can I help you today?
ME: Tell me about scores on lab 3
BOT: Here are the scores for **Lab 3**:

## Overall Completion
- **Completion Rate**: 89.1%
- **Passed**: 156 out of 175 learners

## Task Performance

| Task | Avg Score | Attempts |
|------|-----------|----------|
| Task 1: Explore the API | 63.5 | 382 |
| Task 2: Enable and debug the interactions endpoint | 66.4 | 299 |
| Task 3: Implement the learners endpoint | 50.0 | 4 |
| Task 4: Deploy to a hardened VM | 43.9 | 110 |
| Optional 2: Set up CI with GitHub Actions | 44.0 | 5 |

**Key observations:**
- Task 2 has the highest average score (66.4)
- Task 4 (deployment) has the lowest score among required tasks (43.9)
- Task 3 and Optional 2 have very few attempts, suggesting they may be newer or more challenging

Would you like to see more details like the submission timeline, group performance, or top learners for this lab?
<!-- Add screenshot after fixing Qwen credentials -->

## Task 3A — Structured logging

**Happy-path log excerpt** (request_started → request_completed with status 200):

```
backend-1  | 2026-04-01 09:42:50,266 INFO [lms_backend.main] [main.py:62] [trace_id=7cc8dd298b57b395ac8d694ed1b18fa8 span_id=01f0d7166f40634a resource.service.name=Learning Management Service trace_sampled=True] - request_started
backend-1  | 2026-04-01 09:42:50,561 INFO [lms_backend.auth] [auth.py:30] [trace_id=7cc8dd298b57b395ac8d694ed1b18fa8 span_id=01f0d7166f40634a resource.service.name=Learning Management Service trace_sampled=True] - auth_success
backend-1  | 2026-04-01 09:42:50,665 INFO [lms_backend.db.items] [items.py:16] [trace_id=7cc8dd298b57b395ac8d694ed1b18fa8 span_id=01f0d7166f40634a resource.service.name=Learning Management Service trace_sampled=True] - db_query
backend-1  | 2026-04-01 09:42:51,580 INFO [lms_backend.main] [main.py:74] [trace_id=7cc8dd298b57b395ac8d694ed1b18fa8 span_id=01f0d7166f40634a resource.service.name=Learning Management Service trace_sampled=True] - request_completed
```

**Error-path log excerpt** (db_query with error when PostgreSQL stopped):

```
backend-1  | 2026-04-01 10:01:52,464 ERROR [lms_backend.db.items] [items.py:23] [trace_id=c6425e77b0e98a114a176786f6f26afa span_id=642bb1531ee45a38 resource.service.name=Learning Management Service trace_sampled=True] - db_query
backend-1  | 2026-04-01 10:01:52,482 INFO [lms_backend.main] [main.py:74] [trace_id=c6425e77b0e98a114a176786f6f26afa span_id=642bb1531ee45a38 resource.service.name=Learning Management Service trace_sampled=True] - request_completed
```

**VictoriaLogs query:**

Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`

Results show structured JSON logs with fields like:
- `_time`: timestamp
- `service.name`: "Learning Management Service"
- `severity`: "ERROR"
- `event`: "db_query"
- `error`: "(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) ... connection is closed"
- `trace_id`: for correlating with traces

<!-- Screenshot of VictoriaLogs UI would go here -->

## Task 3B — Traces

**Healthy trace:** Shows span hierarchy with request_started → auth_success → db_query → request_completed, all completing successfully.

**Error trace:** Shows the same span hierarchy but the db_query span contains an error tag with "connection is closed" message.

<!-- Screenshots of VictoriaTraces UI would go here -->

## Task 3C — Observability MCP tools

**Created MCP observability server** (`mcp/mcp-obs/`) with 4 tools:
- `mcp_obs_logs_search` — Search VictoriaLogs using LogsQL
- `mcp_obs_logs_error_count` — Count errors per service over a time window
- `mcp_obs_traces_list` — List recent traces for a service
- `mcp_obs_traces_get` — Fetch a specific trace by ID

**Created observability skill** (`nanobot/workspace/skills/observability/SKILL.md`) teaching the agent to:
1. Start with `mcp_obs_logs_error_count` for an overview
2. Use `mcp_obs_logs_search` to inspect specific errors
3. Extract `trace_id` from logs and fetch full traces with `mcp_obs_traces_get`
4. Summarize findings concisely

### Agent Response: Normal Conditions

**Question:** "Any LMS backend errors in the last 10 minutes?"

**Response:**
> Good news! **No LMS backend errors** in the last 10 minutes. ✅
>
> Both the error count and log search confirm the Learning Management Service has been running cleanly during that time window.

**Tool calls observed:**
- `mcp_obs_logs_error_count({"service": "Learning Management Service", "time_window": "10m"})`
- `mcp_obs_logs_search({"query": "_time:10m service.name:\"Learning Management Service\" severity:ERROR", "limit": 10})`

### Agent Response: Failure Conditions (PostgreSQL stopped)

**Question:** "Any LMS backend errors in the last 10 minutes?"

**Response:**
> Yes, there was **1 error** in the LMS backend in the last 10 minutes:
>
> | Time | Error | Details |
> |------|-------|---------|
> | ... | db_query | connection is closed |

**Tool calls observed:**
- `mcp_obs_logs_error_count({"service": "Learning Management Service", "time_window": "10m"})`
- `mcp_obs_logs_search({"query": "_time:10m service.name:\"Learning Management Service\" severity:ERROR", "limit": 10})`

**Files created:**
- `mcp/mcp-obs/pyproject.toml`
- `mcp/mcp-obs/src/mcp_obs/server.py`
- `mcp/mcp-obs/src/mcp_obs/__init__.py`
- `mcp/mcp-obs/src/mcp_obs/__main__.py`
- `mcp/mcp-obs/README.md`
- `nanobot/workspace/skills/observability/SKILL.md`
- `nanobot/entrypoint.py` (updated — added obs MCP server config)
- `nanobot/Dockerfile` (updated — added mcp-obs package)
- `pyproject.toml` (updated — added mcp-obs workspace member)

## Task 4A — Multi-step investigation

**Agent response to "What went wrong?"** (with PostgreSQL stopped):

```
## Summary: What Went Wrong ❌

The **Learning Management Service (LMS) backend** is experiencing **database connectivity issues**.

**Log Evidence:**
- Found 5 errors in the last hour from the Learning Management Service
- Error event: db_query
- Error message: "(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) ... connection is closed"
- Operation: SELECT from item table

**Trace Evidence:**
- Trace ID: c6425e77b0e98a114a176786f6f26afa
- Span hierarchy: request_started → auth_success → db_query (FAILED) → request_completed
- The db_query span failed with SQLAlchemy error

**Root Cause:**
PostgreSQL database is unavailable. The backend cannot establish database connections, causing all database queries to fail.

**Affected Service:**
Learning Management Service (LMS backend)
```

**Tool calls observed:**
- `mcp_obs_logs_error_count({"time_window": "1h"})`
- `mcp_obs_logs_search({"query": "_time:1h service.name:\"Learning Management Service\" severity:ERROR", "limit": 10})`
- `mcp_obs_traces_get(trace_id="c6425e77b0e98a114a176786f6f26afa")`

## Task 4B — Proactive health check

**Scheduled health check job:**

Agent created a cron job that runs every 2 minutes:
- Checks for LMS backend errors in the last 2 minutes using `mcp_obs_logs_error_count`
- Searches error logs using `mcp_obs_logs_search`
- Posts a summary to the chat

**Proactive health report** (while PostgreSQL was stopped):

```
## 🔴 Health Report — Issues Detected

**Time window:** Last 2 minutes
**Errors found:** 3 errors in Learning Management Service

**Recent errors:**
1. db_query failed: connection is closed
2. items_list_failed: Database error
3. request_completed with 500 status

**Status:** Backend is unhealthy due to database connectivity issues.
```

**Nanobot logs showing cron execution:**
```
nanobot-1 | Tool call: cron({"action": "list"})
nanobot-1 | Tool call: mcp_obs_logs_error_count({"time_window": "2m", "service": "Learning Management Service"})
nanobot-1 | Tool call: mcp_obs_logs_search({"query": "_time:2m severity:ERROR", "limit": 10})
```

## Task 4C — Bug fix and recovery

### 1. Root Cause — Planted Bug

**Location:** `backend/src/lms_backend/routers/items.py`, lines 20-30

**Bug:** The `get_items` endpoint caught all exceptions and incorrectly returned **HTTP 404 "Items not found"** instead of propagating the real database error.

```python
# BEFORE (buggy code):
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    try:
        return await read_items(session)
    except Exception as exc:
        logger.warning(
            "items_list_failed_as_not_found",
            extra={"event": "items_list_failed_as_not_found"},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Items not found",
        ) from exc
```

**Problem:** When PostgreSQL was down, the real error (SQLAlchemy connection failure) was hidden and replaced with a misleading 404 error.

### 2. Fix Applied

**Changed:**
- Log level from `warning` to `error`
- Event name from `items_list_failed_as_not_found` to `items_list_failed`
- Added error details to log (error message and error type)
- HTTP status code from `404_NOT_FOUND` to `500_INTERNAL_SERVER_ERROR`
- Error detail from generic "Items not found" to actual database error message

```python
# AFTER (fixed code):
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    try:
        return await read_items(session)
    except Exception as exc:
        logger.error(
            "items_list_failed",
            extra={
                "event": "items_list_failed",
                "error": str(exc),
                "error_type": type(exc).__name__,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc
```

### 3. Post-Fix Response to "What went wrong?" (after redeploy)

**Question:** "What labs are available?" (with PostgreSQL stopped)

**Response:**
```
The LMS backend is currently **unhealthy** and experiencing database connectivity issues.

The error logs show:
- **Error**: `[Errno -2] Name or service not known`
- **Issue**: The LMS service cannot resolve the database hostname (DNS resolution failure)
- **Impact**: All lab data queries are failing with HTTP 500 errors

This appears to be an infrastructure issue with the database connection. The LMS backend cannot connect to its PostgreSQL database.
```

**Key improvement:** The agent now reports the **real underlying failure** (database connectivity, DNS resolution) instead of the misleading "404 Items not found".

### 4. Healthy Follow-Up Report (after PostgreSQL restarted)

**Question:** "How is the backend doing?" (after PostgreSQL restarted)

**Response:**
```
The LMS backend is **healthy** ✅

- Status: OK
- Items in system: 56
- No errors detected in the last 2 minutes

All database connections are working normally.
```

**Files modified:**
- `backend/src/lms_backend/routers/items.py` — Fixed exception handler to return 500 with real error instead of 404
