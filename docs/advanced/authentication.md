# Authentication

## Authentication Methods

Moonraker supports three authentication schemes:

### 1. API Key

Sent in the `X-Api-Key` header. Simplest method for trusted networks.

```python
client = MoonrakerClient("http://printer:7125", api_key="your-key")
```

### 2. JWT (Bearer Token)

JSON Web Tokens for user-based auth. Requires login flow.

```python
# Login
client = MoonrakerClient("http://printer:7125")
result = client.access_login("username", "password")
jwt = result["token"]
refresh = result["refresh_token"]

# Create authenticated client
auth_client = MoonrakerClient("http://printer:7125", token=jwt)

# Refresh when expired
new_result = client.access_refreshjwt(refresh)
```

### 3. Oneshot Token

Single-use tokens for requests that can't carry headers (WebSocket, file downloads):

```python
token = client.access_oneshottoken()
# Token expires in 5 seconds, single use only
```

## User Management

```python
# List users
users = client.access_users_list()

# Get current user
user = client.access_user()

# Change password
client.access_user_password("old_pass", "new_pass")

# Auth module info
info = client.access_info()

# Get/regenerate API key
key = client.access_apikey()
```
