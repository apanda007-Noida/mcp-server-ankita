import argparse
import sys
import time
import schedule
from datetime import datetime, timedelta
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
        logger.info("Scheduler started. Pipeline will run every Monday at 08:00 (Local Time)...")
        
        def run_weekly_job():
            # Calculate the ISO week for the previous week
            prev_week_date = datetime.now() - timedelta(days=7)
            iso_year, iso_week, _ = prev_week_date.isocalendar()
            week_str = f"{iso_year}-W{iso_week:02d}"
            
            logger.info(f"Cron triggered! Running pipeline for Groww, week: {week_str}")
            try:
                run_pulse("Groww", week_str)
            except Exception as e:
                logger.error(f"Scheduled run failed: {e}")

        # Schedule the job
        schedule.every().monday.at("08:00").do(run_weekly_job)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60) # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped.")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
