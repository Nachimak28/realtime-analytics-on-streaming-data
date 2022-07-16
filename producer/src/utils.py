from datetime import datetime
from pytz import timezone

def get_current_time():
    # Getting current time with indian timezone
    india_tz = timezone('Asia/Kolkata')
    time = datetime.now(india_tz)
    ist_time = time.strftime('%Y-%m-%d_%H-%M-%S')
    return ist_time