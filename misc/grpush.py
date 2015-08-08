#!/usr/bin/python3
import plumbum
import click
import subprocess

git = plumbum.local['git']
ssh = plumbum.local['ssh']

@click.command()
@click.argument('host')
@click.argument('proj_name')
def publish_repo(host, proj_name):

#host = 'git@bataille'
#proj_name = 'grunt-ng-seed'
    remote = 'origin'
    bare_name = proj_name + '.git'
    remote_repo = '%s:~/repos/%s' % (host, bare_name)

    ssh[host, 'cd repos && git init --bare %s' % bare_name]()
    git['remote', 'add', remote, remote_repo]()
    git['push', remote, 'master']()

if __name__ == '__main__':
    publish_repo()
