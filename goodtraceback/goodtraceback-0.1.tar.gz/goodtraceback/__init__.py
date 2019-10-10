import sys
import traceback

def __print_exc_plus(exctype, value, trb):
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    if exctype == KeyboardInterrupt:
        sys.__excepthook__(exctype, value, trb)
    else:
        tb = trb

        while True:
            if not tb.tb_next:
                break
            tb = tb.tb_next
        stack = []
        f = tb.tb_frame
        while f:
            stack.append(f)
            f = f.f_back
        stack.reverse()

        traceback.print_exception(exctype, value, trb)
        sys.stderr.write("\nLocals by frame, innermost last\n")

        for frame in stack:
            sys.stderr.write("\nFrame %s in %s at line %s\n" % (frame.f_code.co_name,
                                                 frame.f_code.co_filename,
                                                 frame.f_lineno))
            for key, value in frame.f_locals.items(  ):
                rep = value.__repr__()
                # If the repr string of the object is too long (very long strings, web pages, etc)
                # we print only the first 1024 characters
                if len(rep) > 1024:
                    key = 'len(%d) ' % len(rep) + key
                    rep = rep[:1024]

                sys.stderr.write("\t%20s = " % key)
        
                try:
                    sys.stderr.write(rep + '\n')
                except:
                    sys.stderr.write("<ERROR WHILE PRINTING VALUE>\n")




sys.excepthook = __print_exc_plus
