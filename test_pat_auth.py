#!/usr/bin/env python3
"""
Test script for PAT authentication via HTTP headers.
"""

import requests
import json
import sys

def test_pat_authentication(host="127.0.0.1", port=8000, pat_token="test-pat-token"):
    """Test PAT authentication with the HTTP server."""
    
    base_url = f"http://{host}:{port}"
    headers = {"X-Azure-DevOps-PAT": pat_token}
    
    print(f"Testing PAT authentication on {base_url}")
    print(f"Using PAT token: {pat_token[:10]}..." if len(pat_token) > 10 else f"Using PAT token: {pat_token}")
    print()
    
    try:
        # Test server info endpoint (GET /)
        print("1. Testing server info endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Error: {response.text}")
        print()
        
        # Test connection tool without PAT (should fail)
        print("2. Testing connection without PAT header...")
        response = requests.post(f"{base_url}/mcp", json={
            "method": "tools/call",
            "params": {
                "name": "test_connection",
                "arguments": {}
            }
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
        
        # Test connection tool with PAT
        print("3. Testing connection with PAT header...")
        response = requests.post(f"{base_url}/mcp", 
            headers=headers,
            json={
                "method": "tools/call", 
                "params": {
                    "name": "test_connection",
                    "arguments": {}
                }
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Error: {response.text}")
        print()
        
        # Test server info tool with PAT
        print("4. Testing server info tool with PAT header...")
        response = requests.post(f"{base_url}/mcp",
            headers=headers,
            json={
                "method": "tools/call",
                "params": {
                    "name": "get_server_info", 
                    "arguments": {}
                }
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
    except requests.ConnectionError:
        print(f"Error: Could not connect to server at {base_url}")
        print("Make sure the server is running with:")
        print("  python -m azure_devops_mcp.main your-org --mode http --authentication pat")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # You can provide custom PAT token as command line argument
    pat_token = sys.argv[1] if len(sys.argv) > 1 else "test-pat-token-12345"
    
    print("=" * 60)
    print("PAT Authentication Test")
    print("=" * 60)
    
    success = test_pat_authentication(pat_token=pat_token)
    
    if success:
        print("\nTest completed!")
    else:
        print("\nTest failed!")
        sys.exit(1)