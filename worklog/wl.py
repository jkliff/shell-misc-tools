#!env python

import datetime
import os
from plumbum import local, FG
from plumbum.cmd import git
import sys
import yaml

perr = lambda x: sys.stderr.write("%s\n" % x)

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

    conf_dir = os.path.dirname(CONF_PATH)
    with local.cwd(conf_dir):
        if os.path.dirname(git['rev-parse', '--git-dir'](retcode=None)) != conf_dir:
            perr('CONF_DIR %s is not a git repo.' % conf_dir)

        if '-y' not in args:
            perr('Aborting.')
            return 3

        print('Initializing git repo on %s' % conf_dir)
        git['init']()
        git['add', CONF_PATH]()

    print '''Remote sync support depends on definition of a remote named 'origin'.
If you need this feature, define a remote repo on your H7R_WORKLOG_PATH.'''

    conf = _f('w')
    yaml.dump(ctx, conf)
    print 'Created empty config file.'

    return 0

#def __publish(args):
#    pass

def __sync(args):
    conf_dir = os.path.dirname(CONF_PATH)

    with local.cwd(conf_dir):
        git['commit', '-a', '-m', 'worklog at %s' % local['hostname']().strip()](retcode=(0,1))
        if etn(git['remote']()) is None:
            perr('No remote repo. Aborting.')
            return 0

        git['pull']()
        git['push', '-u', 'origin', 'master']()

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
        with local.cwd(os.path.dirname(log_path)):
            git['add', log_path]()

    editor = local[os.environ['EDITOR']]
    editor[log_path] & FG

    save_conf(ctx)

    return 0

CMDS = {
    'init': __init,
#    'pub': __publish,
    'sync': __sync,
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

    global CONF_PATH
    CONF_PATH = os.path.join(os.environ['H7R_WORKLOG_PATH'], 'wl.conf')

    cmd, args = parse_args(argv)

    if cmd not in CMDS.keys():
        perr('Uknown command: %s' % cmd)
        return 2

    return CMDS[cmd](args)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
