#!/usr/bin/env python
from argparse import ArgumentParser
import os
import os.path
import urwid
import re
import sys

# it is as pain in the ass to install this.
#import PythonMagick

def _w (t):
    sys.stdout.write ("\r%s" % t)
    sys.stdout.flush ()

def parse_options():
    parser = ArgumentParser (description = 'bulk image size converter')
    parser.add_argument ('--path', default = '.', help = 'path to where the images are located')
    return parser.parse_args ()

def prompt_user_for_imgs (path):
    print 'Selecting images from %s' % path
    return [os.path.join (path, f) for f in os.listdir (path)]

def convert_images (l):
    c = 0
    for i in l:
        c += 1
        _w ("Converting %s/%s" % (c, len (l)))
        convert (i)

def convert (img):
    new_name = re.sub (r'(.*)\.([a-zA-Z]+)', r'\1-reduced.\2', img)
    # be decent and use python magick api. if only PythonMagick's folks had decent docs and packaging...
    cmd = 'convert -scale 1024x768 "%s" "%s"' % (img, new_name)
    #print 'will execute: %s' % cmd
    os.system (cmd)

def main ():
    args = parse_options ()
    path = os.path.abspath (os.path.expanduser (args.path))

    if not os.path.exists (path) or not os.path.isdir (path):
        print 'path %s does not exists or is not a directory' % path
        exit (-1)

    imgs_to_convert = prompt_user_for_imgs (path)
    if len (imgs_to_convert) == 0:
        print 'No images selected for convertion. Exiting'
        return

    convert_images (imgs_to_convert)

if __name__ == '__main__': 
    main()
