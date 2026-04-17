#!/usr/bin/env python3
"""
cli.py — Arc Fleet Unified CLI

Replaces: run_campaign.py

Usage:
    python cli.py --list
    python cli.py --vehicle mkz --module email --dry-run
    python cli.py --vehicle mkz --module email --live
    python cli.py --vehicle mkz --module formfill
    python cli.py --vehicle mkz --module formfill --submit
    python cli.py --vehicle mkz --module sms --dry-run
    python cli.py --vehicle mkz --module phone --dry-run
    python cli.py --vehicle all --module email --dry-run
    python cli.py --health

Or via Makefile:
    make list
    make dry-run
    make dry-run-mkz
    make health
"""

import argparse
import asyncio
import sys
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("arc-fleet")


def _banner(text: str):
    print(f"\n{'═' * 60}")
    print(f"  {text}")
    print(f"{'═' * 60}")


def cmd_list():
    """List all campaigns and their stats."""
    from campaigns import CampaignRegistry
    registry = CampaignRegistry()
    _banner("Arc Fleet Campaign Registry")
    for campaign in registry.all():
        s = campaign.summary()
        print(f"\n  [{s['slug']}] {s['vehicle']}")
        print(f"    VIN:      {s['vin']}")
        print(f"    Location: {s['location']}")
        print(f"    Asking:   {s['asking']}")
        print(f"    Contacts: {s['total_contacts']} total, {s['pending']} pending")
        if s.get("alert"):
            print(f"    ⚡ ALERT:  {s['alert']}")
    print()


def cmd_health():
    """Show all module health."""
    from modules import ModuleRegistry
    registry = ModuleRegistry()
    _banner("Module Health Report")
    report = registry.health_report()
    print(json.dumps(report, indent=2))
    print(f"\n  Summary: {registry}")
    print()


def cmd_run(vehicle_id: str, module: str, dry_run: bool, submit: bool = False):
    """Run a module against one or all campaigns."""
    from campaigns import CampaignRegistry
    registry = CampaignRegistry()

    if vehicle_id == "all":
        campaigns = registry.all()
    else:
        campaigns = [registry.get(vehicle_id)]

    for campaign in campaigns:
        _banner(f"{campaign.CAMPAIGN_ID} → {module} | {'DRY RUN' if dry_run else 'LIVE'}")

        if module == "email":
            from modules.email import EmailModule
            emailer = EmailModule()
            results = emailer.run_campaign(campaign, dry_run=dry_run)
            sent = sum(1 for r in results if r.get("status") == "SENT")
            logger.info(f"Email: {sent}/{len(results)} sent")

        elif module == "formfill":
            from modules.formfill import FormFiller
            filler = FormFiller(
                headless=True,
                submit=submit,
                screenshot_dir=f"screenshots/{campaign.CAMPAIGN_ID}",
            )
            results = asyncio.run(filler.run_campaign(campaign))

        elif module == "sms":
            from modules.sms import SMSModule
            sms = SMSModule()
            results = sms.send_campaign_sms(campaign.CAMPAIGN_ID, campaign.contacts)
            logger.info(f"SMS: {len(results)} processed")

        elif module == "phone":
            from modules.phone import PhoneModule
            phone = PhoneModule()
            summary = phone.run_pipeline(campaign.contacts, campaign)
            logger.info(f"Phone pipeline: {summary['qualified']}/{summary['wave_total']} qualified")

        else:
            logger.error(f"Unknown module: {module}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Arc Fleet Campaign CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --list
  python cli.py --health
  python cli.py --vehicle mkz --module email --dry-run
  python cli.py --vehicle mkz --module email --live
  python cli.py --vehicle mkz --module formfill
  python cli.py --vehicle mkz --module formfill --submit
  python cli.py --vehicle all --module email --dry-run
        """
    )
    parser.add_argument("--vehicle",
                        choices=["mkz", "towncar", "f350", "jayco", "all"],
                        help="Campaign to run")
    parser.add_argument("--module",
                        choices=["email", "formfill", "sms", "phone"],
                        help="Module to execute")
    parser.add_argument("--dry-run",  action="store_true", default=True,
                        help="Preview mode — no sends (default)")
    parser.add_argument("--live",     action="store_true",
                        help="Actually send/submit")
    parser.add_argument("--submit",   action="store_true",
                        help="Submit forms (formfill only, review screenshots first!)")
    parser.add_argument("--list",     action="store_true",
                        help="List all campaigns")
    parser.add_argument("--health",   action="store_true",
                        help="Show module health")
    args = parser.parse_args()

    if args.list:
        cmd_list()
        return

    if args.health:
        cmd_health()
        return

    if not args.vehicle or not args.module:
        parser.print_help()
        sys.exit(1)

    dry_run = not args.live
    cmd_run(args.vehicle, args.module, dry_run=dry_run, submit=args.submit)


if __name__ == "__main__":
    main()
