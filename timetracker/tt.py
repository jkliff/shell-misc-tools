"""
CLI timetracker

Sample usage:

tt curr

tt rec "reboot-1234"
tt rec "reboot-666"

tt stop

tt list TODAY
tt list 20120215
tt sum 2012
tt sum 201201
"""
import os.path
from argparse import ArgumentParser
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

DATA_DIR = os.path.expanduser ('~/.timetracker/')

if not os.path.exists (DATA_DIR):
    print 'Creating datadir', DATA_DIR
    os.mkdir (DATA_DIR)

def _gen_record (t):
    d = datetime.now ()
    return (d.strftime (DATE_FORMAT), t)

def _f ():
    return os.path.join (DATA_DIR, 'log')

def _w (r):
    with (open (_f(), 'a')) as f:
        f.write (','.join (r))
        f.write ("\n")

def current (p):
    r = None
    with (open (_f(), 'r')) as f:
        r = list (f)[-1]

    x = r.strip().split (',')
    t = x [0]
    d = datetime.now() - datetime.strptime (t, DATE_FORMAT)
    print 'Current: %s, since %s (%s)' % (x[1], x[0], d)

def new_record (p):
    r = _gen_record (p)
    _w (r)

def stop (p):
    _w (_gen_record ('--'))

def list_period (p):
    print p

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
    parser.add_argument ('command', type=str, nargs=1, help='Action to be executed', default='list')
    parser.add_argument ('param', type=str, nargs='?', help='parameters')
    a = parser.parse_args ()

    cmd = a.command [0]
    p = None
    if a.param:
        p = a.param

    return (cmd, p)

def main ():
    cmd, params = parse_args ()
    CMDS [cmd] (params)

if __name__ == '__main__':
    main()
