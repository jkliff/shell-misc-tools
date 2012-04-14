#!/usr/bin/env python

"""simple bulk image resizer (I use this a lot when trying to send someone pictures that are in too high resolution).

TODO: prompt user to select which images to convert.
TODO: allow not to delete all images after convertion in case of --zip
TODO: send per email the zip
TODO: allow definition of max size of zip to break up in little ones automatically
TODO: possibly run convert jobs in parallel (check how many cores there are)
TODO: avoid stopping the whole execution (currently only the current convert process is stopped if C-c is pressed)
"""

from argparse import ArgumentParser
import os
import os.path
import urwid
import re
import sys
import tempfile
import zipfile

# it is as pain in the ass to install this.
#import PythonMagick

# some files are annoying, like these:
IGNORE_FILES = ['.DS_Store']

def _w (t):
    sys.stdout.write ("\r%s" % t)
    sys.stdout.flush ()

def parse_options():
    parser = ArgumentParser (description = 'bulk image size converter')
    parser.add_argument ('path', default = '.', help = 'path to where the images are located')
    parser.add_argument ('target', help = 'path to where the converted files will be saved.')
    parser.add_argument ('--zip', required = False, default=False, action='store_true', help = 'if present, the converted images will be packged in a zip file. If present, TARGET will specify the zip file')

    return parser.parse_args ()

def prompt_user_for_imgs (path):
    """TODO: really prompt the user"""
    print 'Selecting images from %s' % path
    return [os.path.join (path, f) for f in os.listdir (path) if f not in IGNORE_FILES]

def convert_images (l, target_dir):
    new_files = []
    c = 0
    #print 'Using %s as destdir.' % target_dir
    for i in l:
        c += 1
        _w ("Converting %s/%s" % (c, len (l)))
        f = convert (i, target_dir)
        new_files.append (f)

    sys.stdout.write ("\n")
    print 'Done converting.'

    return new_files

def convert (img, dest_dir):
    new_name = os.path.join (dest_dir, re.sub (r'(.*)\.([a-zA-Z]+)', r'\1-reduced.\2', os.path.split (img)[1]))
    # be decent and use python magick api. if only PythonMagick's folks had decent docs and packaging...
    cmd = 'convert -scale 1024x768 "%s" "%s"' % (img, new_name)
    #print 'will execute: %s' % cmd
    os.system (cmd)
    return new_name

def package_images (target_file, files):
    print 'Packaging to %s...' % target_file

    z = zipfile.ZipFile (target_file, 'w')
    for i in files:
        z.write (i, os.path.split (i)[1])

    z.close ()
    print 'Done packaging'

def main ():
    args = parse_options ()
    path = os.path.abspath (os.path.expanduser (args.path))

    if not os.path.exists (path) or not os.path.isdir (path):
        print 'path %s does not exists or is not a directory' % path
        exit (-1)

    if not args.target.endswith ('.zip'):
        args.target += '.zip'

    if os.path.exists (args.target):
        print 'Specified target %s file already exists. Aborting.' % args.target
        exit (-2)

    imgs_to_convert = prompt_user_for_imgs (path)
    if len (imgs_to_convert) == 0:
        print 'No images selected for convertion. Exiting'
        return

    dest_dir = args.target
    if args.zip:
        dest_dir = tempfile.mkdtemp ()
    else:
        os.mkdir (dest_dir)

    generated_files = convert_images (imgs_to_convert, dest_dir)

    if args.zip:
        package_images (args.target, generated_files, dest_dir)

if __name__ == '__main__': 
    main()
