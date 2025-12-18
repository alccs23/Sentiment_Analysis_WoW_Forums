from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from scraper import run_forum_scraper


def scheduled_scrape():
    
    run_forum_scraper(page_scrape_num=1)


def main():
    """
    Initializes and starts the APScheduler. It will exectue every TODO:{FIGURE OUT HOW LONG} minutes...
    ... so that enough time will pass for the NLP and database loading can take place before filtered_data.json gets flushed
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    scheduler = BlockingScheduler(timezone="UTC")

    scheduler.add_job(
        scheduled_scrape,
        trigger=IntervalTrigger(hours=6),
        id="forum_scraper_job",
        name="Blizzard Forum Scraper",
        replace_existing=True,
        next_run_time=datetime.utcnow()
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
