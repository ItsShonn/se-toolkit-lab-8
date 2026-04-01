"""MCP server for observability tools (VictoriaLogs and VictoriaTraces)."""

from __future__ import annotations

import json
import os
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("mcp-obs")

# Configuration from environment
_VICTORIALOGS_URL = os.environ.get("NANOBOT_VICTORIALOGS_URL", "http://localhost:42010")
_VICTORIATRACES_URL = os.environ.get("NANOBOT_VICTORIATRACES_URL", "http://localhost:42011")


class _LogsSearchQuery(BaseModel):
    query: str = Field(
        description="LogsQL query string. Examples: '_time:10m severity:ERROR', 'service.name:\"Learning Management Service\"'"
    )
    limit: int = Field(default=20, description="Maximum number of log entries to return")


class _LogsErrorCountQuery(BaseModel):
    time_window: str = Field(
        default="1h",
        description="Time window for counting errors. Examples: '10m', '1h', '24h'"
    )
    service: str = Field(
        default="",
        description="Optional service name filter. Examples: 'Learning Management Service', 'Qwen Code API'"
    )


class _TracesListQuery(BaseModel):
    service: str = Field(
        description="Service name to list traces for. Examples: 'Learning Management Service', 'Qwen Code API'"
    )
    limit: int = Field(default=10, description="Maximum number of traces to return")


class _TracesGetQuery(BaseModel):
    trace_id: str = Field(description="The trace ID to fetch. Example: 'c6425e77b0e98a114a176786f6f26afa'")


def _text(data: BaseModel | Sequence[BaseModel] | dict[str, Any] | str) -> list[TextContent]:
    """Convert data to MCP TextContent response."""
    if isinstance(data, BaseModel):
        payload: object = data.model_dump()
    elif isinstance(data, dict):
        payload = data
    elif isinstance(data, str):
        return [TextContent(type="text", text=data)]
    else:
        payload = [item.model_dump() if hasattr(item, "model_dump") else item for item in data]
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


async def _logs_search(args: _LogsSearchQuery) -> list[TextContent]:
    """Search VictoriaLogs using LogsQL query."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{_VICTORIALOGS_URL}/select/logsql/query"
            params = {"query": args.query, "limit": args.limit}
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            
            # Parse the response - VictoriaLogs returns newline-delimited JSON
            lines = response.text.strip().split("\n")
            results = []
            for line in lines:
                if line.strip():
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        results.append({"raw": line})
            
            if not results:
                return _text(f"No logs found for query: {args.query}")
            
            return _text({"query": args.query, "count": len(results), "logs": results})
        except httpx.HTTPError as e:
            return _text(f"Error querying VictoriaLogs: {type(e).__name__}: {e}")
        except Exception as e:
            return _text(f"Error: {type(e).__name__}: {e}")


async def _logs_error_count(args: _LogsErrorCountQuery) -> list[TextContent]:
    """Count errors per service over a time window."""
    time_window = args.time_window
    service_filter = f' service.name:"{args.service}"' if args.service else ""
    query = f"_time:{time_window} severity:ERROR{service_filter}"
    
    async with httpx.AsyncClient() as client:
        try:
            url = f"{_VICTORIALOGS_URL}/select/logsql/query"
            params = {"query": query, "limit": 1000}
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            
            # Parse and count errors by service
            lines = response.text.strip().split("\n")
            error_count = 0
            errors_by_service: dict[str, int] = {}
            recent_errors = []
            
            for line in lines:
                if line.strip():
                    try:
                        log_entry = json.loads(line)
                        service_name = log_entry.get("service.name", "unknown")
                        error_count += 1
                        errors_by_service[service_name] = errors_by_service.get(service_name, 0) + 1
                        
                        # Keep track of recent errors for summary
                        if len(recent_errors) < 5:
                            recent_errors.append({
                                "time": log_entry.get("_time", ""),
                                "service": service_name,
                                "event": log_entry.get("event", ""),
                                "error": log_entry.get("error", log_entry.get("_msg", ""))[:200]
                            })
                    except json.JSONDecodeError:
                        pass
            
            result = {
                "time_window": time_window,
                "total_errors": error_count,
                "errors_by_service": errors_by_service,
                "recent_errors": recent_errors
            }
            return _text(result)
        except httpx.HTTPError as e:
            return _text(f"Error counting errors: {type(e).__name__}: {e}")
        except Exception as e:
            return _text(f"Error: {type(e).__name__}: {e}")


async def _traces_list(args: _TracesListQuery) -> list[TextContent]:
    """List recent traces for a service."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{_VICTORIATRACES_URL}/select/jaeger/api/traces"
            params = {"service": args.service, "limit": args.limit}
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            traces = data.get("data", [])
            if not traces:
                return _text(f"No traces found for service: {args.service}")
            
            # Simplify trace data for response
            trace_summaries = []
            for trace in traces:
                trace_summaries.append({
                    "trace_id": trace.get("traceID", ""),
                    "spans": len(trace.get("spans", [])),
                    "start_time": trace.get("startTime", 0),
                    "duration": trace.get("duration", 0)
                })
            
            return _text({"service": args.service, "count": len(traces), "traces": trace_summaries})
        except httpx.HTTPError as e:
            return _text(f"Error listing traces: {type(e).__name__}: {e}")
        except Exception as e:
            return _text(f"Error: {type(e).__name__}: {e}")


async def _traces_get(args: _TracesGetQuery) -> list[TextContent]:
    """Fetch a specific trace by ID."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{_VICTORIATRACES_URL}/select/jaeger/api/traces/{args.trace_id}"
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            traces = data.get("data", [])
            if not traces:
                return _text(f"Trace not found: {args.trace_id}")
            
            trace = traces[0]
            
            # Build span hierarchy summary
            spans = trace.get("spans", [])
            span_summary = []
            for span in spans:
                span_info = {
                    "span_id": span.get("spanID", ""),
                    "operation": span.get("operationName", ""),
                    "service": span.get("process", {}).get("serviceName", ""),
                    "duration": span.get("duration", 0),
                    "tags": {tag["key"]: tag["value"] for tag in span.get("tags", []) if tag.get("key") in ["error", "http.status_code", "db.system"]}
                }
                span_summary.append(span_info)
            
            return _text({
                "trace_id": args.trace_id,
                "duration": trace.get("duration", 0),
                "span_count": len(spans),
                "spans": span_summary
            })
        except httpx.HTTPError as e:
            return _text(f"Error fetching trace: {type(e).__name__}: {e}")
        except Exception as e:
            return _text(f"Error: {type(e).__name__}: {e}")


# Tool registry
_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]
_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (model, handler, Tool(name=name, description=description, inputSchema=schema))


_register(
    "mcp_obs_logs_search",
    "Search VictoriaLogs using LogsQL. Use for finding logs by keyword, time range, severity, or service. Example query: '_time:10m service.name:\"Learning Management Service\" severity:ERROR'",
    _LogsSearchQuery,
    _logs_search,
)

_register(
    "mcp_obs_logs_error_count",
    "Count errors per service over a time window. Returns total count, breakdown by service, and recent error summaries.",
    _LogsErrorCountQuery,
    _logs_error_count,
)

_register(
    "mcp_obs_traces_list",
    "List recent traces for a service. Returns trace IDs, span counts, and durations.",
    _TracesListQuery,
    _traces_list,
)

_register(
    "mcp_obs_traces_get",
    "Fetch a specific trace by ID. Returns span hierarchy with operation names, services, and durations.",
    _TracesGetQuery,
    _traces_get,
)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available observability tools."""
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Call an observability tool by name."""
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


async def main() -> None:
    """Run the MCP observability server."""
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
