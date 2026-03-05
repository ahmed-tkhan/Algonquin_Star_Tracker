"""
Background scheduler for the Algonquin Stargazing Service.

Uses APScheduler to fire the nightly check at the configured time every day
while the process is running.
"""

from __future__ import annotations

import logging
import signal
import time
from types import FrameType
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import config
from .service import run_check

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def _job() -> None:
    """APScheduler job callback."""
    try:
        run_check()
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected error during stargazing check: %s", exc)


def start(run_immediately: bool = False) -> BackgroundScheduler:
    """
    Start the background scheduler.

    Parameters
    ----------
    run_immediately:
        If ``True``, also run a check right away (useful for testing / manual
        invocations so you don't have to wait until the scheduled time).

    Returns
    -------
    BackgroundScheduler
        The running scheduler instance.
    """
    global _scheduler  # noqa: PLW0603

    scheduler = BackgroundScheduler(timezone=config.TIMEZONE)
    trigger = CronTrigger(
        hour=config.POLL_HOUR,
        minute=config.POLL_MINUTE,
        timezone=config.TIMEZONE,
    )
    scheduler.add_job(_job, trigger, id="nightly_check", replace_existing=True)
    scheduler.start()
    _scheduler = scheduler

    logger.info(
        "Scheduler started – nightly check will run at %02d:%02d (%s).",
        config.POLL_HOUR,
        config.POLL_MINUTE,
        config.TIMEZONE,
    )

    if run_immediately:
        logger.info("Running immediate check as requested.")
        _job()

    return scheduler


def stop() -> None:
    """Gracefully stop the background scheduler if it is running."""
    global _scheduler  # noqa: PLW0603
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
    _scheduler = None


def run_forever(run_immediately: bool = False) -> None:
    """
    Start the scheduler and block until a SIGINT or SIGTERM is received.

    This is the main loop used when the service runs as a standalone daemon.
    """
    scheduler = start(run_immediately=run_immediately)

    def _handle_exit(signum: int, _frame: Optional[FrameType]) -> None:
        logger.info("Signal %s received – shutting down.", signum)
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, _handle_exit)
    signal.signal(signal.SIGTERM, _handle_exit)

    print(
        f"\nAlgonquin Stargazing Service is running.\n"
        f"  Nightly check scheduled at "
        f"{config.POLL_HOUR:02d}:{config.POLL_MINUTE:02d} {config.TIMEZONE}.\n"
        f"  Press Ctrl-C to stop.\n"
    )

    while scheduler.running:
        time.sleep(1)

    logger.info("Service exited cleanly.")
