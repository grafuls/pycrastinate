import re
from modules.send_email import send_email
import concurrent.futures as cf
from modules.process_results import process_results


def find_recipient_and_send(config, data, depth=0):
    """Assumes that all levels are nested dicts until a list of dicts.
    Asumes e-mails to send are the keys of some of these nodes"""

    def send_email_or_go_deeper(key_val):
        key, val = key_val
        if re.match(config["email_re"], key):
            body = config["render_function"](config, val)
            config["to"] = config.get("to", []) + [key.lower()]
            return send_email({"send_email": config}, body)
        else:
            return find_recipient_and_send(config, val, depth+1)

    if isinstance(data, list):
        return
    MAX_THREADS = config.get("MAX_THREADS", 4)
    with cf.ThreadPoolExecutor(max_workers=MAX_THREADS) as e:
        process_results({}, e.map(send_email_or_go_deeper, data.items()))


def send_aggregated_email_threadpool(config, data):
    """Assumes data can be iterated multiple times"""
    config = config.get(__name__.split(".")[-1], {})
    config["email_re"] = re.compile(u"[^ ]+@[^ ].[^ ]", re.IGNORECASE)
    find_recipient_and_send(config, data)
    return data
