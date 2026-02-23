from datetime import timedelta, timezone, datetime

expire = datetime.now(timezone.utc) + timedelta(seconds=5)

print(expire)