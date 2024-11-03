import logging

from supabase import create_client, Client


class LoggerService:
    def __init__(self, is_firebase_needed=True, url_supabase: str = None, api_key: str = None):
        self.__is_supabase_needed = is_firebase_needed
        if is_firebase_needed:
            try:
                self.db: Client = create_client(url_supabase, api_key)
                self.actions_db = self.db.table('iht_bot_actions_23_24')
                self.service_db = self.db.table('iht_bot_service_23_24')

            except:
                self.log_service("PROBLEM", "Problem with connection to Supabase")

            self.log_service("OK", "ну ")

    def log_service(self, status: str, message: str):
        logging.info(f"Service message -> {message}. STATUS = {status}")
        if self.__is_supabase_needed:
            try:
                self.service_db.insert(
                    {"status": status,
                     "text": message}
                ).execute()
            except:
                logging.error("(!!!) Problem with connection to Supabase")

    def log(self, tg_id: str, name: str,
            dt: str, status: str, message: str):
        logging.info(f"({tg_id} {name} {dt}) -> {message}. STATUS = {status}")

        if self.__is_supabase_needed:
            try:
                self.actions_db.insert(
                    {"type": "work_tg_info",
                     "user_tg_id": tg_id,
                     "user_name": name,
                     "dt": dt,
                     "status": status,
                     "message": message}
                ).execute()
            except:
                logging.error("(!!!) Problem with connection to Supabase")
