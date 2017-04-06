from tempfile import TemporaryFile
from subprocess import check_output, CalledProcessError

import logging


def get_out(args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t, shell=True)
            print out
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            print "ERROR: " + str(args) + str(e.returncode) + ',' + t.read()
            # raise RuntimeError
            return False, t.read()


def write_to_file(path, content):
    with open(path, 'w') as fp:
        fp.write(content)


def get_in(args, input_data):
    with TemporaryFile() as t:
        try:
            t.write(input_data)
            out = check_output(args, stdin=t, shell=False)
            # print "SUCCESS: " + str(args) + ",0 ," + str(out)
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            print "ERROR: " + str(args) + str(e.returncode) + ',' + t.read()
            # raise RuntimeError

            return False, t.read()


def get_logger(name, loglevel):
    # LOGGING
    if loglevel == 'INFO':
        log_level = logging.INFO
    elif loglevel == 'DEBUG':
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # add handler
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if len(logger.handlers) == 0:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
