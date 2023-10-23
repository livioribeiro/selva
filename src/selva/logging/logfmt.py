def logfmt_format(record):
    message = {
        "time": f"{record['time']}",
        "level": f"{record['level']}",
        "source": f"{record['module']}.{record['name']}:{record['function']}:{record['line']}",
        "message": '"' + record["message"].replace('"', r"\"") + '"',
    }
    message |= record["extra"]

    return " ".join(f"{key}={value}" for key, value in message.items()) + "\n"
