# Enabling Network Access for RAG Scraper

## Security Warning ⚠️

By default, RAG Scraper only accepts connections from the local machine (localhost/127.0.0.1) for security reasons. Enabling network access allows other computers to connect to your server, which could be a security risk if you're on an untrusted network.

## Why External IP Doesn't Work by Default

When you run `python start_server.py`, the server binds to `127.0.0.1` (localhost), which:
- Only accepts connections from the same machine
- Ignores connection attempts from external IPs
- Provides security by limiting access

## How to Enable Network Access

### Method 1: Environment Variable (Recommended)

```bash
# Set the host to accept all connections
export RAG_SCRAPER_HOST=0.0.0.0

# Run the server
python start_server.py
```

### Method 2: Use the Network-Enabled Script

```bash
# Run the network-enabled server
python start_server_network.py
```

This script:
- Sets host to `0.0.0.0` (accepts connections from any IP)
- Shows your local IP address
- Provides clear warnings about network access

### Method 3: Direct Configuration

```python
# In your Python code
from src.config.app_config import get_app_config

config = get_app_config()
config.host = "0.0.0.0"  # Accept from any IP
# OR
config.host = "192.168.1.100"  # Accept only from specific IP
```

## Finding Your IP Address

### On Linux/Mac:
```bash
ifconfig | grep "inet "
# or
ip addr show
```

### On Windows:
```cmd
ipconfig
```

Look for your IPv4 address (usually starts with 192.168.x.x or 10.x.x.x on local networks).

## Accessing from Other Computers

Once network access is enabled:

1. **Find your server's IP address** using the commands above
2. **On the other computer**, open a browser and go to:
   ```
   http://YOUR_IP_ADDRESS:8085
   ```
   Replace `YOUR_IP_ADDRESS` with your actual IP (e.g., `http://192.168.1.100:8085`)

## Firewall Considerations

If you still can't connect from other computers:

### Linux (Ubuntu/Debian):
```bash
# Allow port 8085
sudo ufw allow 8085

# Check firewall status
sudo ufw status
```

### Windows:
1. Open Windows Defender Firewall
2. Click "Allow an app or feature"
3. Add Python and allow port 8085

### Mac:
1. System Preferences → Security & Privacy → Firewall
2. Click "Firewall Options"
3. Add Python to allowed applications

## Security Best Practices

1. **Only enable network access when needed**
2. **Use it only on trusted networks** (not public WiFi)
3. **Consider using a reverse proxy** (nginx) for production
4. **Implement authentication** if exposing to network
5. **Use HTTPS** for sensitive data

## Troubleshooting

### "Connection Refused" Error
- Check the server is running with `0.0.0.0` as host
- Verify the port (8085) is not blocked by firewall
- Ensure you're using the correct IP address

### "Site Can't Be Reached" Error
- Verify both computers are on the same network
- Check if you can ping the server: `ping YOUR_IP_ADDRESS`
- Make sure to include `http://` in the URL

### Port Already in Use
```bash
# Find what's using port 8085
lsof -i :8085  # Linux/Mac
netstat -ano | findstr :8085  # Windows

# Use a different port
export RAG_SCRAPER_PORT=9000
```

## Example Network Setup

```bash
# Terminal 1 (Server machine)
export RAG_SCRAPER_HOST=0.0.0.0
export RAG_SCRAPER_PORT=8085
python start_server.py

# Output will show:
# Starting RAG Scraper server...
# Access at: http://0.0.0.0:8085
# Running on http://0.0.0.0:8085

# Terminal 2 (Server machine - find IP)
ifconfig | grep "inet "
# Example output: inet 192.168.1.100

# Browser (Client machine)
# Navigate to: http://192.168.1.100:8085
```