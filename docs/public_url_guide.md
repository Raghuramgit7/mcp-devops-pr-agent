# How to Get a Public URL for Webhooks

GitHub runs on the public internet, but your agent service is running on your local machine (localhost). GitHub cannot "see" your localhost. You need a "tunnel" to expose your local port 8000 to the public internet.

## Option 1: Use VS Code Ports (Easiest if using VS Code)
1. Open the **Ports** view in VS Code (cmd+shift+p > "Ports: Focus on Ports View").
2. Click **Add Port** and enter `8000`.
3. Right-click the new row and check **Port Visibility**. Set it to **Public**.
4. Copy the "Local Address" (which should look like `https://...GithubCodespaces...` or similar).
5. Append `/webhook` to it.
   - Example: `https://abcd-1234.usw2.devtunnels.ms/webhook`

## Option 2: Use ngrok (Standard)
1. **Install ngrok**:
   ```bash
   brew install ngrok/ngrok/ngrok
   ```
2. **Sign up**: Go to [dashboard.ngrok.com](https://dashboard.ngrok.com/signup) and get your Authtoken.
3. **Connect account**:
   ```bash
   ngrok config add-authtoken <YOUR_TOKEN>
   ```
4. **Start the tunnel**:
   ```bash
   ngrok http 8000
   ```
5. **Copy the URL**:
   - Look for the line `Forwarding https://<random-id>.ngrok-free.app -> http://localhost:8000`.
   - Copy the `https://...` part.
   - **Important**: Append `/webhook` to the end.
   - Final URL: `https://<random-id>.ngrok-free.app/webhook`

## Where to paste this?
In your GitHub App settings:
1. Go to **General** > **Webhook URL**.
2. Paste the URL you generated above (e.g., `https://<id>.ngrok-free.app/webhook`).
3. Click **Save changes**.
4. Restart your agent service whenever you change this if you hardcoded it, but typically you don't need to updates the code, just the GitHub App config.
