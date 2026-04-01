#!/usr/bin/env python3
"""
Entrypoint script for nanobot Docker container.

Reads config.json, injects environment variable values for secrets and
container-specific settings, writes config.resolved.json, then execs
into `nanobot gateway`.
"""

import json
import os
import sys


def main():
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    resolved_path = os.path.join(script_dir, "config.resolved.json")

    # Load base config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Inject LLM provider settings from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL")
    llm_api_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base_url:
        config["providers"]["custom"]["apiBase"] = llm_api_base_url
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model

    # Inject gateway settings from env vars
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)

    # Inject LMS MCP server settings from env vars
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")

    if "tools" not in config:
        config["tools"] = {}
    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}
    if "lms" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["lms"] = {"env": {}}

    if lms_backend_url:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
    if lms_api_key:
        config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Inject webchat channel settings from env vars
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")
    nanobot_access_key = os.environ.get("NANOBOT_ACCESS_KEY")

    if "channels" not in config:
        config["channels"] = {}

    if "webchat" not in config["channels"]:
        config["channels"]["webchat"] = {"enabled": True, "allowFrom": ["*"]}

    if webchat_host:
        config["channels"]["webchat"]["host"] = webchat_host
    if webchat_port:
        config["channels"]["webchat"]["port"] = int(webchat_port)
    if nanobot_access_key:
        config["channels"]["webchat"]["accessKey"] = nanobot_access_key

    # Inject webchat MCP server settings from env vars
    # The UI relay runs inside the webchat channel at port+1
    ui_relay_host = webchat_host or "0.0.0.0"
    ui_relay_port = int(webchat_port) + 1 if webchat_port else 8766

    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}

    if "webchat" not in config["tools"]["mcpServers"]:
        config["tools"]["mcpServers"]["webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {}
        }

    # Set UI relay URL and token for mcp-webchat
    config["tools"]["mcpServers"]["webchat"]["env"]["NANOBOT_UI_RELAY_URL"] = f"http://{ui_relay_host}:{ui_relay_port}"
    config["tools"]["mcpServers"]["webchat"]["env"]["NANOBOT_UI_RELAY_TOKEN"] = nanobot_access_key or ""

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Determine workspace directory
    workspace_dir = os.environ.get("NANOBOT_WORKSPACE", os.path.join(script_dir, "workspace"))

    # Exec into nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_path, "--workspace", workspace_dir])


if __name__ == "__main__":
    main()
