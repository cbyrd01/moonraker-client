# Configuration

## Connection Options

### Base URL

The base URL should point to your Moonraker instance, typically on port 7125:

```python
client = MoonrakerClient("http://192.168.1.100:7125")
```

### Timeout

Default timeout is 30 seconds. Adjust for slow networks or large file uploads:

```python
client = MoonrakerClient("http://printer.local:7125", timeout=60.0)
```

## Authentication

Moonraker supports three authentication methods:

### API Key

The simplest method. Get your API key from Moonraker's configuration or via the API:

```python
client = MoonrakerClient(
    "http://printer.local:7125",
    api_key="your-api-key"
)
```

### JWT (JSON Web Token)

For user-based authentication with login credentials:

```python
# First, login to get tokens
client = MoonrakerClient("http://printer.local:7125")
result = client.access_login("username", "password")
token = result["token"]
refresh_token = result["refresh_token"]

# Use the JWT token
client = MoonrakerClient(
    "http://printer.local:7125",
    token=token
)

# Refresh when expired
new_result = client.access_refreshjwt(refresh_token)
```

### Oneshot Token

Single-use tokens for specific requests (e.g., file downloads in browsers):

```python
token = client.access_oneshottoken()
# Use within 5 seconds for a single request
```

## Environment Variables

For functional tests and CI, configure via environment variables:

```bash
export MOONRAKER_URL=http://your-printer:7125
export MOONRAKER_API_KEY=your-api-key  # optional
```
