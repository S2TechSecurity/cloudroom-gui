# S2 Tech Cloudroom to OpenClaw bridge

This integration gives the local OpenClaw agent an explicit skill and a restricted Python standard-library client for the Cloudroom Core API. It also points the agent to the S2TechSecurity GUI source checkout.

## What works without Core

- Inspect the fork with `cloudroomctl.py repo`.
- Inspect Core availability with `cloudroomctl.py status`.
- Use the repo as an authorised development target.

## What requires a separately deployed Core

- Create Codex/Pi agent sessions, send prompts, check state/events, and close sessions.
- The tested upstream Core uses the local HTTP API on port 9840. Keep it loopback-only.
- Store its API token in a user-readable file with chmod 600; set `CLOUDROOM_TOKEN_FILE` in the environment. The bridge does not print secrets.
- Core's upstream setup requires a separate trusted Linux environment and agent isolation. Do not install it over S2TECH1's existing production services.
- Upstream GUI primarily supports macOS Apple Silicon. The Linux x64 release is alpha. A GUI window, Cloudroom computer-use session, and OpenClaw computer-use integration are NOT installed by this skill.

## Verification

```bash
python3 -m py_compile integrations/openclaw/cloudroomctl.py
python3 -m unittest discover -s integrations/openclaw -p 'test_*.py'
python3 integrations/openclaw/cloudroomctl.py repo
python3 integrations/openclaw/cloudroomctl.py status
openclaw skills list
```

## Restrictions

Only loopback HTTP endpoints can be used. No arbitrary URLs, shell execution by the bridge, raw bearer-token output, or automatic service installation. Commands that start Cloudroom agent work must be intentionally requested, and 202 acceptance is not completion. This is an early bridge, not a replacement for Cloudroom's UI or an unsupported native OpenClaw harness.

References: https://github.com/davidondrej/cloudroom-core/blob/main/docs/setup.md
