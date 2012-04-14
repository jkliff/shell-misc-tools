"""
CLI timetracker

Sample usage:

tt curr

tt rec "foo-1234"
tt rec "bar-666"

tt stop

tt list TODAY
tt list 20120215
tt sum 2012
tt sum 201201
"""
import os.path
from argparse import ArgumentParser
from datetime import datetime
import tempfile
import json

import termcolor
c=termcolor.colored

# TODO: improve this to resolve the editor dinamically ($EDITOR, or what is configured)
EDITOR = 'vim'

COMMENT_CHAR = '#'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

TEMPLATE = {'new_record': """%s Enter event description below. Lines starting with %s are ignored.
""" % (COMMENT_CHAR, COMMENT_CHAR)}

DATA_DIR = os.path.expanduser ('~/.timetracker/')
def __check_datadir (d=DATA_DIR):
    if not os.path.exists (d):
        print 'Creating datadir %s' % c(d, 'red', attrs=['bold'])
        os.mkdir (d)
        open(_f(), 'w').close()

class Record:
    time = None
    desc = None

    def __init__ (self, d = None):
        if d:
            self.__dict__ = json.loads (d)

    def toJson (self):
        return json.dumps (self.__dict__)

def _gen_record (t):
    d = datetime.now ()

    r = Record()
    r.time = d.strftime (DATE_FORMAT)
    r.desc = t

    return r

def _last_record ():
    r = None
    with (open (_f(), 'r')) as f:
        l = list (f)
        if len (l) > 0:
            r = l[-1]
    return Record (r)

def __prompt_user_input (s, tmpl):
    """Prompt for user input writing on a temp file, calling an editor on it, and then reading its contents and then returning them. The temp file is deleted afterwards"""

    def comment_lines (t):
        s = ''
        if type (list) != type (t):
            s = '%s %s' % (COMMENT_CHAR, t)
        else :
            s = "\n".join (['%s %s' % (COMMENT_CHAR, i) for i in t])
        return s

    t = tempfile.mktemp ()
    with (open (t, 'w')) as f:
        f.write (tmpl)
        f.write (comment_lines (s))
        f.write ("\n\n")

    cmd = '%s "%s"' % (EDITOR, t)
    os.system (cmd)
    with (open (t)) as f:
        msg = "\n".join ([l for l in f.readlines () if not l.startswith (COMMENT_CHAR)])
    os.remove (t)

    return msg

def __gen_ful_log_filename (d=DATA_DIR):
    """Gets the full path to the datastore"""
    return os.path.join (d, 'log')

def __write_datastore (r):
    """Updates the datastore"""
    print 'Updating store...',
    with (open (_f(), 'a')) as f:
        f.write (r.toJson ())
        f.write ("\n")
    print 'done.'

_w = __write_datastore
_i = __prompt_user_input
_f = __gen_ful_log_filename

def current (p):
    x =_last_record ()
    if x.desc == COMMENT_CHAR:
        print 'No current activity'
        return

    t = x.time
    d = datetime.now() - datetime.strptime (t, DATE_FORMAT)
    print "Current activity:\n%s\nStarted at %s (%s)" % (x.desc, d, x.time, d)

def new_record (p):
    if not p:
        p = _i ('New record data:', TEMPLATE ['new_record'])
    # if last record is exaclty the same as the new, there's not really the need to create a new one.
    if _last_record ().desc == p:
        return
    r = _gen_record (p)
    print 'Including record at %s' % c(r.time, 'green')
    _w (r)

def stop (p, stop_delimiter=COMMENT_CHAR):
    # if last entry is already a STOP we don't have to do anything.
    if _last_record ().desc != stop_delimiter:
        _w (_gen_record (stop_delimiter))

def list_period (p):

    with (open (_f())) as f:
        d = list (f)
        if p:
            d = d [-int(p):]

    print "\n".join (["%s\n%s%s" % (r.time, 20*' ', r.desc) for r in map (lambda x: Record (x), d)])

def summarize_period (p):
    print p

CMDS = {
    'curr': current,
    'rec': new_record,
    'stop': stop,
    'list': list_period,
    'sum': summarize_period
}

def parse_args ():
    parser = ArgumentParser (description = 'Timetracker')
    parser.add_argument ('command', type=str, nargs=1, help='Action to be executed: %s' % ', '.join (sorted(CMDS.keys())), default='list')
    parser.add_argument ('param', type=str, nargs='?', help='parameters')
    a = parser.parse_args ()

    cmd = a.command [0]
    p = None
    if a.param:
        p = a.param

    return (cmd, p)

def main ():

    __check_datadir ()

    cmd, params = parse_args ()
    CMDS [cmd] (params)

if __name__ == '__main__':
    main()
