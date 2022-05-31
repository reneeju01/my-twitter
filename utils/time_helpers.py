from datetime import datetime
import pytz

def utc_now():
    return datetime.now(tz=pytz.utc)