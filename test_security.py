#!/usr/bin/env python3
"""
Security Verification Test Suite
Tests all authentication fixes and security enhancements
"""

import sys
import os
import requests
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:5000"

def print_header(text):
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}{text:^70}")
    print(f"{Fore.CYAN}{'=' * 70}\n")

def print_test(name):
    print(f"{Fore.YELLOW}[TEST] {name}")

def print_pass(message):
    print(f"{Fore.GREEN}  [PASS] {message}")

def print_fail(message):
    print(f"{Fore.RED}  [FAIL] {message}")

def print_info(message):
    print(f"{Fore.BLUE}  [INFO] {message}")

def test_direct_route_access():
    """Test that protected routes redirect to login"""
    print_test("Direct Protected Route Access")

    protected_routes = [
        '/api/scan',
        '/logout'
    ]

    session = requests.Session()

    for route in protected_routes:
        try:
            response = session.get(f"{BASE_URL}{route}", allow_redirects=False)

            if response.status_code in [302, 307]:
                if '/login' in response.headers.get('Location', '') or response.headers.get('Location', '') == '/':
                    print_pass(f"{route} → Redirected to login (Status: {response.status_code})")
                else:
                    print_fail(f"{route} → Wrong redirect: {response.headers.get('Location')}")
            elif response.status_code == 401:
                print_pass(f"{route} → Returned 401 Unauthorized")
            else:
                print_fail(f"{route} → Unexpected status: {response.status_code}")

        except Exception as e:
            print_fail(f"{route} → Error: {str(e)}")

def test_api_protection():
    """Test API endpoints return proper 401"""
    print_test("API Endpoint Protection")

    try:
        response = requests.post(
            f"{BASE_URL}/api/scan",
            json={"url": "https://example.com"},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 401:
            data = response.json()
            if 'error' in data and 'Authentication required' in data['error']:
                print_pass(f"API returns 401 with proper JSON error")
                print_info(f"Response: {data}")
            else:
                print_fail(f"API returns 401 but wrong error format: {data}")
        else:
            print_fail(f"API should return 401, got {response.status_code}")

    except Exception as e:
        print_fail(f"Error: {str(e)}")

def test_security_headers():
    """Test security headers are present"""
    print_test("Security Headers Verification")

    try:
        response = requests.get(f"{BASE_URL}/")

        required_headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': 'default-src'
        }

        for header, expected_value in required_headers.items():
            if header in response.headers:
                header_value = response.headers[header]
                if expected_value in header_value:
                    print_pass(f"{header}: {header_value[:50]}...")
                else:
                    print_fail(f"{header} present but value unexpected")
            else:
                print_fail(f"{header} is missing!")

    except Exception as e:
        print_fail(f"Error: {str(e)}")

def test_login_functionality():
    """Test that legitimate login still works"""
    print_test("Legitimate Login Functionality")

    session = requests.Session()

    try:
        # Get login page first to get CSRF token
        response = session.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print_fail(f"Cannot access login page: {response.status_code}")
            return

        print_pass("Login page accessible")

        # Try to login (will fail with wrong credentials, but tests endpoint)
        login_data = {
            'email': 'admin@ssipmt.com',
            'password': 'WrongPassword123'
        }

        response = session.post(f"{BASE_URL}/", data=login_data, allow_redirects=False)

        # Should stay on login page or redirect back with error
        if response.status_code in [200, 302]:
            print_pass("Login endpoint functional (tested with wrong credentials)")
        else:
            print_fail(f"Login endpoint returned unexpected status: {response.status_code}")

    except Exception as e:
        print_fail(f"Error: {str(e)}")

def test_guest_only_routes():
    """Test that @guest_only decorator works"""
    print_test("Guest-Only Route Protection")

    print_info("This test requires manual verification:")
    print_info("1. Login with valid credentials")
    print_info("2. Try to access http://localhost:5000/")
    print_info("3. Should redirect to /dashboard automatically")
    print_info("4. Try to access http://localhost:5000/signup")
    print_info("5. Should also redirect to /dashboard")

def test_bypass_login_works():
    """Verify the intentional bypass login buttons route to /scan"""
    print_test("Bypass Login Buttons (intended feature)")

    try:
        response = requests.get(f"{BASE_URL}/")
        html_content = response.text

        bypass_count = html_content.count(
            "onclick=\"window.location.href='/scan'\""
        )

        if bypass_count >= 2:
            print_pass(f"Bypass buttons present (found {bypass_count})")
        else:
            print_fail(f"Bypass buttons missing from login page (found {bypass_count})")

        # The bypass only works if /scan is reachable without login
        scan_response = requests.get(
            f"{BASE_URL}/scan", allow_redirects=False
        )
        if scan_response.status_code == 200:
            print_pass("/scan accessible anonymously (bypass works)")
        else:
            print_fail(
                f"/scan returned {scan_response.status_code} for anonymous user"
            )

    except Exception as e:
        print_fail(f"Error: {str(e)}")

def main():
    print_header("SECURITY VERIFICATION TEST SUITE")
    print_info(f"Testing application at: {BASE_URL}")
    print_info("Make sure the application is running!")
    print()

    # Run all tests
    tests = [
        test_bypass_login_works,
        test_direct_route_access,
        test_api_protection,
        test_security_headers,
        test_login_functionality,
        test_guest_only_routes
    ]

    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print_fail(f"Test crashed: {str(e)}")

    print_header("TEST SUITE COMPLETE")
    print(f"{Fore.CYAN}Review the results above to verify all security fixes.")
    print(f"{Fore.CYAN}All critical vulnerabilities should show PASS status.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]

    try:
        # Check if server is running
        requests.get(f"{BASE_URL}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}ERROR: Cannot connect to {BASE_URL}")
        print(f"{Fore.YELLOW}Make sure the application is running:")
        print(f"{Fore.YELLOW}  python app.py")
        sys.exit(1)

    main()
