import logging

from services.YaContestService import YaContestService
from services.DataService import DataService
from services.TelegramService import TelegramService
from services.LoggerService import LoggerService

secret_bot_key = '7676288154:AAHzVX0_BQQk_-n4R0hiOOJ1QU1leO23ueQ'
secret_yandex_key = 'y0_AgAAAAAW3qH0AAyEuAAAAAESenn_AAC9dsJiYphGR6AcWui1Zg4RPZPSNQ'
secret_supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlicHhmeWdxcnppbnFzamNkZGZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkxOTQyMDIsImV4cCI6MjA0NDc3MDIwMn0.cZrcAl9hBBjT1Yu-N3LdZrFolbH2w7d4fRNdKmt1VwY'
secret_supabase_url = 'https://ybpxfygqrzinqsjcddfs.supabase.co'

file_log = logging.FileHandler("bot_yacontest_logs.log")
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), level=logging.INFO)

##### PARAMS.
is_firebase_needed = True

logger_service = LoggerService(url_supabase=secret_supabase_url,
                               api_key=secret_supabase_key,
                               is_firebase_needed=is_firebase_needed)

database_service = DataService("postgres", "postgres",
                               "postgres", "database", 5432,
                               logger_service)


api_service = YaContestService(secret_yandex_key, logger_service)

telegram_service = TelegramService(secret_bot_key, database_service, api_service, logger_service)
telegram_service.start()
