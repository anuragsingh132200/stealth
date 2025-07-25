import os
from celery.schedules import crontab

# Broker settings
broker_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
result_backend = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Task execution settings
task_track_started = True
task_time_limit = 30 * 60  # 30 minutes
task_soft_time_limit = 25 * 60  # 25 minutes

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 100
worker_hijack_root_logger = False
worker_send_task_events = True
worker_enable_remote_control = True

# Beat settings (for scheduled tasks)
beat_schedule = {
    # Example scheduled task (can be removed if not needed)
    'cleanup-old-jobs': {
        'task': 'app.tasks.cleanup_old_jobs',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}

# Result backend settings
result_expires = 60 * 60 * 24 * 7  # 1 week

# Task routing
task_routes = {
    'app.tasks.process_job': {'queue': 'jobs'},
}

# Enable events for monitoring
worker_send_task_events = True
task_send_sent_event = True
event_queue_expires = 60  # 1 minute
event_queue_ttl = 5  # 5 seconds
worker_cancel_long_running_tasks_on_connection_loss = True

# Task time limits
task_annotations = {
    'app.tasks.process_job': {'time_limit': 300, 'soft_time_limit': 240},
}

# Security settings
worker_send_task_events = True
task_send_sent_event = True
event_serializer = 'json'
