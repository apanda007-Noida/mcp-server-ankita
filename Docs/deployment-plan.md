# Railway Deployment Plan

This document outlines how to deploy the Google Workspace MCP Server (`google-mcp-server`) to [Railway.app](https://railway.app). 

Because the server runs in the cloud unattended, we must inject secrets securely via Environment Variables instead of using local `.json` files.

## 1. Prerequisites
Before deploying, ensure you have:
1. Created an **OAuth 2.0 Client ID (Desktop App)** in Google Cloud Console.
2. Downloaded the JSON and successfully authenticated locally at least once, generating the `token.json` file.
3. Both `credentials.json` and `token.json` **must be added to your `.gitignore`** so they are not pushed to GitHub.

## 2. Pushing to GitHub
Railway automatically deploys code from a GitHub repository. 
1. Commit the entire `google-mcp-server` directory to your repository.
2. Push the changes to GitHub.

## 3. Creating the Railway Project
1. Log into your [Railway account](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select the repository containing your MCP server.
4. Railway will scan the repository. Because we created a `Procfile` and `requirements.txt` inside `google-mcp-server`, it will know exactly how to install dependencies and start the FastAPI server.

## 4. Configuring Environment Variables
For the server to authenticate with Google without prompting for a browser login, you must provide your credentials via Environment Variables.

In the Railway Dashboard, click on your deployed service, go to the **Variables** tab, and add the following three variables:

### `REQUIRE_APPROVAL`
- **Value**: `false`
- **Why**: Our FastAPI server has a safety feature that blocks and asks for `y/n` input in the terminal. Since Railway doesn't have an interactive terminal, this variable tells the server to bypass the manual prompt and auto-approve requests.

### `GOOGLE_CREDENTIALS_JSON`
- **Value**: Open your local `google-mcp-server/credentials.json` file, copy the **entire raw JSON content**, and paste it here.

### `GOOGLE_TOKEN_JSON`
- **Value**: Open your local `google-mcp-server/token.json` file, copy the **entire raw JSON content**, and paste it here.

## 5. Deployment and Verification
Once the variables are saved:
1. Railway will automatically trigger a redeployment.
2. Go to the **Deployments** tab and click **View Logs**.
3. You should see `Starting Google MCP Server on port...`
4. The server is now running securely in the cloud!
