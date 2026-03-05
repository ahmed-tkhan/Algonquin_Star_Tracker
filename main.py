#!/usr/bin/env python3
"""
Entry point for the Algonquin Stargazing Service.

Usage
-----
Run as a background service (blocks until Ctrl-C / SIGTERM):

    python main.py

Run once immediately (for testing / manual checks):

    python main.py --now

Override the nightly poll time (e.g. 20:30):

    AST_POLL_HOUR=20 AST_POLL_MINUTE=30 python main.py
"""

from __future__ import annotations

import argparse
import logging
import sys


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s – %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Algonquin Park Stargazing Service – "
                    "nightly clear-sky & meteor-shower checker."
    )
    parser.add_argument(
        "--now",
        action="store_true",
        default=False,
        help="Run a check immediately (in addition to the scheduled time).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        default=False,
        help="Run a single check now and exit (do not start the scheduler).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Enable DEBUG logging.",
    )
    args = parser.parse_args()

    _configure_logging(args.verbose)

    if args.once:
        # One-shot mode: run and exit
        from stargazing_service.service import run_check  # noqa: PLC0415
        run_check()
        return

    # Daemon mode: run as a background service
    from stargazing_service.scheduler import run_forever  # noqa: PLC0415
    run_forever(run_immediately=args.now)


if __name__ == "__main__":
    main()
