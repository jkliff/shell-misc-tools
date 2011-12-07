#!/bin/bash

FILENAME=$1

cat > $FILENAME <<EOF
#!/usr/bin/python
""" ... """

def main ():
    print "...and that was about it."

if __name__ == '__main__':
    main ()

EOF
