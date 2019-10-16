import logging.config


from pathlib import Path
import alexber.reqsync.app_conf as conf
from alexber.utils.parsers import is_empty

from collections import deque

_READ_BUFFER_SIZE = 2 ** 16
_WRITE_BUFFER_SIZE = 2 ** 16

def _getSourceGen(filename, more_pck):
    #yield None  # gracefully handled adding package before all existing ones

    buffersize = _READ_BUFFER_SIZE
    with open(filename, 'rt') as f:
        while True:
            lines_buffer = f.readlines(buffersize)
            if not lines_buffer:
                break
            for line in lines_buffer:
                pck = line.rstrip()  # remove '\r'
                if pck:
                    yield pck

    if more_pck is not None:
        yield None  # to nullify prev_line

        for line in deque(more_pck):  # copy-constructor, more_pck is also changed outside, so
            # on first usage, we're creating the copy
            # (duplication is handled correctly by the code)
            pck = line.rstrip()  # remove '\r'
            if pck:
                yield pck






def _process_line(prev_line, cur_line, **kwargs):
    cur_pck, _ = ('', None) if cur_line is None else cur_line.split('==')
    prev_pck, _ = ('', None) if prev_line is None else prev_line.split('==')

    #lowercase them
    low_prev_line = None if prev_line is None else prev_line.casefold()
    low_cur_line = None if cur_line is None else cur_line.casefold()

    if (low_prev_line is not None) and (low_prev_line == low_cur_line) and not is_empty(low_cur_line):
        return None #duplicate line, ignore


    low_prev_pck = prev_pck.casefold()
    low_cur_pck = cur_pck.casefold()

    if (low_prev_line is not None) and (low_prev_pck > low_cur_pck) and not is_empty(low_cur_pck):
        raise ValueError("Source file expected to be sorted. Use sort utilities, for example.")


    if (is_empty(low_prev_pck)) and (low_prev_pck == low_cur_pck) and not is_empty(low_cur_pck):
        raise ValueError(f"Packages in the source file should be unique, but duplicate package {cur_pck} is found.")


    add_pckgs = kwargs.get(conf.ADD_KEY, None)
    rm_pckgs = kwargs.get(conf.RM_KEY, None)
    ret = deque([])
    is_append_curr_line = True

    #remove packages first
    while rm_pckgs is not None and not is_empty(rm_pckgs) and not is_empty(low_cur_pck):
        rm_pck = rm_pckgs[0]
        low_rm_pck = rm_pck.casefold()

        if low_cur_pck < low_rm_pck:
            is_append_curr_line = True
            break
        elif low_cur_pck == low_rm_pck:
            rm_pckgs.popleft()
            is_append_curr_line = False
            break
        else:
            rm_pckgs.popleft()
            continue


    # add packages
    while add_pckgs is not None and not is_empty(add_pckgs):
        add_line = add_pckgs[0]
        add_pck = _extract_pck(add_line)

        low_add_pck = add_pck.casefold()
        if is_empty(low_prev_pck) and (low_prev_pck < low_add_pck <= low_cur_pck): #adding new package at the head of file
            ret.append(add_line)
            is_append_curr_line = True
            add_pckgs.popleft()
        elif low_prev_pck < low_add_pck <= low_cur_pck:
            ret.append(add_line)
            is_append_curr_line = False
            add_pckgs.popleft()
        else:
            break

    if is_append_curr_line and not is_empty(cur_line):
        ret.append(cur_line)

    return ret

def _extract_pck(element):
    if element is None or is_empty(element):
        return ''
    elif '==' not in element:
        pck = element
    else:
        pck, _ = element.split('==')
    return pck


def _validate_mutual_exclusion(add_pckgs, rm_pckgs):
    if is_empty(add_pckgs) or is_empty(rm_pckgs):
        return

    s_add = {_extract_pck(element) for element in add_pckgs}
    for pck in rm_pckgs:
        if pck.casefold() in s_add:
            raise ValueError(f"Mutual_Exclusion enabled, but {pck} was found in both lists")



def _create_deque(pckgs):
    if pckgs is None:
        return None
    pckgs = [pck for pck in pckgs if pck is not None and pck]       #filter out None and ''
    ret_pckgs = None if pckgs is None else deque(sorted(pckgs, key=lambda s: s.casefold()))

    return ret_pckgs

def run(**kwargs):
    """
    This method recieved all conf params in kwargs.
    All unexpected values will be ignored.
    It is expected that value type is correct.
    No conversion on the value of the dict kwargs will be applied.
    This method will built playerA, playerB, engine,
    and run engine with these players.

    Please, consult alexber.rpsgame.app_conf in order to construct kwargs.
    Command-line argument and ini-file are suppored out of the box.
    JSON/YML, etc. can be easiliy handled also.
    """

    #filter out unrelated params
    kwargs = conf.parse_dict(kwargs)

    src_f = kwargs.get(conf.SOURCE_KEY, None)
    if src_f is None:
        raise ValueError(f'{conf.SOURCE_KEY} key should be defined')

    dest_f = kwargs.get(conf.DEST_KEY, None)
    if dest_f is None:
        raise ValueError(f'{conf.DEST_KEY} key should be defined')

    add_pckgs = kwargs.pop(conf.ADD_KEY, None)
    # Limitation: in-memory sorted
    add_pckgs = _create_deque(add_pckgs)

    rm_pckgs = kwargs.pop(conf.RM_KEY, None)
    # Limitation: in-memory sorted
    rm_pckgs = _create_deque(rm_pckgs)

    kwargs[conf.ADD_KEY] = add_pckgs
    kwargs[conf.RM_KEY] = rm_pckgs

    is_mutual_exclusion = kwargs.pop(conf.MUTUAL_EXCLUSION_KEY, True)
    if is_mutual_exclusion:
        _validate_mutual_exclusion(add_pckgs, rm_pckgs)

    full_src_path = Path(src_f).resolve()  # relative to cwd
    full_dest_path = Path(dest_f).resolve()  # relative to cwd
    sourceGen = _getSourceGen(full_src_path, add_pckgs)

    buffersize = _WRITE_BUFFER_SIZE
    lines_buffer = deque(maxlen=buffersize)
    prev_line = None

    with open(full_dest_path, 'wt') as f:
        for cur_line in sourceGen:
            lines = _process_line(prev_line, cur_line,
                                  **kwargs)
            if lines is not None:
                lines_buffer.extend(lines)

            length = len(lines_buffer)
            if length ==  buffersize:
                # writelines ridiculously does not add newlines to the end of each line.
                f.writelines(map(lambda s: s + '\n', lines_buffer))
                lines_buffer.clear()
            prev_line = cur_line
        # writelines ridiculously does not add newlines to the end of each line.
        f.writelines(map(lambda s: s + '\n', lines_buffer))
        lines_buffer.clear()






def main(args=None):
    """
    main method
    :param args: if not None, suppresses sys.args
    """
    dd = conf.parse_config(args)
    run(**dd)


#see https://terryoy.github.io/2016/05/short-ref-python-logging.html
_config = {
        "log_config": {
            "version": 1,
            "formatters": {
                "brief": {
                    "format": "%(message)s",
                },
                "detail": {
                    "format": "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s] %(message)s",
                    "datefmt": '%Y-%m-%d %H:%M:%S',
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "brief",
                },
                # "file": {
                #     "class": "logging.handlers.RotatingFileHandler",
                #     "filename": "dev.log",
                #     "level": "DEBUG",
                #     "formatter": "detail",
                # },
            },
            "root": {
                # "handlers": ["console", "file"],
                "handlers": ["console"],
                "level": "DEBUG",
            },
            "loggers": {
                "requests": {
                    # "handlers": ["file"],
                    "handlers": ["console"],
                    "level": "DEBUG",
                    "propagate": False,
                }
            },
        },
    }

if __name__ == '__main__':
    logging.config.dictConfig(_config["log_config"])
    del _config
    logger = logging.getLogger(__name__)
    main()


