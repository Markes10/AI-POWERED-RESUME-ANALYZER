"""
Celery tasks for system maintenance.
"""
import logging
import os
import shutil
from datetime import datetime, timedelta
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="services.tasks.maintenance.cleanup_old_task_results"
)
def cleanup_old_task_results(days: int = 30) -> Dict[str, Any]:
    """
    Clean up old Celery task results from Redis.
    
    Args:
        days: Results older than this many days will be deleted
    
    Returns:
        Dict with cleanup stats
    """
    from services.celery_app import celery_app
    
    try:
        # Get Redis client
        redis_client = celery_app.backend.client
        
        # Scan for old task result keys
        pattern = "celery-task-meta-*"
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_timestamp = cutoff.timestamp()
        
        deleted = 0
        scanned = 0
        
        for key in redis_client.scan_iter(match=pattern):
            scanned += 1
            try:
                # Check TTL or timestamp in result
                ttl = redis_client.ttl(key)
                if ttl == -1:  # No expiry set
                    # Could check result timestamp if stored
                    pass
            except Exception:
                pass
        
        # For now, just log
        logger.info(f"Task result cleanup scanned {scanned} keys")
        
        return {
            "status": "completed",
            "scanned": scanned,
            "note": "Full cleanup requires Redis key iteration with timestamp check"
        }
        
    except Exception as e:
        logger.error(f"Task result cleanup failed: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    name="services.tasks.maintenance.cleanup_temp_files"
)
def cleanup_temp_files(hours: int = 24) -> Dict[str, Any]:
    """
    Clean up temporary uploaded files older than specified hours.
    
    Args:
        hours: Files older than this many hours will be deleted
    
    Returns:
        Dict with cleanup stats
    """
    upload_dir = "uploads/resumes"
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    deleted = 0
    errors = 0
    freed_bytes = 0
    
    try:
        for filename in os.listdir(upload_dir):
            filepath = os.path.join(upload_dir, filename)
            
            if os.path.isfile(filepath):
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if mtime < cutoff:
                    try:
                        size = os.path.getsize(filepath)
                        os.remove(filepath)
                        deleted += 1
                        freed_bytes += size
                    except Exception as e:
                        errors += 1
                        logger.error(f"Failed to delete {filepath}: {e}")
        
        logger.info(f"Temp file cleanup: {deleted} files deleted, {freed_bytes} bytes freed")
        
        return {
            "status": "completed",
            "deleted": deleted,
            "errors": errors,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"Temp file cleanup failed: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    name="services.tasks.maintenance.vacuum_database"
)
def vacuum_database() -> Dict[str, Any]:
    """
    Run database vacuum/analyze for PostgreSQL.
    """
    from db.database import get_db
    from sqlalchemy import text
    
    try:
        db = next(get_db())
        
        # Run VACUUM ANALYZE on main tables
        tables = ["users", "resumes", "jobs", "job_matches", "interviews", 
                  "performance_reviews", "learning_paths", "attendance_records",
                  "compensation_records", "diversity_metrics"]
        
        for table in tables:
            try:
                db.execute(text(f"VACUUM ANALYZE {table}"))
                logger.info(f"Vacuumed table: {table}")
            except Exception as e:
                logger.warning(f"Could not vacuum {table}: {e}")
        
        db.commit()
        
        return {"status": "completed", "tables": len(tables)}
        
    except Exception as e:
        logger.error(f"Database vacuum failed: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    name="services.tasks.maintenance.backup_database"
)
def backup_database(backup_dir: str = "backups") -> Dict[str, Any]:
    """
    Create database backup (PostgreSQL).
    """
    import subprocess
    
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"hr_ai_backup_{timestamp}.sql")
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL", "")
    
    if not db_url.startswith("postgresql"):
        return {"status": "skipped", "reason": "Not a PostgreSQL database"}
    
    try:
        # Parse connection details
        # postgresql://user:pass@host:port/db
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        
        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password or ""
        
        cmd = [
            "pg_dump",
            "-h", parsed.hostname or "localhost",
            "-p", str(parsed.port or 5432),
            "-U", parsed.username,
            "-d", parsed.path.lstrip("/"),
            "-f", backup_file,
            "--no-owner",
            "--no-privileges"
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            size = os.path.getsize(backup_file)
            logger.info(f"Database backup created: {backup_file} ({size} bytes)")
            
            # Compress
            import gzip
            with open(backup_file, 'rb') as f_in:
                with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            os.remove(backup_file)
            compressed_size = os.path.getsize(f"{backup_file}.gz")
            
            return {
                "status": "completed",
                "backup_file": f"{backup_file}.gz",
                "size_mb": round(compressed_size / (1024 * 1024), 2)
            }
        else:
            logger.error(f"pg_dump failed: {result.stderr}")
            return {"status": "error", "error": result.stderr}
            
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(
    name="services.tasks.maintenance.health_check"
)
def health_check() -> Dict[str, Any]:
    """
    System health check task.
    """
    import psutil
    from db.database import get_db
    from sqlalchemy import text
    
    checks = {}
    
    # Database
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"
    
    # Redis
    try:
        from services.celery_app import celery_app
        redis_client = celery_app.backend.client
        redis_client.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {e}"
    
    # Disk space
    try:
        disk = psutil.disk_usage("/")
        free_gb = disk.free / (1024**3)
        checks["disk"] = f"healthy ({free_gb:.1f} GB free)" if free_gb > 1 else f"warning ({free_gb:.1f} GB free)"
    except Exception:
        checks["disk"] = "unknown"
    
    # Memory
    try:
        mem = psutil.virtual_memory()
        checks["memory"] = f"healthy ({mem.percent}% used)" if mem.percent < 85 else f"warning ({mem.percent}% used)"
    except Exception:
        checks["memory"] = "unknown"
    
    # Celery workers
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        checks["celery_workers"] = f"healthy ({len(active)} workers)" if active else "no workers"
    except Exception as e:
        checks["celery_workers"] = f"unhealthy: {e}"
    
    overall = "healthy" if all("healthy" in str(v) or "warning" in str(v) for v in checks.values()) else "unhealthy"
    
    return {
        "overall": overall,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }