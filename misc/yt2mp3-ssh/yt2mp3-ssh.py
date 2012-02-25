#!/usr/bin/python
import sys
import os
import os.path
import subprocess as sub
import re

"""ssh_cred : The connection string to the remote server. as in foo@bar.net.
Expected to be found in a file named ~/.yt2mp3-ssh.conf
"""
ssh_cred = None
with (open (os.path.expanduser ('~/.yt2mp3-ssh.conf'))) as f:
    ssh_cred = f.read().strip()

"""We expect a sole parameter being the video_id (the value of paramter v in the request)."""

video = sys.argv[1]

cmd = """ssh %s "~/youtube-dl --extract-audio -t \\"http://www.youtube.com/watch?v=%s\\"" """ % (ssh_cred, video)
print cmd
p = sub.Popen (cmd, shell=True,stdout=sub.PIPE).stdout

download_file = None
audio_file = None

while 1:
    line = p.readline()
    if not line:
        break
    else:
        if re.match ('^\[.+\] Destination: .+$', line):
            r = re.search ('^\[(.+)\] Destination: (.+)$', line)
            action = r.group (1)
            file_name = r.group (2)
            if action == 'download':
                download_file = file_name
            elif action == 'ffmpeg':
                audio_file = file_name
    print line,

cmd = """scp %s:~/%s .""" % (ssh_cred, audio_file)
print cmd
os.system (cmd)

cmd = """ssh %s rm "~/%s" """ % (ssh_cred, audio_file)
print cmd
os.system (cmd)
