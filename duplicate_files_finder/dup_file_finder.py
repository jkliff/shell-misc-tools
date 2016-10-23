import sqlite3
import click
import os
import hashlib
import sys
import itertools

@click.group()
def app():
    pass


def init_db(conn):
    print('creating db')
    conn.execute('''
create table hashes (
    path            text unique,
    name            text,
    size_b          int,
    c_date          text,
    md5_1k          text,
    md5_10k         text,
    offset          int,
    md5_offset_1k   text,
    md5_offset_10k  text,
    sha1_offset_10k text,
    last_check      datetime
);
''')

    conn.commit()

class FileInfo(object):
    def __init__(self):
        self.path = None
        self.name = None
        self.size = None
        self.offset = None
        self.md5_1k = None
        self.md5_10k = None
        self.md5_offset_10k = None
        self.sha1_offset_10k = None


def store(cur, info):
    cur.execute('''insert into hashes
(path, name, size_b, md5_1k, md5_10k, offset, md5_offset_10k, sha1_offset_10k, last_check)
values
(?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
        (info.path, info.name, info.size, info.md5_1k, info.md5_10k, info.offset, info.md5_offset_10k, info.sha1_offset_10k))


def process(src):
    chunk_size = 20 *1024
    one_mb = 1024 * 1024
    offset = one_mb - chunk_size

    with(open(src, 'rb')) as f:
        b_1k = f.read(1024)
        f.seek(0)
        b_10k = f.read(10240)

        h_1k = hashlib.md5(b_1k)
        h_10k = hashlib.md5(b_10k)
        info = FileInfo()
        info.path = src
        info.name = os.path.basename(src)
        info.size = os.stat(src).st_size
        info.md5_1k = h_1k.hexdigest()
        info.md5_10k = h_10k.hexdigest()

        if info.size >= one_mb:
            f.seek(offset)
            ob_10k = f.read(chunk_size)
            info.offset = offset
            info.md5_offset_10k = hashlib.md5(ob_10k).hexdigest()
            info.sha1_offset_10k = hashlib.sha1(ob_10k).hexdigest()

    return info

total_expected_files = 0
checked_files = 0

def scan_recursive(path, ignore_dirs=['.git']):
    global total_expected_files
    for r, ds, fs in os.walk(path, topdown=True):
        total_expected_files += len(fs)
        ds[:] = [d for d in ds if d not in ignore_dirs]
        #if os.path.basename(r) in ignore_dirs:
        #    continue
        #print('root' + r)
        #print(os.path.basename(r))
        #print(ds)
        for f in fs:
            yield os.path.abspath(os.path.join(r, f))


def open_db(db, init_if_missing=False):
    conn = sqlite3.connect(db, isolation_level=None)
    tables = conn.execute('''select name from sqlite_master where type = 'table' ''').fetchall()
    tables = list(map(lambda x: x[0], tables))
    if init_if_missing and 'hashes' not in tables:
        init_db(conn)
    return conn

def update_counter(t, c):
    print('\rProcessed %s/%s' % (c, t), end='\r')
    sys.stdout.flush()

@app.command('scan')
@click.argument('path')
def scan_files(path, db_file='dups.db'):
    global checked_files
    assert os.path.exists(path)
    assert os.path.isdir(path)
    conn = open_db(db_file, init_if_missing=True)
    cur = conn.cursor()
    print('Starting ...')
    for f in scan_recursive(path):
        info = process(f)
        store(cur, info)
        checked_files += 1
        update_counter(total_expected_files, checked_files)
    cur.close()
    print('Finished')
    conn.close()

@app.command('find')
def find_duplicate(db_file='dups.db', strategy=None):
    conn = open_db(db_file)


    cur = conn.cursor()
    dup_md5 = cur.execute('''
select md5_offset_10k, count(1)
from hashes
where md5_offset_10k is not null
group by md5_offset_10k
having count(1) > 1
order by count(1) desc
''').fetchall()

    dup_md5 = [x[0] for x in dup_md5]
    for m in dup_md5:
        dup_sha1 = cur.execute('''
select sha1_offset_10k
from hashes
where md5_offset_10k = ?
group by sha1_offset_10k
having count(1) > 1
''', (m, )).fetchall()
        dup_sha1 = [x[0] for x in dup_sha1]


        ids = list(itertools.product([m], dup_sha1))
        print(ids)
        for i in ids:
            files = cur.execute('select path from hashes where md5_offset_10k = ? and sha1_offset_10k = ? order by path', (i[0], i[1])).fetchall()
            if len(files) < 1:
                continue
            print('Probable duplicate group found:')
            for f in [x[0] for x in files]:
                print('\t' + f)

    conn.close()


if __name__ == '__main__':
    app()
