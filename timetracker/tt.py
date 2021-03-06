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
import re
import termcolor
import shutil
import sys

c=termcolor.colored

# TODO: improve this to resolve the editor dinamically ($EDITOR, or what is configured)
EDITOR = 'vim'

COMMENT_CHAR = '#'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT_BACKUP_SUFFIX = '%Y%m%d%H%M%S'
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
            # we have to correct encoding as we read
            self.desc = self.desc.encode ('utf-8')
        else:
            self.time = datetime.now().strftime (DATE_FORMAT)
            self.desc = desc
            self.set_work_log (work_log)

    def toJson (self):
        return json.dumps (self.__dict__)

    def set_work_log (self, m):
        if m:
            self.work_log = base64.b64encode (m.strip())
        else:
            self.work_log = None

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
        f.write (tmpl.encode ('utf-8'))
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

    _b()

    print 'Updating store...',
    with (open (_f(), 'a')) as f:
        f.write (r.toJson ())
        f.write ("\n")
    print 'done.'

def __time_delta (b, e):
    now = datetime.now()

    if type (now) != type (e):
        e = datetime.strptime (e, DATE_FORMAT)
    if type (now) != type (b):
        b = datetime.strptime (b, DATE_FORMAT)

    return e - b

def __update_current (r):

    _b()

    print 'Updating store...',
    l = []
    with (open (_f())) as f:
        l = f.readlines () [: -1]

    with (open (_f(), 'w')) as f:
        l.append (r.toJson())
        f.writelines (l)
        f.write ("\n")

    print 'done.'

def __filter_TODAY (r):
    return datetime.strptime (r.time, DATE_FORMAT).date() == datetime.today().date()

LIST_FILTERS = {
    'TODAY': __filter_TODAY
}

def __build_record_list (p, q = None, ignore_stops=True):
    """ p = listing paremeter, if any
        q = quantity of records to fetch. if not specified, takes all"""

    if p not in ['TODAY']:
        q = p
        lf = lambda x: True
    else:
        lf = LIST_FILTERS [p]

    with (open (_f())) as f:
        l = [Record (serial = x) for x in list(f)]

    return filter (lf, [x for x in l if not ignore_stops or x.desc != COMMENT_CHAR][-int((0,q)[q is not None]):]) or []

__interval_from = lambda l, i: (lambda x, b: (datetime.now(), l[min (x-1, i+1)].time)[b])(len(l), (i+1) < len (l))

def __check_and_do_store_backup (force=False):
    """makes a backup of the datastore. if not forced, will create a backup everytime the last backup is older than one day."""

    if sys.platform == 'linux2':
        """we don't do this check right now since it does not work under linux.
        TODO: fix this!"""
        return

    will_do_backup = False
    f = _f()
    if not force:
        will_do_backup = _td (datetime.fromtimestamp (os.stat(f).st_birthtime), datetime.now()) > timedelta (days=1)
    else:
        will_do_backup = True

    if not will_do_backup:
        return

    print 'Doing safety backup...',
    backup_name = f + '-%s.backup' % datetime.now().strftime (DATE_FORMAT_BACKUP_SUFFIX)
    os.rename (f, backup_name)
    shutil.copyfile (backup_name, f)
    print 'done.'

# convenience shortcuts
_td = lambda b, e: __time_delta (b, e)
_ctd = lambda b: (lambda e: _td(b, e))(datetime.now())
_w = __write_datastore
_i = __prompt_user_input
_f = __gen_full_log_filename
_u = __update_current
_b = __check_and_do_store_backup

# commands
def current (p):
    x = _last_record ()
    if x is None:
        print 'No current activity'
        return

    print c('Current activity:', attrs=['underline']), c (x.desc, 'red')
    print "Started at %s (%s)" % (c(x.time, 'green'), _ctd (x.time))
    print x.get_work_log() or ''
    print '.'

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

def edit_current (p):
    """edit current task"""

    r = _last_record ()
    if r is None:
        print c ('Rejected:', 'red'), 'No current record'
        return

    msg = u"""%s Editing record %s
%s Lines starting with %s will be ignored
%s Record description:
%s
%s Record time:
%s
%s Work log:
%s""" % (COMMENT_CHAR, r.desc,
        COMMENT_CHAR, COMMENT_CHAR,
        COMMENT_CHAR,
        r.desc,
        COMMENT_CHAR,
        r.time,
        COMMENT_CHAR,
        unicode(r.get_work_log (), 'utf-8'))

    t = _i (None, msg).split ("\n")

    (d, ts) = (t[0], t[1])
    wl = "\n".join (t[2:])

    r = Record (desc = d, work_log = wl)
    r.time = ts

    _u (r)

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
        work_log_lines = r.get_work_log().split ("\n")
        work_log_lines = ['    %s' % x for x in work_log_lines]

        wll = "\n".join (work_log_lines)

        print c(r.time, 'white', attrs=['underline']), c(r.desc, 'red'), _td (r.time, n_time)
        print wll

def summarize_period (p):
    l =__build_record_list (p)

    s = {}
    total_records = 0

    for i in range (len (l)):
        r = l[i]
        if r.desc == COMMENT_CHAR:
            continue

        n_time = __interval_from (l, i)
        if r.desc not in s:
            s [r.desc] = 0

        duration = _td (r.time, n_time).total_seconds ()
        s [r.desc] += duration

        total_records += duration

    print c('Activity summary for %s' % c(datetime.strftime (datetime.today(), DAY_FORMAT), 'green'), attrs = ['underline'])
    print 'Total time registered: %s' % c(str (timedelta (seconds = total_records)))
    for k in sorted (s, lambda x,y: cmp (x, y)):
        print " - %s\t:\t%s" % (k, timedelta (seconds=s[k]))

def rebuild_records (p):
    """Rewrites the datastore. Useful when records are manipulated or to upgrade a version."""

    _b(True)

    print 'Rewriting store...',

    records = __build_record_list (None, ignore_stops = False)
    with (open (_f(), 'w')) as f:
        f.writelines (["%s\n" % x.toJson() for x in sorted (records, key=lambda r: r.time)])

    print 'done.'

CMDS = {
    'curr':     current,
    'rec':      new_record,
    'edit':     edit_current,
    'stop':     stop,
    'last':     list_period,
    'sum':      summarize_period,
    'rebase':   rebuild_records
}

def parse_args ():

    parser = ArgumentParser (description = 'Timetracker')
    parser.add_argument ('command', type=str, nargs=1, help='Action to be executed: %s' % ', '.join (sorted(CMDS.keys())), default='list')
    parser.add_argument ('param', type=str, nargs='?', help='parameters')
    a = parser.parse_args ()

    cmd = a.command [0]
    if cmd not in CMDS:
        print 'Command %s not recognized.' % cmd
        parser.print_help ()
        return (None, None)

    p = None
    if a.param:
        p = a.param

    return (cmd, p)

def main ():
    __check_datadir ()

    cmd, params = parse_args ()
    if cmd:
        CMDS [cmd] (params)

if __name__ == '__main__':
    main()
