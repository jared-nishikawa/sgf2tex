#!/usr/bin/python

import process

if __name__ == '__main__':
    with open('sgf/Younggil.sgf') as f:
        raw = f.read()

    clean = process.filter_comments(raw)
    with open('argh.sgf','w') as f:
        f.write(clean)
