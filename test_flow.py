#!/usr/bin/env python3
"""
Test script for SaaS API Load Testing Platform.
Tests the complete flow: signup -> login -> create test -> monitor test.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test-{int(datetime.now().timestamp())}@example.com"
TEST_PASSWORD = "TestPassword123!"

async def main():
    async with aiohttp.ClientSession() as session:
        print(f"\n{'='*60}")
        print(f"🔥 SaaS API Load Testing - Complete Flow Test")
        print(f"{'='*60}\n")

        # 1. Signup
        print("1️⃣  SIGNUP TEST")
        signup_data = {
            "name": "Test User",
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        async with session.post(f"{BASE_URL}/api/auth/signup", json=signup_data) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(result, indent=2, default=str)}")
            if resp.status != 201:
                print("   ❌ Signup failed!")
                return
            token = result.get("access_token")
            print(f"   ✓ Token: {token[:20]}...")

        # 2. Login
        print("\n2️⃣  LOGIN TEST")
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        async with session.post(f"{BASE_URL}/api/auth/login", json=login_data) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                token = result.get("access_token")
                print(f"   ✓ Login successful")
            else:
                print(f"   ❌ Login failed: {result}")
                return

        # 3. Get Profile
        print("\n3️⃣  GET PROFILE TEST")
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{BASE_URL}/api/auth/profile", headers=headers) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                print(f"   ✓ Profile retrieved")
                print(f"     Email: {result.get('email')}")
                print(f"     Plan: {result.get('subscription', {}).get('plan')}")
            else:
                print(f"   ❌ Failed to get profile: {result}")

        # 4. Create Test
        print("\n4️⃣  CREATE TEST")
        test_data = {
            "name": "Homepage Load Test",
            "urls": [
                {"url": "https://httpbin.org/get", "method": "GET"},
                {"url": "https://httpbin.org/post", "method": "POST"}
            ],
            "duration": 10,
            "concurrency": 5,
            "ramp_up": 0
        }
        async with session.post(f"{BASE_URL}/api/tests", json=test_data, headers=headers) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            if resp.status == 201:
                test_id = result.get("id")
                print(f"   ✓ Test created: {test_id}")
                print(f"     Name: {result.get('name')}")
                print(f"     Status: {result.get('status')}")
            else:
                print(f"   ❌ Failed to create test: {result}")
                return

        # 5. List Tests
        print("\n5️⃣  LIST TESTS")
        async with session.get(f"{BASE_URL}/api/tests", headers=headers) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                print(f"   ✓ Tests retrieved: {len(result)} total")
                for i, test in enumerate(result[:3]):
                    print(f"     [{i+1}] {test.get('name')} - Status: {test.get('status')}")
            else:
                print(f"   ❌ Failed to list tests: {result}")

        # 6. Get Test Details
        print(f"\n6️⃣  GET TEST DETAILS ({test_id})")
        await asyncio.sleep(1)  # Wait a bit for test execution to start
        async with session.get(f"{BASE_URL}/api/tests/{test_id}", headers=headers) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                print(f"   ✓ Test details retrieved")
                print(f"     Name: {result.get('name')}")
                print(f"     Status: {result.get('status')}")
                print(f"     Config: {json.dumps(result.get('config'), indent=6, default=str)}")
                if result.get('summary'):
                    print(f"     Summary: {json.dumps(result.get('summary'), indent=6, default=str)}")
            else:
                print(f"   ❌ Failed to get test details: {result}")

        # 7. Get User Stats
        print("\n7️⃣  GET USER STATS")
        async with session.get(f"{BASE_URL}/api/tests/stats/user", headers=headers) as resp:
            result = await resp.json()
            print(f"   Status: {resp.status}")
            if resp.status == 200:
                print(f"   ✓ Stats retrieved")
                print(f"     Total Tests: {result.get('total_tests')}")
                print(f"     Tests Today: {result.get('tests_today')}")
                print(f"     Plan: {result.get('plan')}")
                print(f"     Remaining Tests: {result.get('remaining_tests')}")
            else:
                print(f"   ❌ Failed to get stats: {result}")

        # 8. Wait for test completion and check again
        print("\n8️⃣  MONITORING TEST EXECUTION...")
        print("   Waiting 5 seconds for test to execute...")
        await asyncio.sleep(5)
        
        async with session.get(f"{BASE_URL}/api/tests/{test_id}", headers=headers) as resp:
            result = await resp.json()
            print(f"   Status after 5s: {result.get('status')}")
            if result.get('summary'):
                summary = result.get('summary')
                print(f"   ✓ Test completed with results:")
                print(f"     Total Requests: {summary.get('total')}")
                print(f"     Success: {summary.get('success')}")
                print(f"     Failed: {summary.get('failed')}")
            else:
                print(f"   ⏳ Test still running or pending...")
                print(f"   Current Status: {result.get('status')}")

        print(f"\n{'='*60}")
        print(f"✓ Test flow completed successfully!")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
