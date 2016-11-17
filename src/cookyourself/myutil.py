import sys
import traceback

class __LINE__(object):
    import sys

    def __repr__(self):
        try:
            raise Exception
        except:
            return str(sys.exc_info()[2].tb_frame.f_back.f_lineno)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def integer(s):
    try:
        res = int(s)
        return res
    except (ValueError, SyntaxError) as e:
        eprint(e)

def to_float(s):
    try:
        res = eval(s)
        return res
    except (ValueError, SyntaxError) as e:
        traceback.print_exc()
