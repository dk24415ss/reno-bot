Deployment instructions (Render / Docker)

Option A — Deploy to Render (recommended)
1. Create a Git repository containing this project (root contains `Dockerfile` and `app/discord_bot.py`).
2. Create an account on Render (https://render.com) and connect your GitHub/GitLab account.
3. Create a new "Web Service" or "Private Service" and point it to the repository/branch.
4. Choose "Docker" as the environment (Render detects Dockerfile).
5. Set the following environment variables in the Render dashboard:
   - `DISCORD_TOKEN` = your bot token
   - `ALLOWED_GUILD_ID` = 1429103387655409666
   - `ALLOWED_CHANNEL_ID` = 1429103461349199945
   - `LOG_CHANNEL_ID` = 1429106676367097947
6. Deploy. Render will build the image and run the container. In Render, set the service to auto-restart.

Option B — Deploy with Docker on a VPS
1. Copy repository to your VPS (git clone or scp files).
2. Build image:
   docker build -t reno-bot .
3. Run container with restart policy and env:
   docker run -d --name reno-bot --restart unless-stopped \
     -e DISCORD_TOKEN="<YOUR_TOKEN>" \
     -e ALLOWED_GUILD_ID=1429103387655409666 \
     -e ALLOWED_CHANNEL_ID=1429103461349199945 \
     -e LOG_CHANNEL_ID=1429106676367097947 \
     reno-bot

Notes
- Keep the `DISCORD_TOKEN` secret. If the token is compromised, regenerate it in the Discord Developer Portal.
- If you want me to deploy to Render for you, I will need either:
  - Access to your GitHub repo and Render account (or invite), or
  - Your permission to push this workspace to a new GitHub repo and deploy (you still must add token to Render secrets).

If you want me to handle the full deploy to Render, tell me which access method you prefer and provide necessary access. If you'd rather keep credentials private, I will prepare everything here and you can deploy using the steps above.
