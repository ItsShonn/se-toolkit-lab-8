# Observability Skill

You have access to observability tools for querying VictoriaLogs and VictoriaTraces. Use these tools to investigate system health, errors, and request traces.

## Available Tools

### Log Tools

- **`mcp_obs_logs_search`** — Search logs using LogsQL queries
  - Use for finding specific events, errors, or traces
  - Example queries:
    - `_time:10m severity:ERROR` — errors in last 10 minutes
    - `service.name:"Learning Management Service"` — logs from LMS backend
    - `_time:1h trace_id:abc123` — all logs for a specific trace

- **`mcp_obs_logs_error_count`** — Count errors per service
  - Use as first step when asked about errors
  - Returns total count, breakdown by service, and recent error summaries
  - Parameters:
    - `time_window`: e.g., "10m", "1h", "24h"
    - `service`: optional filter by service name

### Trace Tools

- **`mcp_obs_traces_list`** — List recent traces for a service
  - Use to find traces for a specific service
  - Returns trace IDs, span counts, and durations

- **`mcp_obs_traces_get`** — Fetch a specific trace by ID
  - Use to inspect the span hierarchy of a request
  - Shows operation names, services, durations, and error tags
  - Extract trace IDs from log results using the `trace_id` field

## Reasoning Flow

When the user asks about errors or system health:

1. **Start with `mcp_obs_logs_error_count`** to get an overview
   - Use a narrow time window like "10m" for recent issues
   - Filter by service if the user asks about a specific service

2. **Use `mcp_obs_logs_search`** to inspect specific errors
   - Query: `_time:10m severity:ERROR service.name:"Learning Management Service"`
   - Look for `trace_id` in the results

3. **Use `mcp_obs_traces_get`** if you found a relevant trace ID
   - Fetch the full trace to see the request flow
   - Identify which span failed and why

4. **Summarize findings concisely**
   - Don't dump raw JSON
   - Report: number of errors, affected services, root cause if found
   - Example: "Found 3 errors in the LMS backend in the last 10 minutes. All failures occurred in the database layer: 'connection is closed'. Trace c6425e77 shows the request failed at the db_query span."

## Examples

**User:** "Any errors in the last hour?"

**You:** Call `mcp_obs_logs_error_count(time_window="1h")` first, then summarize the results.

**User:** "What went wrong with the LMS backend?"

**You:** 
1. Call `mcp_obs_logs_error_count(time_window="10m", service="Learning Management Service")`
2. Call `mcp_obs_logs_search(query="_time:10m service.name:\"Learning Management Service\" severity:ERROR")`
3. If you find a trace_id, call `mcp_obs_traces_get(trace_id="...")`
4. Summarize the failure point

**User:** "Show me the trace for request abc123"

**You:** Call `mcp_obs_traces_get(trace_id="abc123")` and describe the span hierarchy.

## Tips

- Always use narrow time windows ("10m", "1h") to avoid overwhelming results
- Filter by `service.name` when the user asks about a specific service
- Look for `severity:ERROR` or `severity:WARN` in log queries
- Trace IDs are 32-character hex strings (e.g., `c6425e77b0e98a114a176786f6f26afa`)
- When you find an error in logs, extract the `trace_id` and fetch the full trace for context
