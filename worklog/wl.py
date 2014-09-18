#!env python

import datetime
import os
from plumbum import local, FG
import sys
import yaml

perr = lambda x: sys.stderr.write("%s\n" % x)

CONF_PATH = os.path.join(os.environ['H7R_WORKLOG_PATH'], 'wl.conf')

_f = lambda mode: file(CONF_PATH, mode)
empty_to_none = lambda x: None if x.strip() == '' else x
etn = empty_to_none


def load_conf():
    return yaml.load(_f('r'))

def save_conf(ctx):
    yaml.dump(ctx, _f('w'))

def __init(args):
    ctx = {
        'current_file': '',
    }

    if os.path.exists(CONF_PATH):
        perr('Config file already exists. Aborting.')
        return 2

    conf = _f('w')
    yaml.dump(ctx, conf)
    print 'Created empty config file.'

    return 0

def __publish(args):
    pass

def __save(args):
    pass

def __edit(args):
    if 'EDITOR' not in os.environ:
        perr('$EDITOR undefined')
        return 3

    ctx = load_conf()

    if '-n' in args or etn(ctx['current_file']) is None:
        ctx['current_file'] = 'wl_%s.md' % datetime.date.today().isoformat()

    log_path = os.path.join(os.environ['H7R_WORKLOG_PATH'], ctx['current_file'])
    if not os.path.exists(log_path):
        print 'Creating new worklog file %s' % ctx['current_file']
        with(open(log_path, 'w')) as f:
            f.write('<!--- H7R worklog file %s; on %s --->' %(ctx['current_file'], datetime.date.today().isoformat()))

    editor = local[os.environ['EDITOR']]
    editor[log_path] & FG

    save_conf(ctx)

    return 0

CMDS = {
    'init': __init,
    'pub': __publish,
    'save': __save,
    'edit': __edit
}

def parse_args(args):

    v = args [1:]
    cmd = 'edit'

    if len(v) > 0 and not v[0].startswith('--'):
        if len(v) > 1 and v[1] == '--':
            v = [v[0]] + v[2:]
        cmd = v[0]
        v = v[1:]

    return cmd, v

def main(argv):

    if 'H7R_WORKLOG_PATH' not in os.environ:
        perr('$H7R_WORKLOG_PATH undefined')
        return 3

    cmd, args = parse_args(argv)

    if cmd not in CMDS.keys():
        perr('Uknown command: %s' % cmd)
        return 2

    return CMDS[cmd](args)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
