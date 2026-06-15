from datetime import datetime
from dateutil.relativedelta import relativedelta
# pyrefly: ignore [missing-import]
# pyrefly: ignore [missing-import]
from google_play_scraper import Sort, reviews
# pyrefly: ignore [missing-import]
import emoji
# pyrefly: ignore [missing-import]
from langdetect import detect, DetectorFactory
# pyrefly: ignore [missing-import]
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent language detection
DetectorFactory.seed = 0

def fetch_reviews(app_package: str, weeks: int = 12, logger=None):
    """
    Fetch reviews for a given Google Play app package from the last N weeks.
    
    Args:
        app_package (str): The Google Play app package identifier.
        weeks (int): Number of weeks to look back.
        logger (Logger): Optional logger instance.
        
    Returns:
        list: A list of normalized review dictionaries.
    """
    cutoff_date = datetime.now() - relativedelta(weeks=weeks)
    
    if logger:
        logger.info(f"Fetching Play Store reviews for {app_package} since {cutoff_date.date()}")
    
    result, continuation_token = reviews(
        app_package,
        lang='en', # assuming English language analysis
        country='in', # assuming India given the fintech apps listed
        sort=Sort.NEWEST,
        count=100 # fetch in batches
    )
    
    all_reviews = []
    all_reviews.extend(result)
    
    # Paginate if the last review in the batch is still newer than the cutoff date
    while continuation_token and all_reviews[-1]['at'] > cutoff_date:
        result, continuation_token = reviews(
            app_package,
            continuation_token=continuation_token
        )
        all_reviews.extend(result)
        
    # Filter strictly by cutoff_date
    filtered_reviews = [r for r in all_reviews if r['at'] > cutoff_date]
    
    if logger:
        logger.info(f"Fetched {len(filtered_reviews)} reviews within the last {weeks} weeks.")
        
    return _normalize_reviews(filtered_reviews), filtered_reviews

def _normalize_reviews(raw_reviews):
    """
    Standardize the extracted data into a clean schema and filter out noise.
    Filters applied:
    1. Removes reviews with less than 8 words.
    2. Removes reviews containing emojis.
    3. Removes reviews not in English.
    """
    normalized = []
    for r in raw_reviews:
        content = r.get('content', '')
        if not content:
            continue
            
        # 1. Check word count
        if len(content.split()) < 8:
            continue
            
        # 2. Check for emojis
        if emoji.emoji_count(content) > 0:
            continue
            
        # 3. Check language
        try:
            if detect(content) != 'en':
                continue
        except LangDetectException:
            # If language cannot be detected (e.g. only punctuation), it's likely noise
            continue

        normalized.append({
            "rating": r.get('score'),
            "content": content
        })
    return normalized
