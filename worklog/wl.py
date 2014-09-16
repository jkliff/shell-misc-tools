#!env python

import os
import sys
from plumbum import local, FG

perr = lambda x: sys.stderr.write("%s\n" % x)

def __publish (args):
    pass

def __save (args):
    pass

def __edit (args):
    if 'EDITOR' not in os.environ:
        perr ('$EDITOR undefined')
        return 3

    if 'H7R_WORKLOG_PATH' not in os.environ:
        perr ('$H7R_WORKLOG_PATH undefined')
        return 3


    log_path = os.path.join (os.environ['H7R_WORKLOG_PATH'], 'foo')
    if not os.path.exists (log_path):
        local['touch'][log_path]()

    editor = local[os.environ['EDITOR']]
    editor[log_path] & FG

    return 0

CMDS = {
    'pub': __publish,
    'save': __save,
    'edit': __edit
}

def parse_args (args):

    #from argparse import ArgumentParser
    #parser = ArgumentParser (prog=args[0])

    v = args [1:]
    cmd = 'edit'

    if len (v) > 0 and not v[0].startswith ('--'):
        if len (v) > 1 and v[1] == '--':
            v = [v[0]] + v[2:]
        cmd = v[0]
        v = v[1:]

    #parser.add_argument('command', default='edit', nargs='?')

    #return cmd, parser.parse_args (v)
    return cmd, v

def main (argv):

    cmd, args = parse_args (argv)
    print cmd, args
    if cmd not in CMDS.keys():
        perr ('Uknown command: %s' % cmd)
        return 2

    return CMDS[cmd](args)

if __name__ == '__main__':
    sys.exit (main(sys.argv))
