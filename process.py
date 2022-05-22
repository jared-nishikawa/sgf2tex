#!/usr/bin/python

import re
import sys

class Node():
    def __init__(self):
        self.children = []
        self.value = ''
        # Root node is its own parent...
        # This is so I know when to stop when iterating up from a leaf
        self.parent = self
        self.trunk = False

    def push(self, tail):
        # For finding comments
        pattern = "(?<!P)C\[.*?(?<!\\\\)\]"

        # re.DOTALL is set so . will match on newlines
        matches = re.finditer(pattern, tail, flags=re.DOTALL)

        #for cmt in cmts:
        #    print cmt
        #    raw_input()


        intervs = [match.span() for match in matches]

        acc = ''
        assert tail[0] == '('
        i = 1

        # If it's not a ')' or it's a comment, keep going
        while tail[i] != ')' or interval_contain(i, intervs):
            if i == len(tail):
                break

            # This would be the BEGINNING of the next child
            # This was originally an if block, but I've turned
            # it into a while loop in case there are multiple
            # children back to back '(child1)(child2)'
            while tail[i] == '(' and not interval_contain(i,intervs):
                child = Node()
                child.parent = self
                self.children.append(child)
                jump = child.push(tail[i:])
                
                # Increment to the character just past
                # the END of that child
                i += jump

            # If it's a ')' and it's not a comment, stop
            if tail[i] == ')' and not interval_contain(i, intervs):
                break
            else:
                acc += tail[i]
                i += 1
        self.value = acc
        return i + 1
        #return tail[i+1:]

    def disp(self,depth=0):
        M = pull_moves(self.value)
        mvs = M.main

        conv = [convert(S.loc) for S in mvs]
        #print '\t'*depth, mvs
        #print self.value
        #print '  '*depth, conv
        raw_input()
        for child in self.children:
            child.disp(depth=depth+1)

    def get_forks(self):
        # I'd also like to mark the main fork.
        # Goal: find the last leaf, and mark that sequence as main (trunk)
        nds = self.nodes()
        last = self.leaves()[-1]
        cur_main = last
        while cur_main.parent:
            cur_main.trunk = True
            if cur_main == cur_main.parent:
                break
            cur_main = cur_main.parent

        forks = []
        for node in nds:
            seq = []
            cur = node
            while cur.parent:
                seq.append(cur)
                if cur == cur.parent:
                    break
                cur = cur.parent
            seq.reverse()

            #mvs = []
            fork = Moves()
            for each in seq:
                M = pull_moves(each.value)
                fork.length = len(M.main)
                M.convert()

                #print each.value
                #print [s.loc for s in M.main]
                #print "#"*10
                #print
                #raw_input()
               
                #main = M.main
                #conv = [convert(pair) for pair in main]
                fork.main += M.main
                #mvs.append(conv)
                if M.handi:
                    fork.handi = M.handi

            if seq[-1].trunk:
                fork.trunk = True
            #forks.append(flatten(mvs))
            #print [s.loc for s in fork.main]
            #raw_input()
            forks.append(fork)
        return forks

    def leaves(self):
        lvs = []
        stack = [self]
        while stack:
            cur = stack.pop()
            stack += cur.children
            if not cur.children:
                lvs.append(cur)
        return lvs

    def nodes(self):
        nds = []
        stack = [self]
        while stack:
            cur = stack.pop()
            stack += cur.children
            nds.append(cur)
        return nds

class Moves():
    def __init__(self):
        self.main = []
        self.handi = []
        self.trunk = False

    def convert(self):
        newmain = []
        newhandi = []
        for S in self.main:
            T = Stone(convert(S.loc), S.col, cmt=S.cmt, ext=S.ext)
            newmain.append(T)
        for S in self.handi:
            T = Stone(convert(S.loc), S.col, cmt=S.cmt, ext=S.ext)
            newhandi.append(T)
        self.main = newmain
        self.handi = newhandi

class Stone():
    def __init__(self, loc, col, cmt="", ext={}):
        self.loc = loc
        self.col = col
        self.cmt = cmt
        self.ext = ext

def interval_contain(num, intervs):
    for interval in intervs:
        a,b = interval
        if a < num and num < b:
            return True
    return False

def flatten(somelist):
    return [elem for sublist in somelist for elem in sublist]

def pull_moves(raw):
    moves = []
    lines = raw.split(';')
    for line in lines:
        if line.startswith('B[') or line.startswith('W['):
            # regular expression to find two characters following '['
            m = re.search('(?<=\[)[a-s]{2}', line)
            col = line[0]
            if m:
                # Find comments, too
                pattern = "(?<!P)C\[.*?(?<!\\\\)\]"
                comments = re.findall(pattern, line, flags=re.DOTALL)
                #for comment in comments:
                    # Comment starts with C[ and ends with ]
                    #print comment[2:-1]
                assert len(comments) <= 1

                pair = m.group(0)
                S = Stone(pair, col)
                if comments:
                    cmt = comments[0][2:-1]
                    cmt = ']'.join(cmt.split('\\]'))
                    S.cmt = cmt
                lbls = get_labels(line)
                S.ext = lbls
                moves.append(S)
                #moves.append(pair)

    M = Moves()
    handi_string = re.findall('AB[\[\]a-s]*',raw)
    if handi_string:
        handi_raw = re.findall('\[[a-s]*\]', handi_string[0])
        handi_pairs = [mv[1:-1] for mv in handi_raw]
        handi = [Stone(pair, "B") for pair in handi_pairs]
        M.handi = handi

    M.main = moves
    #print [S.cmt for S in M.main]
    #raw_input()

    return M
    #return moves

# Translate coordinates in the form xy (x,y in [a..s])
# to coordinates in the form xn (x in [a..t]/{i}, y in [1..19])
# igo.sty counts up from the BOTTOM
def convert(pair):
    assert len(pair) == 2
    x = pair[0]
    y = pair[1]
    alph1 = 'abcdefghijklmnopqrs'
    alph2 = 'abcdefghjklmnopqrst'
    ind1 = alph1.index(x)
    ind2 = 19 - (alph1.index(y))
    return alph2[ind1] + str(ind2)
    
def read_file(name):
    with open(name) as f:
        return f.read()

def filter_comments(raw):

    pattern = "(?<!P)C\[.*?(?<!\\\\)\]"
    spl = re.split(pattern, raw, flags=re.DOTALL)
    clean = ''.join(spl)
    g = open('dump','w')
    g.write(clean)
    return clean



    hack = raw.split('\\]')
    clean = ''.join(hack)
    while 1:
        new = filter_one_comment(clean)
        if new == clean:
            break
        else:
            clean = new
    return clean
    #print raw

def filter_one_comment(raw):
    i = 0
    while raw[i:i+2] != 'C[':
        i += 1
        if i == len(raw):
            return raw
        if raw[i-1] == 'P':
            i += 1
    j = i
    while raw[j] != ']':
        j += 1
    #print raw
    #print raw[i:j+1]
    return raw[:i] + raw[j+1:]

def forks(raw):
    # optional
    #clean = filter_comments(raw)
    clean = raw

    N = Node()
    N.push(clean)
    #N.disp()
    return N.get_forks()

def get_keys(raw):
    keys = {}
    L_ = re.findall('[A-Z]{1,2}\[[^\]]+\]', raw)
    L = [item for item in L_ if not item.startswith('B[') \
            and not item.startswith('W[') and not item.startswith('BL[')
            and not item.startswith('WL[') and not item.startswith('C[')]

    for item in L:
        i = item.index('[')
        j = item.index(']')
        keys[item[:i]] = item[i+1:j]
    return keys

def get_labels(raw):
    keys = {}
    # Some labels to be on the look out for:
    # TR, SQ, LB, OB
    LB = re.findall('LB[\[\w+:\w+\]]+',raw)
    TR = re.findall('TR[\[\w+\]]+',raw)
    SQ = re.findall('SQ[\[\w+\]]+',raw)

    if LB:
        keys['LB'] = []
        lbs = LB[0]
        coords = re.findall('\[\w+:\w+\]', lbs)
        for coord in coords:
            keys['LB'].append(coord[1:-1])

    if TR:
        keys['TR'] = []
        trs = TR[0]
        coords = re.findall('\[\w+\]', trs)
        for coord in coords:
            keys['TR'].append(coord[1:-1])
    if SQ:
        keys['SQ'] = []
        sqs = SQ[0]
        coords = re.findall('\[\w+\]', sqs)
        for coord in coords:
            keys['SQ'].append(coord[1:-1])

    return keys


if __name__ == '__main__':
    if not sys.argv[1:]:
        sys.exit("Need filename")
    name = sys.argv[1]

    raw = read_file(name)
    F = forks(raw)
    D = get_keys(raw)
    #print D

    #for f in F:
        #print [(stone.loc,stone.col) for stone in f.main]
        #raw_input()
       #print [(stone.loc,stone.col) for stone in f.handi]
