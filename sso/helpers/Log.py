import logging
import traceback


class Log:
    @staticmethod
    def log(o: any, title: str = "") -> None:
        log = logging.getLogger("django")
        if title:
            log.debug(title)
        log.debug(o)



    @staticmethod
    def logException(e: Exception) -> None:
        Log.log(traceback.format_exc(), 'Error')

        try:
            Log.log(e.raw, 'Raw sso data')
        except Exception:
            pass



    @staticmethod
    def actionLog(o: any, user: dict = {}) -> None:
        log = logging.getLogger("django")
        try:
            if "username" in user:
                log.debug("[" + user['username'] + "] " + o)
            else:
                log.debug(o)
        except Exception:
            pass
