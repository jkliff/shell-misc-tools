# -*- coding: utf-8 -*-
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
tt sum 201201github jkliff

Dependencies:
easy_install termcolor

Bugs: 
- handle unicode properly:
$ python timetracker/tt.py rec "lavando louça"
timetracker/tt.py:135: UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
  if _last_record ().desc == p:
Including record at 2012-04-14 20:39:48
Updating store... done.


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

    def __init__ (self, serial = None, desc = None):
        if serial:
            self.__dict__ = json.loads (serial)
        else:
            self.time = datetime.now().strftime (DATE_FORMAT)
            self.desc = desc

    def toJson (self):
        return json.dumps (self.__dict__)

def _last_record ():
    r = None
    with (open (_f(), 'r')) as f:
        l = list (f)
        if len (l) > 0:
            r = l[-1]
    return Record (serial = r)

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

def __gen_full_log_filename (d=DATA_DIR):
    """Gets the full path to the datastore"""
    return os.path.join (d, 'log')

def __write_datastore (r):
    """Updates the datastore"""
    print 'Updating store...',
    with (open (_f(), 'a')) as f:
        f.write (r.toJson ())
        f.write ("\n")
    print 'done.'

def __time_delta (b, e):
    if type (datetime.now()) != type (e):
        e = datetime.strptime (e, DATE_FORMAT)

    return e - datetime.strptime (b, DATE_FORMAT)

# convenience shortcuts
_td = lambda b, e: __time_delta (b, e)
_ctd = lambda b: (lambda e: _td(b, e))(datetime.now())
_w = __write_datastore
_i = __prompt_user_input
_f = __gen_full_log_filename

# commands
def current (p):
    x =_last_record ()
    if x.desc == COMMENT_CHAR:
        print 'No current activity'
        return

    print c('Current activity:', attrs=['underline'])
    print "%s\nStarted at %s (%s)" % (x.desc, c(x.time, 'green'), _ctd (x.time))

def new_record (p):
    if not p:
        p = _i ('New record data:', TEMPLATE ['new_record'])
    # if last record is exaclty the same as the new, there's not really the need to create a new one.
    if _last_record ().desc == unicode (p, 'utf-8'):
        return
    r = Record (desc = p)
    print 'Including record at %s' % c(r.time, 'green')
    _w (r)

def stop (p, stop_delimiter=COMMENT_CHAR):
    # if last entry is already a STOP we don't have to do anything.
    if _last_record ().desc != stop_delimiter:
        _w (Record (desc = stop_delimiter))

def list_period (p):
    with (open (_f())) as f:
        l = map (lambda x: Record (serial = x), list(f)[-int((0,p)[p is not None]):])

    for i in range (len (l or [])):
        r = l[i]
        n_time = (lambda x, b: (datetime.now(), l[min (x-1, i+1)].time)[b])(len(l), (i+1) < len (l))

        print "%s (%s)\n%s%s" % (c(r.time, 'white', attrs=['underline']), _td (r.time, n_time), 20*' ', r.desc)

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
