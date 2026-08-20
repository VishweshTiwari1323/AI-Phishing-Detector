# API Documentation

## Overview

The AI Phishing Detection System provides a RESTful API for programmatic access to URL scanning functionality. All API endpoints require authentication via session cookies.

## Base URL

```
http://localhost:5000
```

## Authentication

### Login

**Endpoint:** `POST /`

**Description:** Authenticate a user and create a session.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "YourPassword123"
}
```

**Response:** HTTP 302 Redirect to `/scan` on success

**Example:**
```python
import requests

session = requests.Session()
response = session.post('http://localhost:5000/', data={
    'email': 'admin@ssipmt.com',
    'password': 'Admin@123'
})
```

### Logout

**Endpoint:** `GET /logout`

**Description:** Destroy the current session.

**Response:** HTTP 302 Redirect to `/`

---

## Scanning Endpoints

### Single URL Scan (Web)

**Endpoint:** `POST /scan`

**Description:** Scan a single URL through the web interface.

**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
- `url` (string, required): The URL to scan

**Response:** HTML page with scan results

---

### Single URL Scan (API)

**Endpoint:** `POST /api/scan`

**Description:** Scan a single URL and get JSON response.

**Authentication:** Required

**Rate Limit:** 20 requests per minute

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Response Body:**
```json
{
  "url": "https://example.com",
  "ml_prediction": "Safe Website",
  "confidence": 0.987,
  "virustotal": {
    "status": "Success",
    "malicious": 0,
    "suspicious": 0,
    "harmless": 67
  },
  "scan_id": 42
}
```

**Error Response:**
```json
{
  "error": "URL is required"
}
```

**Status Codes:**
- `200 OK`: Scan completed successfully
- `400 Bad Request`: Invalid URL or missing parameters
- `401 Unauthorized`: Not authenticated
- `429 Too Many Requests`: Rate limit exceeded

**Example:**
```python
import requests

session = requests.Session()

# Login first
session.post('http://localhost:5000/', data={
    'email': 'admin@ssipmt.com',
    'password': 'Admin@123'
})

# Scan URL
response = session.post('http://localhost:5000/api/scan', json={
    'url': 'https://google.com'
})

result = response.json()
print(f"Prediction: {result['ml_prediction']}")
print(f"VirusTotal Malicious: {result['virustotal']['malicious']}")
```

---

### Batch Scan

**Endpoint:** `POST /batch-scan`

**Description:** Scan multiple URLs at once (up to 50).

**Authentication:** Required

**Rate Limit:** 5 requests per hour

**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
- `urls` (textarea, required): One URL per line

**Response:** HTML page with batch scan results

---

## User Endpoints

### Sign Up

**Endpoint:** `POST /signup`

**Description:** Create a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass@123",
  "confirm_password": "SecurePass@123"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Response:** HTTP 302 Redirect to `/` on success

---

### Dashboard

**Endpoint:** `GET /dashboard`

**Description:** Get user statistics and recent scans.

**Authentication:** Required

**Response:** HTML page with dashboard

---

### Scan History

**Endpoint:** `GET /history`

**Description:** Get paginated scan history for the authenticated user.

**Authentication:** Required

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)

**Response:** HTML page with scan history

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/scan` | 30 per minute |
| `/api/scan` | 20 per minute |
| `/batch-scan` | 5 per hour |
| Default | 100 per hour |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 19
X-RateLimit-Reset: 1659888000
```

**Rate Limit Error:**
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

---

## Response Models

### ML Prediction Values
- `"Phishing Website"`: URL identified as phishing
- `"Safe Website"`: URL identified as safe
- `"Unknown"`: Unable to determine

### VirusTotal Status Values
- `"Success"`: Scan completed
- `"Submitted for scanning"`: URL queued for first-time scan
- `"VirusTotal API Key Missing"`: API key not configured
- `"VirusTotal Error"`: API request failed

---

## Error Handling

### Error Response Format
```json
{
  "error": "Error message description"
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

---

## Code Examples

### Python with Requests

```python
import requests

class PhishingDetectorClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, email, password):
        response = self.session.post(f'{self.base_url}/', data={
            'email': email,
            'password': password
        })
        return response.status_code == 200
    
    def scan_url(self, url):
        response = self.session.post(
            f'{self.base_url}/api/scan',
            json={'url': url}
        )
        return response.json()
    
    def get_history(self, page=1):
        response = self.session.get(
            f'{self.base_url}/history',
            params={'page': page}
        )
        return response.text
    
    def logout(self):
        self.session.get(f'{self.base_url}/logout')

# Usage
client = PhishingDetectorClient()
client.login('admin@ssipmt.com', 'Admin@123')

result = client.scan_url('https://google.com')
print(f"Result: {result['ml_prediction']}")

client.logout()
```

### JavaScript with Fetch

```javascript
class PhishingDetectorClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async login(email, password) {
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);

        const response = await fetch(`${this.baseURL}/`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });

        return response.ok;
    }

    async scanURL(url) {
        const response = await fetch(`${this.baseURL}/api/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url }),
            credentials: 'include'
        });

        return await response.json();
    }

    async logout() {
        await fetch(`${this.baseURL}/logout`, {
            credentials: 'include'
        });
    }
}

// Usage
const client = new PhishingDetectorClient();

(async () => {
    await client.login('admin@ssipmt.com', 'Admin@123');
    
    const result = await client.scanURL('https://google.com');
    console.log('Result:', result.ml_prediction);
    
    await client.logout();
})();
```

### cURL

```bash
# Login and save cookies
curl -c cookies.txt -X POST http://localhost:5000/ \
  -d "email=admin@ssipmt.com" \
  -d "password=Admin@123"

# Scan URL
curl -b cookies.txt -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Get history
curl -b cookies.txt http://localhost:5000/history

# Logout
curl -b cookies.txt http://localhost:5000/logout
```

---

## Security Best Practices

1. **Always use HTTPS in production**
2. **Store API credentials securely** (use environment variables)
3. **Implement proper error handling**
4. **Respect rate limits**
5. **Validate URLs before scanning**
6. **Don't expose VirusTotal API key**
7. **Use strong passwords**
8. **Enable CSRF protection** (enabled by default)

---

## Testing

### Unit Tests

```bash
# Run tests
python tests.py

# Run with coverage
pip install coverage
coverage run tests.py
coverage report
```

### Integration Testing

```python
import unittest
from app import app, db

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Setup test database
    
    def test_api_scan(self):
        # Login
        self.client.post('/', data={
            'email': 'test@example.com',
            'password': 'Test@123'
        })
        
        # Test scan
        response = self.client.post('/api/scan', json={
            'url': 'https://google.com'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('ml_prediction', data)
```

---

## Support

For API support or questions:
- Email: akshya1323@gmail.com
- GitHub Issues: https://github.com/VishweshTiwari1323/AI-Phishing-Detector/issues

---

## Changelog

### Version 2.0 (2026-08-07)
- Added REST API endpoints
- Implemented rate limiting
- Added authentication system
- Added batch scanning
- Added scan history
- Improved security

### Version 1.0 (Initial Release)
- Basic URL scanning
- ML prediction
- VirusTotal integration
