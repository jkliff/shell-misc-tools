"""
CLI timetracker

Sample usage:

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

DATA_DIR = os.path.expanduser ('~/.timetracker/')

if not os.path.exists (DATA_DIR):
    print 'Creating datadir', DATA_DIR
    os.mkdir (DATA_DIR)

def _gen_record (t):
    d = datetime.now ()
    return (str(d), t)

def _w (r):
    l = os.path.join (DATA_DIR, 'log')
    with (open (l, 'a')) as f:
        f.write (','.join (r))
        f.write ("\n")

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
    'rec' : new_record, 
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
