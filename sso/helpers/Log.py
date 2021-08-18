import logging
import traceback


class Log:
    @staticmethod
    def log(o: any, title: str = "") -> None:
        # Sends input logs to the "django" logger (settings).
        log = logging.getLogger("django")
        if title:
            log.debug(title)
        log.debug(o)



    @staticmethod
    def logException(e: Exception) -> None:
        # Logs the stack trace information and the raw output if any.
        Log.log(traceback.format_exc(), 'Error')

        try:
            Log.log(e.raw, 'Raw sso data')
        except Exception:
            pass

    @staticmethod
    def actionLog(o: any, user: dict = {}) -> None:
        # Sends input logs to the "f5" logger (settings).
        log = logging.getLogger("django")
        try:
            if "username" in user:
                log.debug("[" + user['username'] + "] " + o)
            else:
                log.debug(o)
        except Exception:
            pass
