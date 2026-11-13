"""Browser page for the ElevenLabs aragamago agent.

The widget runs in the phone browser. It does not start a Telegram poller
and it does not put an API key in the page. Auth on this agent is off, so
the public agent id is enough for the orb.
"""

AGENT_ID = "agent_2401km9rwrjkef7sn1a8yd2n663c"
TALK_PATH = "/talk"


def talk_page_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Aragamago</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #0b0d14;
      color: #f4f1ea;
      font-family: Georgia, "Times New Roman", serif;
    }}
    main {{
      max-width: 36rem;
      margin: 0 auto;
      padding: 2.5rem 1.25rem 6rem;
    }}
    h1 {{ font-size: 1.8rem; font-weight: 500; margin: 0 0 0.75rem; }}
    p {{ line-height: 1.5; color: #d9d3c7; }}
  </style>
</head>
<body>
  <main>
    <h1>Aragamago</h1>
    <p>Tap the orb and allow the microphone. This is the ElevenLabs voice. Telegram stays a separate chat.</p>
  </main>
  <script src="https://elevenlabs.io/convai-widget/index.js" async></script>
  <elevenlabs-convai agent-id="{AGENT_ID}"></elevenlabs-convai>
</body>
</html>
"""
