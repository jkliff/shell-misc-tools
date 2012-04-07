#!/usr/bin/env python

"""simple bulk image resizer (I use this a lot when trying to send someone pictures that are in too high resolution).

TODO: prompt user to select which images to convert.
TODO: allow not to delete all images after convertion in case of --zip
TODO: send per email the zip
"""

from argparse import ArgumentParser
import os
import os.path
import urwid
import re
import sys
import zipfile

# it is as pain in the ass to install this.
#import PythonMagick

def _w (t):
    sys.stdout.write ("\r%s" % t)
    sys.stdout.flush ()

def parse_options():
    parser = ArgumentParser (description = 'bulk image size converter')
    parser.add_argument ('path', default = '.', help = 'path to where the images are located')
    parser.add_argument ('--zip', required = False, default = None, help = 'if present, specifies the name of zip file with all the converted images. If present, converted images are deleted afterwards.')
    return parser.parse_args ()

def prompt_user_for_imgs (path):
    """TODO: really prompt the user"""
    print 'Selecting images from %s' % path
    return [os.path.join (path, f) for f in os.listdir (path)]

def convert_images (l):
    new_files = []
    c = 0
    for i in l:
        c += 1
        _w ("Converting %s/%s" % (c, len (l)))
        f = convert (i)
        new_files.append (f)

    sys.stdout.write ("\n")
    print 'Done converting.'

    return new_files

def convert (img):
    new_name = re.sub (r'(.*)\.([a-zA-Z]+)', r'\1-reduced.\2', img)
    # be decent and use python magick api. if only PythonMagick's folks had decent docs and packaging...
    cmd = 'convert -scale 1024x768 "%s" "%s"' % (img, new_name)
    #print 'will execute: %s' % cmd
    os.system (cmd)
    return new_name

def package_images (target_file, files, delete_afterwards = True):
    if not target_file.endswith ('.zip'):
        target_file += '.zip'

    print 'Packaging to %s...' % target_file

    z = zipfile.ZipFile (target_file, 'w')
    for i in files:
        z.write (i)
        if delete_afterwards:
            os.remove(i)

    z.close ()
    print 'Done packaging'

def main ():
    args = parse_options ()
    path = os.path.abspath (os.path.expanduser (args.path))

    if not os.path.exists (path) or not os.path.isdir (path):
        print 'path %s does not exists or is not a directory' % path
        exit (-1)

    if args.zip and os.path.exists (args.zip):
        print 'Specified target zip file already exists. Aborting.'
        exit (-2)

    imgs_to_convert = prompt_user_for_imgs (path)
    if len (imgs_to_convert) == 0:
        print 'No images selected for convertion. Exiting'
        return

    generated_files = convert_images (imgs_to_convert)

    if args.zip is not None:
        package_images (args.zip, generated_files)

if __name__ == '__main__': 
    main()
