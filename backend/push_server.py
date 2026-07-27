import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


mcp = FastMCP("push_server")


class PushModelArgs(BaseModel):
    message: str = Field(description="A brief message to push")


@mcp.tool()
def push(args: PushModelArgs):
    """Send a push notification with this brief message.
    
    Use this tool to send trade notifications, portfolio updates, or alerts.
    Example: push("Bought 10 shares of RELIANCE.NS at ₹2450")
    """
    print(f"Push: {args.message}")
    
    if not pushover_user or not pushover_token:
        print("ERROR: Pushover credentials not configured")
        return "Push failed: Missing credentials"
    
    payload = {
        "user": pushover_user,
        "token": pushover_token,
        "message": args.message
    }
    
    try:
        response = requests.post(pushover_url, data=payload, timeout=10)
        result = response.json()
        
        if result.get("status") == 1:
            print(f"Push sent successfully: {args.message[:50]}...")
            return "Push notification sent successfully"
        else:
            error_msg = result.get("errors", ["Unknown error"])
            print(f"Push failed: {error_msg}")
            return f"Push failed: {error_msg}"
            
    except requests.exceptions.Timeout:
        print("Push timeout")
        return "Push failed: Timeout"
    except Exception as e:
        print(f"Push error: {e}")
        return f"Push failed: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
