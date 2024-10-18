from datetime import datetime
import inspect


class Logger:
    __date_structure = "%d-%m-%Y %H:%M:%s"
    def log(self, message: str):
        print(f"[{datetime.now().strftime(self.__date_structure)}] {inspect.stack()[1].function} -> {message}")
