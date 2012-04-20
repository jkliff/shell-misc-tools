#!/usr/bin/env python
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
tt sum 201201
tt edit
// tt add_log "foo"

Dependencies:
easy_install termcolor

"""

import os.path
from argparse import ArgumentParser
from datetime import datetime, timedelta
import tempfile
import json
import base64

import termcolor
c=termcolor.colored

# TODO: improve this to resolve the editor dinamically ($EDITOR, or what is configured)
EDITOR = 'vim'

COMMENT_CHAR = '#'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DAY_FORMAT = '%Y-%m-%d'

TEMPLATE_NEW_RECORD = """%s Enter event description below. Lines starting with %s are ignored.
""" % (COMMENT_CHAR, COMMENT_CHAR)

DATA_DIR = os.path.expanduser ('~/.timetracker/')
def __check_datadir (d=DATA_DIR):
    if not os.path.exists (d):
        print 'Creating datadir %s' % c(d, 'red', attrs=['bold'])
        os.mkdir (d)
        open(_f(), 'w').close()

class Record:
    time = None
    desc = None
    work_log = None

    def __init__ (self, serial = None, desc = None, work_log = None):
        if serial:
            self.__dict__ = json.loads (serial)
        else:
            self.time = datetime.now().strftime (DATE_FORMAT)
            self.desc = desc
            self.set_work_log (work_log)

    def toJson (self):
        return json.dumps (self.__dict__)

    def set_work_log (self, m):
        self.work_log = base64.b64encode (m.strip())

    def get_work_log (self):
        if self.work_log is None:
            return None
        return base64.b64decode (self.work_log)

def _last_record ():
    r = None
    with (open (_f(), 'r')) as f:
        l = list (f)
        if len (l) > 0:
            r = l[-1]

    rec = Record (serial = r)
    if rec.desc == COMMENT_CHAR:
        return None

    return rec

def __prompt_user_input (s, tmpl):
    """Prompt for user input writing on a temp file, calling an editor on it, and then reading its contents and then returning them. The temp file is deleted afterwards"""

    def comment_lines (t):
        s = ''
        if t is None:
            return s
        if type (list) != type (t):
            s = '%s %s' % (COMMENT_CHAR, t)
        else :
            s = "\n".join (['%s %s' % (COMMENT_CHAR, i) for i in t])
        return s

    t = tempfile.mktemp ()
    with (open (t, 'w')) as f:
        f.write (tmpl)
        f.write (comment_lines (s))
        f.write ("\n")

    cmd = '%s "%s"' % (EDITOR, t)
    os.system (cmd)
    with (open (t)) as f:
        msg = ''.join ([l for l in f.readlines () if not l.startswith (COMMENT_CHAR)])
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

def __update_current (t):
    r = _last_record ()
    print r.get_work_log ()
    print t
    r.set_work_log (t)
    l = []
    with (open (_f())) as f:
        l = f.readlines () [: -1]

    with (open (_f(), 'w')) as f:
        l.append (r.toJson())
        f.writelines (l)

def __filter_TODAY (r):
    return datetime.strptime (r.time, DATE_FORMAT).date() == datetime.today().date()

LIST_FILTERS = {
    'TODAY': __filter_TODAY
}

def __build_record_list (p, q = None):
    if p not in ['TODAY']:
        q = p
        lf = lambda x: x
    else:
        lf = LIST_FILTERS [p]

    with (open (_f())) as f:
        return filter (lf, map (lambda x: Record (serial = x), list(f)[-int((0,q)[q is not None]):])) or []

__interval_from = lambda l, i: (lambda x, b: (datetime.now(), l[min (x-1, i+1)].time)[b])(len(l), (i+1) < len (l))

def __llpad (t, p):
    if not t:
        return ''
    return "\n".join (['%s%s' % (p*' ', k) for k in t.split ("\n")])

# convenience shortcuts
_td = lambda b, e: __time_delta (b, e)
_ctd = lambda b: (lambda e: _td(b, e))(datetime.now())
_w = __write_datastore
_i = __prompt_user_input
_f = __gen_full_log_filename
_u = __update_current

# commands
def current (p):
    x = _last_record ()
    if x.desc == COMMENT_CHAR:
        print 'No current activity'
        return

    print c('Current activity:', attrs=['underline']), c (x.desc, 'red')
    print x.get_work_log() or ''
    print "Started at %s (%s)" % (c(x.time, 'green'), _ctd (x.time))

def new_record (p):

    if not p or p.strip () == '':
        print c('Rejected:', 'red'), 'No description.'
        return

    # if last record is exaclty the same as the new, there's not really the need to create a new one.
    r = _last_record ()
    if r and _last_record ().desc == unicode (p, 'utf-8'):
        print c('Rejected:', 'red'), 'Same activity as before.'
        return

    t = _i ('New record data:', TEMPLATE_NEW_RECORD )

    r = Record (desc = p, work_log = t)
    print 'Including record at %s' % c(r.time, 'green')
    _w (r)

def add_log (p):
    """include log line to current task"""

def edit_current (p):
    """edit current task"""
    r = _last_record ()
    if r is None:
        print c ('Rejected:', 'red'), 'No current record'

    t = _i (None, """%s Editing record %s (from %s)
%s Lines starting with %s will be ignored
%s"""% (COMMENT_CHAR, r.desc, r.time, COMMENT_CHAR, COMMENT_CHAR, r.get_work_log()))

    _u (t)

def stop (p, stop_delimiter=COMMENT_CHAR):
    # if last entry is already a STOP we don't have to do anything.
    if _last_record ().desc != stop_delimiter:
        _w (Record (desc = stop_delimiter))

def list_period (p, q = None, lf = None):

    l = __build_record_list (p, q)
    for i in range (len (l)):
        r = l[i]
        if r.desc == COMMENT_CHAR:
            continue

        n_time = __interval_from (l, i)

        print "%s %s (%s)\n%s" % (c(r.time, 'white', attrs=['underline']), c(r.desc, 'red'), _td (r.time, n_time), __llpad (r.get_work_log(), 4))

def summarize_period (p):
    l =__build_record_list (p)

    s = {}
    total_records = 0

    for i in range (len (l)):
        r = l[i]
        if r.desc == COMMENT_CHAR:
            continue

        n_time = interval_from (l, i)
        if r.desc not in s:
            s [r.desc] = 0

        duration = _td (r.time, n_time).total_seconds ()
        s [r.desc] += duration

        total_records += duration

    print c('Activity summary for %s' % c(datetime.strftime (datetime.today(), DAY_FORMAT), 'green'), attrs = ['underline'])
    print 'Total time registered: %s' % c(str (timedelta (seconds = total_records)))
    for k in sorted (s, lambda x,y: cmp (x, y)):
        print " - %s\t:\t%s" % (k, timedelta (seconds=s[k]))

CMDS = {
    'curr': current,
    'rec':  new_record,
    'edit': edit_current, 
    'wl':   add_log,
    'stop': stop,
    'last': list_period,
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
