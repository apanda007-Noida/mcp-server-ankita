import argparse
import sys
from datetime import datetime
from pulse.orchestrator import run_pulse
from pulse.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description="Automated Weekly App Review Pulse CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run Command
    run_parser = subparsers.add_parser("run", help="Trigger a manual run for a specific product and ISO week")
    run_parser.add_argument("--product", type=str, required=True, help="Target product (e.g., Groww)")
    run_parser.add_argument("--week", type=str, required=True, help="ISO Week (e.g., 2026-W24)")
    
    # Schedule Command
    schedule_parser = subparsers.add_parser("schedule", help="Start the background cron scheduler")
    
    args = parser.parse_args()
    
    logger = setup_logger("cli_logger")
    
    if args.command == "run":
        logger.info(f"Manual run triggered for {args.product} on week {args.week}")
        run_pulse(args.product, args.week)
    elif args.command == "schedule":
        logger.info("Scheduler started. Waiting for next cron trigger...")
        # Stub for scheduler
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Scheduler stopped.")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
