"""Entrypoint — runs the ping-rent workflow without the agent.

Usage:
    python run.py

The orchestrator polls Pararius indefinitely (Ctrl-C to stop).
"""

import sys

print("ping-rent: starting workflow…")

try:
    from orchestrator import main
except ImportError as exc:
    print(f"Import error — is your virtualenv active and requirements installed? {exc}")
    sys.exit(1)

try:
    main()
except KeyboardInterrupt:
    print("\nping-rent: stopped by user.")
    sys.exit(0)
except Exception as exc:
    print(f"ping-rent: fatal error — {exc}")
    sys.exit(1)
