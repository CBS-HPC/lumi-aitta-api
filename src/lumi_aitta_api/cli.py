from __future__ import annotations

import argparse
import json
import sys

from .client import AittaClient, AittaError
from .settings import Settings, load_env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LUMI AITTA managed inference control API")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("models")
    commands.add_parser("status")
    for name in ("model", "workers", "preload"):
        command = commands.add_parser(name)
        command.add_argument("--model", required=True)
    args = parser.parse_args(argv)
    try:
        load_env()
        client = AittaClient(Settings.from_env())
        result = getattr(client, args.command)(args.model) if hasattr(args, "model") else getattr(client, args.command)()
        print(json.dumps(result, indent=2))
        return 0
    except (AittaError, ValueError, OSError) as exc:
        message = str(exc) if isinstance(exc, (AittaError, ValueError)) else type(exc).__name__
        print("Operation failed: " + message, file=sys.stderr)
        return 1
