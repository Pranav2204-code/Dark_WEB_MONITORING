"""
Celery worker configuration and tasks
"""
from celery import Celery
from celery.schedules import crontab
from loguru import logger

from .core.config import settings

# Create Celery app
celery_app = Celery(
    "darkweb_monitor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "scan-paste-sites": {
        "task": "app.celery_worker.scan_paste_sites",
        "schedule": crontab(minute="0", hour="*/1"),  # Every hour
    },
    "scan-forums": {
        "task": "app.celery_worker.scan_forums",
        "schedule": crontab(minute="0", hour="*/6"),  # Every 6 hours
    },
    "cleanup-old-data": {
        "task": "app.celery_worker.cleanup_old_data",
        "schedule": crontab(minute="0", hour="2"),  # Daily at 2 AM
    },
}


@celery_app.task(name="app.celery_worker.scan_paste_sites")
def scan_paste_sites():
    """
    Periodic task to scan paste sites for threats
    """
    logger.info("Starting paste site scan task")

    try:
        # Import here to avoid circular imports
        from .scrapers import PasteScraper
        from .nlp import threat_analyzer
        from .core.database import db
        from .models import ThreatModel
        from .alerting import notifier
        import asyncio

        async def run_scan():
            # Example: Scan a paste site
            # In production, you would configure multiple paste sites
            scraper = PasteScraper(
                site_url="https://pastebin.com",  # Example - replace with actual dark web paste sites
                site_name="Pastebin"
            )

            # Perform scraping
            threats = await scraper.scrape()
            logger.info(f"Found {len(threats)} potential threats from paste sites")

            # Process and store threats
            for threat_data in threats:
                # Perform NLP analysis
                intelligence = await threat_analyzer.analyze(
                    threat_data.content,
                    threat_data.title
                )

                # Create threat model
                threat_dict = threat_data.model_dump()
                threat_dict["intelligence"] = intelligence.model_dump()
                threat_dict["alert_triggered"] = False
                threat_dict["alert_sent"] = False

                # Store in database
                if db.db:
                    result = await db.db.threats.insert_one(threat_dict)
                    threat_dict["_id"] = result.inserted_id

                    # Check if alert should be triggered
                    # (In production, this would check against monitoring rules)
                    if threat_data.severity in ["critical", "high"]:
                        threat_model = ThreatModel(**threat_dict)
                        # Send alert
                        await notifier.send_alert(
                            threat_model,
                            channels=["email"],  # Configure based on settings
                        )

                        # Mark alert as sent
                        await db.db.threats.update_one(
                            {"_id": result.inserted_id},
                            {"$set": {"alert_sent": True}}
                        )

            logger.info("Paste site scan completed successfully")

        # Run async task
        asyncio.run(run_scan())

        return {"status": "success", "threats_found": 0}

    except Exception as e:
        logger.error(f"Error in paste site scan: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.celery_worker.scan_forums")
def scan_forums():
    """
    Periodic task to scan dark web forums
    """
    logger.info("Starting forum scan task")

    try:
        # Implement forum scanning logic here
        # Similar to paste site scanning but targeting dark web forums
        logger.info("Forum scan completed")
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error in forum scan: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.celery_worker.cleanup_old_data")
def cleanup_old_data():
    """
    Periodic task to clean up old data based on retention policy
    """
    logger.info("Starting data cleanup task")

    try:
        from datetime import datetime, timedelta
        from .core.database import db
        import asyncio

        async def run_cleanup():
            if not settings.CLEANUP_ENABLED:
                logger.info("Data cleanup is disabled")
                return

            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=settings.DATA_RETENTION_DAYS)

            # Delete old threats
            if db.db:
                result = await db.db.threats.delete_many({
                    "discovered_at": {"$lt": cutoff_date},
                    "reviewed": True,
                    "false_positive": True,
                })

                logger.info(f"Deleted {result.deleted_count} old threat records")

        asyncio.run(run_cleanup())

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.celery_worker.analyze_threat")
def analyze_threat(threat_id: str):
    """
    Analyze a specific threat with NLP
    """
    logger.info(f"Analyzing threat: {threat_id}")

    try:
        from .nlp import threat_analyzer
        from .core.database import db
        from bson import ObjectId
        import asyncio

        async def run_analysis():
            if db.db:
                # Get threat
                threat = await db.db.threats.find_one({"_id": ObjectId(threat_id)})

                if not threat:
                    logger.error(f"Threat not found: {threat_id}")
                    return {"status": "error", "error": "Threat not found"}

                # Perform analysis
                intelligence = await threat_analyzer.analyze(
                    threat["content"],
                    threat.get("title", "")
                )

                # Update threat with intelligence
                await db.db.threats.update_one(
                    {"_id": ObjectId(threat_id)},
                    {"$set": {"intelligence": intelligence.model_dump()}}
                )

                logger.info(f"Threat analysis completed: {threat_id}")
                return {"status": "success"}

        return asyncio.run(run_analysis())

    except Exception as e:
        logger.error(f"Error analyzing threat: {e}")
        return {"status": "error", "error": str(e)}
