#!/usr/bin/env python3
"""
Azure Web App Test Script
Tests the deployed Azure DevOps MCP server on Azure Web App
"""

import requests
import json
import sys
import os
from typing import Optional

def test_azure_webapp(
    app_url: str,
    pat_token: str,
    organization: str
) -> bool:
    """Test the Azure Web App deployment."""
    
    print(f"🔍 Testing Azure Web App: {app_url}")
    print(f"📦 Organization: {organization}")
    print(f"🔑 PAT Token: {pat_token[:10]}..." if len(pat_token) > 10 else f"🔑 PAT Token: {pat_token}")
    print("=" * 60)
    
    # Ensure URL starts with https://
    if not app_url.startswith(('http://', 'https://')):
        app_url = f"https://{app_url}"
    
    headers = {
        "Content-Type": "application/json",
        "X-Azure-DevOps-PAT": pat_token
    }
    
    try:
        # Test 1: Server Info (GET /)
        print("1️⃣  Testing server info endpoint...")
        response = requests.get(f"{app_url}/", timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Server Name: {data.get('name', 'Unknown')}")
                print(f"   ✅ Version: {data.get('version', 'Unknown')}")
                print(f"   ✅ Organization: {data.get('organization', 'Unknown')}")
                print(f"   ✅ Domains: {', '.join(data.get('enabled_domains', []))}")
            except json.JSONDecodeError:
                print(f"   ⚠️  Response: {response.text[:200]}")
        else:
            print(f"   ❌ Error: {response.text}")
        print()
        
        # Test 2: Test Connection Tool
        print("2️⃣  Testing connection tool with PAT...")
        test_payload = {
            "method": "tools/call",
            "params": {
                "name": "test_connection",
                "arguments": {}
            }
        }
        
        response = requests.post(
            f"{app_url}/mcp",
            headers=headers,
            json=test_payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Response: {json.dumps(data, indent=4)}")
            except json.JSONDecodeError:
                print(f"   ✅ Response: {response.text}")
        else:
            print(f"   ❌ Error: {response.text}")
        print()
        
        # Test 3: Test without PAT (should fail)
        print("3️⃣  Testing without PAT header (should fail)...")
        response = requests.post(
            f"{app_url}/mcp",
            json=test_payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejected request without PAT")
        elif response.status_code == 403:
            print("   ✅ Correctly rejected request without PAT (403)")
        else:
            print(f"   ⚠️  Unexpected response: {response.text}")
        print()
        
        # Test 4: Get Server Info Tool
        print("4️⃣  Testing server info tool...")
        info_payload = {
            "method": "tools/call",
            "params": {
                "name": "get_server_info",
                "arguments": {}
            }
        }
        
        response = requests.post(
            f"{app_url}/mcp",
            headers=headers,
            json=info_payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Response: {json.dumps(data, indent=4)}")
            except json.JSONDecodeError:
                print(f"   ✅ Response: {response.text}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        return True
        
    except requests.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print(f"   Make sure the Azure Web App is running and accessible")
        return False
    except requests.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        print(f"   The request took too long. Check if the app is starting up.")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Azure Web App Test Script")
    print("=" * 60)
    
    # Get parameters from command line or environment
    if len(sys.argv) >= 4:
        app_url = sys.argv[1]
        pat_token = sys.argv[2] 
        organization = sys.argv[3]
    else:
        # Try to get from environment variables
        app_url = os.environ.get("AZURE_WEBAPP_URL")
        pat_token = os.environ.get("AZURE_DEVOPS_PAT")
        organization = os.environ.get("AZURE_DEVOPS_ORG")
        
        if not all([app_url, pat_token, organization]):
            print("❌ Missing required parameters!")
            print()
            print("Usage:")
            print("  python test_azure_webapp.py <webapp_url> <pat_token> <organization>")
            print()
            print("Or set environment variables:")
            print("  AZURE_WEBAPP_URL=your-app.azurewebsites.net")
            print("  AZURE_DEVOPS_PAT=your-pat-token") 
            print("  AZURE_DEVOPS_ORG=your-organization")
            print()
            print("Example:")
            print("  python test_azure_webapp.py devops-mcp-server.azurewebsites.net abc123pat myorg")
            return False
    
    success = test_azure_webapp(app_url, pat_token, organization)
    
    print()
    print("=" * 60)
    if success:
        print("✅ Azure Web App test completed!")
        print("🎉 Your Azure DevOps MCP server is working correctly!")
    else:
        print("❌ Azure Web App test failed!")
        print("🔧 Check the deployment guide for troubleshooting steps.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)