import os
import csv
from datetime import datetime
from . import config

def init_log():
    """Initialize the skipped stories log file with headers if it doesn't exist."""
    if not os.path.exists(config.SKIPPED_STORIES_LOG):
        with open(config.SKIPPED_STORIES_LOG, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "story_id", "token_count", "reason"])

def log_skipped_story(story_id: str, reason: str, token_count: int = 0):
    """
    Log a skipped story to the CSV file.
    
    Args:
        story_id: The unique ID of the story.
        reason: The reason why it was skipped (e.g., "Too long").
        token_count: approximate token count if available.
    """
    init_log() # Ensure header exists
    
    with open(config.SKIPPED_STORIES_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            story_id,
            token_count,
            reason
        ])
