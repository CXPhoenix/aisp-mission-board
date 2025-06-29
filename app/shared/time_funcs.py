from datetime import datetime, timezone, timedelta
from typing import Optional

def _get_zone(zone: int = 8) -> timezone:
    return timezone(timedelta(hours=zone), name='Asia/Taipei')

taipei_timezone = _get_zone()

def get_now(utc: int = 8) -> datetime:
    return datetime.now(_get_zone(utc))

def timediff(delta: int, unit: str = 'seconds', from_src: datetime = get_now()) -> datetime:
    _params = {unit: delta}
    return from_src + timedelta(**_params)

def format_datetime_to_taipei_dt(utc_dt: Optional[datetime]) -> datetime:
    """將一個 UTC 的 `datetime` 物件轉換為台北時區 (UTC+8) 的格式化字串。

    如果輸入的 `datetime` 物件為 `None`，則回傳字串 `N/A`。
    如果輸入的 `datetime` 物件是 naive (無時區資訊)，則會假設其代表 UTC 時間。

    Args:
        utc_dt (Optional[datetime]): 待轉換的 UTC `datetime` 物件。
        fmt (str, optional): 輸出的日期時間格式字串。
                             預設為 "%Y-%m-%d %H:%M:%S"。

    Returns:
        datetime: 轉換後的 UTC+8 時間，或在輸入為 `None` 時回傳現在時間。
    """
    if utc_dt is None:
        return get_now()
    
    # 由於 Reflex Var 包裝的 datetime 可能沒有 tzinfo 屬性，
    # 我們假設傳入的 utc_dt 代表 UTC 時間，但可能是 naive 的。
    # 我們從其基本屬性重建一個 aware datetime 物件。
    try:
        # 這些屬性標準 datetime 物件都有
        aware_utc_dt = datetime(
            year=utc_dt.year,
            month=utc_dt.month,
            day=utc_dt.day,
            hour=utc_dt.hour,
            minute=utc_dt.minute,
            second=utc_dt.second,
            microsecond=utc_dt.microsecond,
            tzinfo=timezone.utc  # 強制賦予 UTC 時區
        )
    except AttributeError:
        # 如果連 year, month 等基本屬性都沒有，那問題更嚴重
        # 這通常不應該發生，如果傳入的確實是 datetime 物件
        raise ValueError(AttributeError.__traceback__)
        
    taipei_dt = aware_utc_dt.astimezone(taipei_timezone)
    return taipei_dt