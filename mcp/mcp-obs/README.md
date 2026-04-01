# mcp-obs

MCP server for observability tools (VictoriaLogs and VictoriaTraces).

## Tools

- `mcp_obs_logs_search` — Search VictoriaLogs using LogsQL
- `mcp_obs_logs_error_count` — Count errors per service over a time window
- `mcp_obs_traces_list` — List recent traces for a service
- `mcp_obs_traces_get` — Fetch a specific trace by ID

## Usage

```bash
python -m mcp_obs
```

## Environment Variables

- `NANOBOT_VICTORIALOGS_URL` — VictoriaLogs URL (default: `http://localhost:42010`)
- `NANOBOT_VICTORIATRACES_URL` — VictoriaTraces URL (default: `http://localhost:42011`)
