### Example of interacting with API using curl
```bash
curl -X POST 127.0.0.1:8000/api/v2/detection -d @detection.json -H "Authorization: Token aaaa01" -H "Content-Type: application/json"
```
# Authorization
### Username/email + password
In request body
```
{
  "username": "mrrobot",
  "password": "64yrJJKSxmYKpF8nuYLg",
  ...
  other data
  ...
}
```
or
```
{
  "email": "humanperson@notrobots.com",
  "password": "WzQp4XLJ5K6HgPMw",
  ...
  other data
  ...
}
```

### Token
HTTP header
```
Authorization: Token d403...a359
```

## Failed authorization
Server returns HTTP_401 (optional message)

# Endpoints
## /api/v2/user/register
Register user

| Field | Description | Constraint |
| --- | --- | --- |
| `email` | User email address | Valid email address. |
| `username` | Desired username | 50 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `display_name` | User display name | 50 characters or fewer. |
| `password` | User password | 128 characters or fewer. |
| `team` | Name of the team to join | 50 characters or fewer. |
| `language` | User language code (ISO 639-1) | 10 characters or fewer. |
| `device_id` | Device ID | 50 characters or fewer. |
| `device_type` | Device type | 50 characters or fewer. |
| `device_model` | Device model | 50 characters or fewer. |
| `system_version` | System version | 50 characters or fewer. |
| `app_version` | Application version | 50 characters or fewer. |

**Authorization:** none

**Example request:** [register.json](sample-payloads/requests/register.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/user/login
Login user

**Authorization:** username/email + password

**Example request:** [login.json](sample-payloads/requests/login.json)

**Example response:** [login_success.json](sample-payloads/responses/login_success.json)

**On success:** HTTP_2xx (optional message)

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/user/update_info
Update user info

**Authorization:** token

** Optional fields **
* `display_name`
* `team`
* `language`

**Example requests:**
* [update_info.json](sample-payloads/requests/update_info.json)
* [update_info2.json](sample-payloads/requests/update_info2.json)

**Example response:** [update_info_success.json](sample-payloads/responses/update_info_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/start (Not implemented)

**Authorization:** token

**On success:** HTTP_2xx (optional message)

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/detection
Submit detection

**Authorization:** token

**Example request:** [detection.json](sample-payloads/requests/detection.json)

**Example response:** [detection_success.json](sample-payloads/responses/detection_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/ping

**Authorization:** token

**Example request:** [ping.json](sample-payloads/requests/ping.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)
