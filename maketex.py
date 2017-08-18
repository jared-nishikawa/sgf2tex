#!/usr/bin/python

import argparse
import process
import boardlib
import re

def _title(PW="White", PB="Black", WR="", BR="", \
        KM="0", RE="", DT="", SZ="", PC="", RU="", \
        TM="", OT="",\
        **kwargs):
    s = """\
\\begin{titlepage}
    \\null
    \\vfill
    \\begin{center}
        \\textbf{%s (%s) vs %s (%s)}\\\\
        \\textbf{Board size: %s}\\\\
        \\textbf{Server: %s}\\\\
        \\textbf{Ruleset: %s}\\\\
        \\textbf{Main time: %s}\\\\
        \\textbf{Overtime: %s}\\\\
        \\textbf{Komi: %s}\\\\
        \\textbf{Result: %s}\\\\
        \\textbf{Date: %s}
    \\end{center}
    \\vfill
\\end{titlepage}
\\newpage
\\tableofcontents
""" % (PW, WR, PB, BR, SZ, PC, RU, TM, OT, KM, RE, DT)

    return s

def title(keys):
    return _title(**keys)

def write_fork(fork, f):
    total = len(fork.main)

    # If it's the main fork, then start the section differently 
    header = ''
    footer = ''
    if fork.trunk:
        header = '\\newpage\n'
        header += '\\begin{section}{Game: Move %d}\n' % (total)
        footer = '\\end{section}\n'
    else:
        header = '\\begin{subsection}{Fork: Move %d}\n' % (total)
        footer = '\\end{subsection}\n'

    # Each fork has a length
    # make a new diagram for each variation 
    # [:-length+1], ... [:]
    # where, for each one, the stones that are numbered are the
    # last 
    # 1, 2, 3, ..., length stones

    # These are the coordinates of all the moves in the fork
    #main = [S.loc for S in fork.main]
    #total = len(main)

    # These are the coordinates of any handicap stones
    handi = [S.loc for S in fork.handi]

    # This is the length of the fork since the previous fork
    length = fork.length

    # This is the front "half" of the moves
    front = len(fork.main) - length

    # This dictionary is useful for quickly turning a letter into a color
    tmp_D = {"B": "black", "W": "white"}

    # This is the color of the first move since the previous fork
    # (this is for starting the numbering
    col = tmp_D[fork.main[front].col]

    headered = False

    # Make a diagram for every step along the way
    for i in range(1, length+1):

        # These are the moves to be displayed
        main = [S.loc for S in fork.main[:front + i]]

        # These are the moves to be numbered (will be exactly i stones)
        last = fork.main[front:front+i]

        # These are the comments (of the last stone)
        cmts = last[-1].cmt

        # If no comments, then don't make a diagram
        if not cmts:
            continue

        if not headered:
            f.write(header)
            headered = True
    
        # These are converted coordinates of the main moves, and handicap stones
        main_nums = [boardlib.sgf2num(mv) for mv in main]
        handi_nums = [boardlib.sgf2num(mv) for mv in handi]

        # These are the filtered stones (to account for captured stones)
        cblack,cwhite = boardlib.clean(main_nums, handi=handi_nums)
        black = [boardlib.num2sgf(mv) for mv in cblack]
        white = [boardlib.num2sgf(mv) for mv in cwhite]

        f.write('\\begin{center}\n')
        f.write('\\cleargoban\n')

        # handicap stones
        if handi:
            f.write('\\black{')
            f.write(','.join(handi))
            f.write('}\n')

        f.write('\\black{')
        f.write(','.join(black))
        f.write('}\n')

        f.write('\\white{')
        f.write(','.join(white))
        f.write('}\n')
    
        # last few stones
        f.write('\\' + col + '[' + str(front + 1) + ']{')
        f.write(','.join([S.loc for S in last]))
        f.write('}\n')

        # labels (this should go in another function)
        cur = last[-1]
        for key in cur.ext.keys():
            if key == 'TR':
                for loc in cur.ext[key]:
                    #print loc
                    #raw_input()
                    coord = process.convert(loc)
                    if coord in black:
                        f.write('\\black[\\igotriangle]{' + coord + '}\n')
                    elif coord in white:
                        f.write('\\white[\\igotriangle]{' + coord + '}\n')
                    else:
                        f.write('\\gobansymbol{' + coord + \
                                '}{\\igotriangle}\n')
    
            elif key == 'SQ':
                for loc in cur.ext[key]:
                    #print loc
                    #raw_input()
                    coord = process.convert(loc)
                    if coord in black:
                        f.write('\\black[\\igosquare]{' + coord + '}\n')
                    elif coord in white:
                        f.write('\\white[\\igosquare]{' + coord + '}\n')
                    else:
                        f.write('\\gobansymbol{' + coord + \
                                '}{\\igosquare}\n')
            elif key == 'LB':
                for string in cur.ext[key]:
                    #raw_input()
                    loc = string.split(':')[0]
                    let = string.split(':')[1]
                    coord = process.convert(loc)
                    if coord in black:
                        pass
                        #f.write('\\black[' + let + ']{' + coord + '}\n')
                    elif coord in white:
                        pass
                        #f.write('\\white[' + let + ']{' + coord + '}\n')
                    else:
                        f.write('\\gobansymbol{' + coord + \
                                '}{' + let + '}\n')
            elif key == 'OB':
                pass



        f.write('\\showfullgoban\n')
    
        f.write('\\\\')
    
        # Comments
        #f.write('\parbox{4.5in}{\n')

        f.write('\\begin{lstlisting}\n')
        f.write(cmts)
        f.write('\\end{lstlisting}\n')

        #f.write('}\n')
    
        f.write('\\end{center}\n')

    if headered:
        f.write(footer)

def make(infile, outfile):
    with open(infile) as f:
        raw = f.read()
        # forks is a list of Moves()
        forks = process.forks(raw)
        #for fork in forks:
        #    print [S.loc for S in fork.main]
        #    raw_input()
        keys = process.get_keys(raw)

    with open(outfile,'w') as f:
        # optional:
        # f.write('\\documentclass[twocolumn]{article}\n')
        f.write('\\documentclass{article}\n')
        f.write('\\usepackage{igo}\n')
        f.write('\\usepackage{listings}\n')
        f.write('\\lstset{\n')
        f.write('    basicstyle=\\small\\ttfamily,\n')
        f.write('    columns=flexible,\n')
        f.write('    breaklines=true\n')
        f.write('}\n')
        f.write('\\begin{document}\n')
    
        f.write(title(keys))
        for fork in forks:
            write_fork(fork, f)

        f.write('\\end{document}\n')

   
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--infile', '-i', required=True)
    ap.add_argument('out')

    args = ap.parse_args()
    
    make(args.infile, args.out)
