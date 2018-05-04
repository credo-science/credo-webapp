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

# Fields required in every request

| Field | Description | Constraint |
| --- | --- | --- |
| `device_id` | Device ID | 50 characters or fewer |
| `device_type` | Device type | 50 characters or fewer |
| `device_model` | Device model | 50 characters or fewer |
| `system_version` | System version | 50 characters or fewer |
| `app_version` | Application version | 50 characters or fewer |


# Endpoints
## /api/v2/user/register
Register user

| Field | Description | Constraint |
| --- | --- | --- |
| `email` | User email address | Valid email address |
| `username` | Desired username | 50 characters or fewer; letters, digits and @/./+/-/_ only |
| `display_name` | User display name | 50 characters or fewer |
| `password` | User password | 128 characters or fewer |
| `team` | Name of the team to join | 50 characters or fewer, empty string indicates no team |
| `language` | User language code (ISO 639-1) | 10 characters or fewer |

**Authorization:** none

**Example request:** [register.json](sample-payloads/requests/register.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/user/login
Login user

| Field | Description | Constraint |
| --- | --- | --- |
| `email` | User email address | Valid email address. |
| `username` | Username | 50 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `password` | User password | 128 characters or fewer. |

**Required fields:** `username`/`email` and `password`

**Authorization:** username/email + password

**Example request:** [login.json](sample-payloads/requests/login.json)

**Example response:** [login_success.json](sample-payloads/responses/login_success.json)

**On success:** HTTP_2xx (optional message)

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/user/info
Get or update user info

| Field | Description | Constraint |
| --- | --- | --- |
| `display_name` | User display name | 50 characters or fewer |
| `team` | Name of the team to join | 50 characters or fewer, empty string indicates no team |
| `language` | User language code (ISO 639-1) | 10 characters or fewer |

**Required fields:** none

**Authorization:** token

**Example requests:**
* [info.json](sample-payloads/requests/info.json)
* [info2.json](sample-payloads/requests/info2.json)

**Example response:** [info_success.json](sample-payloads/responses/info_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/start (Not implemented)

**Authorization:** token

**On success:** HTTP_2xx (optional message)

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/detection
Submit detection

| Field | Description | Constraint |
| --- | --- | --- |
| `detections` | List of submitted detections | - |

### Detection object

| Field | Description | Constraint |
| --- | --- | --- |
| `id` | Detection id | Integer |
| `accuracy` | Location accuracy | Floating point number |
| `altitude` | Altitude | Floating point number |
| `frame_content` | Base64 encoded PNG | 5000 characters or fewer |
| `height` | - | Integer |
| `width` | - | Integer |
| `latitude` | GPS latitude | Floating point number |
| `longitude` | GPS longitude | Floating point number |
| `provider` | Location provider | 20 characters or fewer |
| `timestamp` | UNIX timestamp of detection time | Integer |

**Required fields:** all except `frame_content`

**Authorization:** token

**Example request:** [detection.json](sample-payloads/requests/detection.json)

**Example response:** [detection_success.json](sample-payloads/responses/detection_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/ping


| Field | Description | Constraint |
| --- | --- | --- |
| `delta_time` | Time since last detection / ping / startup | Integer |
| `timestamp` | UNIX timestamp of ping time | Integer |

**Authorization:** token

**Example request:** [ping.json](sample-payloads/requests/ping.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)
