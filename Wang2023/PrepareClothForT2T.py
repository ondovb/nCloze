# +
import os
import json
import csv
from random import random, shuffle

ans2idx = {'A':0, 'B':1, 'C':2, 'D':3}
idx2ans = {0:'A', 1:'B', 2:'C', 3:'D'}


# -

def prepare(d, test=False):
    pairs = []

    for i, a in enumerate(d['answers']):
        t = d['article']
        for j, o in enumerate(d['options']):
            if j == i:
                t = t.replace('_', '<mask>', 1)
            else:
                answer = o[ans2idx[d['answers'][j]]]
                t = t.replace('_', answer, 1)
        ds = d['options'][i]
        ai = ans2idx[a]
        answer = ds[ai]
        ds = ds[:ai]+ds[ai+1:]
        t = t.replace('<mask>', '_')
        
        pairs.append((t+' [SEP] '+answer,' '.join(ds))) # main task
        if test:
            continue
        r = random()
        if r < 0.5:
            # distractor finding
            dr = int(random()*3)
            dd = ds[dr]
            pairs.append((t.replace('_', dd), dd))
        else:
            # cloze test answering
            opts = ds+[answer]
            shuffle(opts)
            pairs.append((t+' [SEP] '+' '.join(opts), answer))
    return pairs


for splt in ['train', 'valid', 'test']:
    data = []
    for levl in ['middle', 'high']:
        print(splt, levl)
        prfx = '../CLOTH/%s/%s/'%(splt,levl)
        for file in os.listdir(prfx):
            f = open(prfx + file)
            d = json.load(f)
            if '(1)' in d['article']:
                print("Skipping %s..."%file)
            else:
                data.extend(prepare(d, splt=='test'))
    o = open('cloth-%s.csv'%splt, 'w')
    w = csv.writer(o)
    w.writerow(['source', 'target'])
    for pair in data:
        w.writerow(pair)
    o.close()


