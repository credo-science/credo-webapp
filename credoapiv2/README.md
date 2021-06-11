# This documentation is aimed at app and tool developers. There is already a collection of tools for exporting and working with CREDO data available at [https://github.com/credo-science/credo-api-tools](https://github.com/credo-science/credo-api-tools)

### Example of interacting with API using cURL
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
| `language` | User language code ([ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)) | 10 characters or fewer |

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

## /api/v2/user/oauth_login (proposed, not yet implemented)
OAuth callback endpoint for logging in user. If field `new_account` in response is set to true, application should present a screen asking user to choose their display username and team.

| Field | Description | Constraint |
| --- | --- | --- |
| `authorization_code` | Authorization code received from provider | 128 characters or fewer. |
| `provider` | OAuth provider | Currently only `scistarter` |

**Example request:** [oauth_login.json](sample-payloads/requests/oauth_login.json)

**Example response:** [oauth_login_success.json](sample-payloads/responses/oauth_login_success.json)

**On success:** HTTP_2xx (optional message)

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/user/info
Get or update user info

| Field | Description | Constraint |
| --- | --- | --- |
| `display_name` | User display name | 50 characters or fewer |
| `team` | Name of the team to join | 50 characters or fewer, empty string indicates no team |
| `language` | User language code ([ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)) | 10 characters or fewer |

**Required fields:** none

**Authorization:** token

**Example requests:**
* [info.json](sample-payloads/requests/info.json)
* [info2.json](sample-payloads/requests/info2.json)

**Example response:** [info_success.json](sample-payloads/responses/info_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/user/id
Get unique user ID

**Method:** GET

**Authorization:** token

**Example response:** [id_success.json](sample-payloads/responses/id_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/detection
Submit detection

| Field | Description | Constraint |
| --- | --- | --- |
| `detections` | List of submitted detections | - |

### Detection object

| Field | Description | Constraint |
| --- | --- | --- |
| `accuracy` | Location accuracy (meters) | Floating point number |
| `altitude` | Altitude (meters) | Floating point number |
| `frame_content` | Base64 encoded and cropped PNG image of event | 10000 characters or fewer |
| `height` | Device sensor height | Integer |
| `width` | Device sensor width | Integer |
| `x` | X coordinate of event | Integer |
| `y` | Y coordinate of event | Integer |
| `latitude` | GPS latitude | Floating point number |
| `longitude` | GPS longitude | Floating point number |
| `provider` | Location provider | 20 characters or fewer |
| `timestamp` | UNIX timestamp of detection time (in milliseconds) | Integer |
| `metadata` | Additional metadata (JSON object serialized to string) | 10000 characters or fewer |

**Required fields:** all except `frame_content`, `height`, `width`, `x`, `y`, `metadata`

**Authorization:** token

**Example request:** [detection.json](sample-payloads/requests/detection.json)

**Example response:** [detection_success.json](sample-payloads/responses/detection_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/ping


| Field | Description | Constraint |
| --- | --- | --- |
| `delta_time` | Time since last detection / ping / startup (in milliseconds) | Integer |
| `on_time` | Duration of detector working and registering events (in milliseconds, resets every ping) | Integer |
| `timestamp` | UNIX timestamp of ping time (in milliseconds) | Integer |
| `metadata` | Additional metadata (JSON object serialized to string) | 10000 characters or fewer |

**Authorization:** token

**Example request:** [ping.json](sample-payloads/requests/ping.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/data_export
Request asynchronous data export.
Returns URL to file with results that will be available after finishing export.
Depending on number of events requested processing time may vary.

| Field | Description | Constraint |
| --- | --- | --- |
| `since` | Timestamp marking the beginning of exported data (using time_received)  (in milliseconds)| Integer |
| `until` | Timestamp marking the end of exported data (using time_received)  (in milliseconds)| Integer |
| `limit` | Limit number of entities in response, maximum: 500k (100k is recommended) | Integer |
| `data_type` | Type of exported resource, can be 'detection' or 'ping' | String |

**Authorization:** token (special permissions required)

**Throttling:** 400 requests / day / user (one every 5 minutes should be safe)

**Example request:** [data_export.json](sample-payloads/requests/data_export.json)

**Example response:** [data_export_success.json](sample-payloads/responses/data_export_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)

## /api/v2/mapping_export
Request asynchronous mapping export (user_id <-> username or device_id <-> device data).
Returns URL to file with results that will be available after finishing export.

| Field | Description | Constraint |
| --- | --- | --- |
| `mapping_type` | Type of exported mapping, can be 'device' or 'user' | String |

**Authorization:** token (special permissions required)

**Throttling:** 30 requests / day / user

**Example request:** [mapping_export.json](sample-payloads/requests/mapping_export.json)

**Example response:** [mapping_export_success.json](sample-payloads/responses/mapping_export_success.json)

**On success:** HTTP_2xx

**On failure:** HTTP_4xx/HTTP_5xx (optional message)
