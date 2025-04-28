from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

#initialize the FastMCP object/server
mcp=FastMCP("weather")

NWS_API_URL = "https://api.weather.gov"
USER_AGENT = "weahter-app/1.0"

async def make_nws_request(url:str)->dict[str,any]|None:
    """
    Make a request to the NWS API and return the JSON response.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers,timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Error making request to NWS API: {e}")
        return None

def format_alert(feature:dict)->str:
    """
    Format the alert data into a string.
    """
    
    description = feature["properties"]["description"]
    area_desc = feature["properties"]["areaDesc"]
    effective = feature["properties"]["effective"]
    expires = feature["properties"]["expires"]
    
    return f"Description: {description}\nArea: {area_desc}\nEffective: {effective}\nExpires: {expires}"


@mcp.tool()
async def get_alerts(state:str)->str:
    """
    Get weather alerts for a given state.
    """
    url = f"{NWS_API_URL}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if data is None:
        return "Error fetching alerts."
    
    if not data["features"]:
        return "No active alerts."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n\n".join(alerts)

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"