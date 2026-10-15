---
name: s2-cloudroom
description: Access the S2TechSecurity Cloudroom GUI fork and operate configured self-hosted Cloudroom Core sessions from S2TECH1.
---

# S2 Cloudroom

Use the local fork at `/mnt/d/dev/S2-Cloudroom-GUI`. The Windows location is `D:\dev\S2-Cloudroom-GUI`. For Cloudroom Core operations use the audited wrapper:

```bash
python3 /mnt/d/dev/S2-Cloudroom-GUI/integrations/openclaw/cloudroomctl.py status
python3 /mnt/d/dev/S2-Cloudroom-GUI/integrations/openclaw/cloudroomctl.py repo
```

When Core is configured and `core_ready` is true, supported commands are:

```bash
python3 /mnt/d/dev/S2-Cloudroom-GUI/integrations/openclaw/cloudroomctl.py start --harness codex --request-id task001
python3 /mnt/d/dev/S2-Cloudroom-GUI/integrations/openclaw/cloudroomctl.py session --session cr_task001
python3 /mnt/d/dev/S2-Cloudroom-GUI/integrations/openclaw/cloudroomctl.py prompt --session cr_task001 --request-id prompt001 --text 'Inspect this repository'
python3 /mnt/d/dev/S2-Cloudroom-GUI/integrations/openclaw/cloudroomctl.py events --session cr_task001
```

Important: Do not assume a session is complete after HTTP 202; check its events and receipt. Choose a fresh request ID per operation. Only close a session after being asked to or after confirming its work is no longer needed.

Cloudroom GUI is an Electron application. Its source checkout does not mean the GUI or Core is running. This skill operates the repository and an independently configured Cloudroom Core. The GUI has no verified OpenClaw-native driver.

Core binds to loopback only. The CLI reads the bearer token from a protected file identified by `CLOUDROOM_TOKEN_FILE`; never print or commit that token. Never install Cloudroom Core in the existing S2TECH1 production WSL user environment, expose API ports, grant agent sudo/Docker access, or operate other infrastructure without explicit authorisation. If the API is unavailable, say so clearly. Never claim Cloudroom computer use is active based on repository access or this skill alone.

Respect existing dirty files and use a feature branch for modifications. No destructive Git, network exposure, financial spending, or production deployment without explicit approval. Refer to `integrations/openclaw/README.md` for exact support limits.
