from datetime import datetime
import os
from cogs.utils import IO
import traceback


class Logger:
    @staticmethod
    def time_now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def check_for_folder():
        """Check for logs folder and create it if it doesn't exist"""
        logs_f = "logs"

        if os.path.isdir(logs_f):
            return True
        else:
            os.makedirs(logs_f)
            if os.path.isdir(logs_f):
                return True
            return False

    @staticmethod
    def get_filename():
        data = IO.read_settings_as_json()
        if data is None:
            return None

        r_time = data['info']['last-login-time']
        time = str(r_time).split(".")[0].replace(":", "-")

        file_name = "Log {}.txt".format(time)

        if not os.path.exists(os.path.join("logs", file_name)):
            with open(os.path.join("logs", file_name), "w") as f:
                f.write("")  # Log Started\n")

        return file_name

    @staticmethod
    def write_and_print(to_write):
        print(to_write)
        if Logger.write(to_write) is True:
            return True
        else:
            return False

    @staticmethod
    def log_write(data):
        try:
            with open(os.path.join(os.path.join("logs", Logger.get_filename())), "a") as lf:
                lf.write(data)
                lf.write("\n")
                return True
        except Exception as e:
            print("Error writing to log file. Reason: {}".format(type(e).__name__))
            return False

    @staticmethod
    def write(to_write):
        if Logger.check_for_folder() is False:
            return False

        file = Logger.get_filename()
        if file is None:
            return "Failed to write error log, File is None"

        if isinstance(to_write, str):
            if Logger.log_write("{} - {}".format(Logger.time_now(), to_write)) is True:
                return True
            else:
                return False

        elif isinstance(to_write, Exception):
            print("An exception has occurred. Check the logs for more info")

            ex_type = type(to_write).__name__
            args = to_write.args
            err_line = to_write.__traceback__.tb_lineno
            err_file = to_write.__traceback__.tb_frame.f_code.co_filename

            fmt_tb = traceback.format_exc()
            tb_split = fmt_tb.split("\n")
            err_code = tb_split[2].strip()

            err_msg = "----------------------------------------------------------\n" \
                      "An Exception Occurred at {}\n" \
                      "Type: {}\n" \
                      "Args: {}\n" \
                      "File: {}\n" \
                      "Line: {}\n" \
                      "Code: {}\n" \
                      "----------------------------------------------------------" \
                      "".format(Logger.time_now(), ex_type, args, err_file, err_line, err_code)

            if Logger.log_write(err_msg) is True:
                return True
            else:
                return False
        else:
            print("Logging for type '{}' currently not handled".format(type(to_write)))
            if Logger.log_write("{} - Tried to write data of type '{}' to log."
                                "".format(Logger.time_now(), type(to_write))) is True:
                return True
            else:
                return False










