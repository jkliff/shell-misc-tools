#!env python

import os
import re
import sys

"""
Command line utility for searching files in a Eclipse-like glob manner.
Mimics workings of find (recursive find up to depth; selection by file type) but selects files as a open dialog in Eclipse.

TODO:
- allow specification of max depth of recursion
- allow determination of -type f or d
- allow specification of case insensitiveness
- allow specification of inclusion/exclusion of hidden files/directories
- allow specificaiton of non ^ at beginning of regexp

"""


def noop(*s):
    pass
perr = lambda s: sys.stderr.write("%s\n" % s)
perr = noop

productions = [
    (r'(^|[^\.])\*', '\g<1>.*'),
    (r'([A-Z][a-z0-9]+)', '\g<1>.*'),
    (r'([A-Z])(?=(?:[A-Z]|$))', '\g<1>[a-z0-9]*'),
    # from here, no asterisks are added
    (r'(:?^\\)\.', '\.'),
]
# cleanup duplicates
cleanup = [
    (r'(\.\*)+', '.*')
]


def usage():
    print 'ccfg [OPTIONS] [PATTERN] [PATHS]'


def is_upper(i):
    return i >= 'A' and i <= 'Z'


def exec_rules(productions, r):
    for p in productions:
        perr('%s %s' % (p[0], p[1]))
        r = re.sub(p[0], p[1], r)
        perr('>>%s' % r)
    return r


def convert_to_regexp(s):
    """
    >>> convert_to_regexp('')
    '^.+$'
    >>> convert_to_regexp('a*')
    '^a.*$'
    >>> convert_to_regexp('*')
    '^.*$'
    >>> convert_to_regexp('.*')
    '^.*$'
    >>> convert_to_regexp('A')
    '^A[a-z0-9]*.*$'
    >>> convert_to_regexp('AB')
    '^A[a-z0-9]*B[a-z0-9]*.*$'
    >>> convert_to_regexp('Ab')
    '^Ab.*$'
    >>> convert_to_regexp('aA')
    '^aA[a-z0-9]*.*$'
    >>> convert_to_regexp('a')
    '^a.*$'
    >>> convert_to_regexp('*asdf')
    '^.*asdf.*$'
    >>> convert_to_regexp('*IT')
    '^.*I[a-z0-9]*T[a-z0-9].*$'
    >>> convert_to_regexp('??_*lala.sql')
    '^??_.*lala\.sql.*$'
    >>> convert_to_regexp('*asdf$')
    '^.*asdf$'
    >>> convert_to_regexp('.*asdf$')
    '^.*asdf$'
    >>> convert_to_regexp('\.*asdf')
    '^\.*asdf.*$'
    >>> convert_to_regexp('SLS')
    '^S[a-z0-9]*L[a-z0-9]*[a-z0-9]*S[a-z0-9]*.*$'
    >>> convert_to_regexp('SoLoSe')
    '^So.*Lo.*Se.*$'
    """

    if type(s) != str:
        raise TypeError

    if len(s) == 0:
        return '^.+$'

    r = s
    perr('==== %s' % r)
    r = exec_rules(productions, r)

    perr('before wrapping up: %s' % r)
    if s[-1] != '$':
        r += '.*$'

    return '^' + exec_rules(cleanup, r)


def find(base_path=os.path.expanduser('.'), depth=0, max_depth=None):
    perr('%s %s %s ' % (base_path, depth, max_depth))
    r = []
    f = os.listdir(base_path)
    for i in f:
        fi = os.path.join(base_path, i)
        r.append(fi)
        #perr (os.path.isdir (fi), fi)
        if (max_depth is None or depth < max_depth) and os.path.isdir(fi):
            r.extend(find(fi, depth=depth + 1, max_depth=max_depth))
            continue

    return r


def main(args):
    # FIXME: use argparse
    if len(args) != 3:
        usage()
        return 1

    sr = convert_to_regexp(args[2])
    perr('produced regexp %s' % sr)
    rexp = re.compile(sr)
    # use a generator over a glob?
    for f in find(args[1]):
        perr('try to match agains %s' % os.path.basename(f))
        if rexp.match(os.path.basename(f)):
            print f

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
