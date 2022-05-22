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
        \\textbf{1 Dan Problems}\\\\
    \\end{center}
    \\vfill
\\end{titlepage}
\\newpage
"""
    return s

def title(keys):
    return _title(**keys)

def parse(row):
    pattern = "\(;AW((\[[^\]]*\])*)AB((\[[^\]]*\])*)C\[([^\]]*)\]\)"
    m = re.match(pattern, row)
    ws = m.groups()[0].lstrip('[').rstrip(']').split('][')
    bs = m.groups()[2].lstrip('[').rstrip(']').split('][')
    comment = m.groups()[4]
    return ws, bs, comment

def write_row(row, f, i):
    whandi, bhandi, comment = parse(row)
    wtex = [process.convert(s) for s in whandi]
    btex = [process.convert(s) for s in bhandi]

    header = '\\begin{subsection}{Problem %d}\n' % (i)
    footer = '\\end{subsection}\n'

    # This dictionary is useful for quickly turning a letter into a color
    tmp_D = {"B": "black", "W": "white"}

    headered = False

    if not headered:
        f.write(header)
        headered = True

    f.write('\\begin{center}\n')
    f.write('\\cleargoban\n')

    if wtex:
        f.write('\\white{')
        f.write(','.join(wtex))
        f.write('}\n')

    if btex:
        f.write('\\black{')
        f.write(','.join(btex))
        f.write('}\n')

    f.write('\\showfullgoban\n')

    f.write('\\\\')

    # Comments
    #f.write('\parbox{4.5in}{\n')

    f.write('\\begin{lstlisting}\n')
    f.write(comment)
    f.write('\\end{lstlisting}\n')

    #f.write('}\n')

    f.write('\\end{center}\n')

    if headered:
        f.write(footer)

def make(infile, outfile):
    with open(infile) as f:
        raw = f.read()
        rows = []
        for line in raw.split('\n'):
            if line.startswith("(;A"):
                rows.append(line)
        keys = process.get_keys(raw)

    with open(outfile,'w') as f:
        # optional:
        f.write('\\documentclass[twocolumn]{article}\n')
        #f.write('\\documentclass{article}\n')

        # removes section numbering
        f.write('\\setcounter{secnumdepth}{0}\n')
        f.write('\\setlength\\parskip{\\baselineskip}\n')
        f.write('\\usepackage{igo}\n')
        f.write('\\usepackage{listings}\n')
        f.write('\\lstset{\n')
        f.write('    basicstyle=\\small\\ttfamily,\n')
        f.write('    columns=flexible,\n')
        f.write('    breaklines=true\n')
        f.write('}\n')
        f.write('\\begin{document}\n')
    
        f.write(title(keys))
        i = 1
        for row in rows:
            write_row(row, f, i)
            i += 1

        f.write('\\end{document}\n')

   
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--infile', '-i', required=True)
    ap.add_argument('out')

    args = ap.parse_args()
    
    make(args.infile, args.out)
