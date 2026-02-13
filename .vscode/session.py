import requests
import json

def load_mcp_config(config_file_path):
    print(f"Loading configuration from {config_file_path}...")
    with open(config_file_path, "r") as f:
        config = json.load(f)
        servers = config["servers"]
        if isinstance(servers, list):
            server_wrapper = next((s for s in servers if "Hf-mcp-server" in s), servers[0] if servers else {})
            server_config = server_wrapper.get("Hf-mcp-server", next(iter(server_wrapper.values()), {}))
        else:
            server_config = servers.get("Hf-mcp-server", servers.get("hf-mcp-server", {}))

        return {
            "url": server_config["url"],
            "headers": server_config.get("headers", {})
        }

def check_mcp_server(mcp_server):
    response = requests.get(mcp_server["url"], headers=mcp_server.get("headers", {}), timeout=10)
    if response.status_code == 200:
        print("MCP server is reachable and working!")
    else:
        print(f"MCP server responded with status code: {response.status_code}")
        print(f"Response text: {response.text[:100]}...")

if __name__ == "__main__":
    CONFIG_FILE = "mcp.json"
    mcp_server_config = load_mcp_config(CONFIG_FILE)
    check_mcp_server(mcp_server_config)