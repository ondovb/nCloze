from sys import argv
import json
import xmltodict
import numpy as np
from scipy.stats.stats import pearsonr
import pandas as pd

# args: results.json stripped.json data1.json data2.json ...

answers = {}
options = {}
ans2idx = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4}
context = {}
blk_tok = '<BLANK>'
ctx = 64

cnd2art = {
	'cloth':'article',
	'cdgp-m':'article-cdgp-m',
	't5multi-m':'article-cdgp-m',
	'ncloze-m':'article-cdgp-m',
	'ncloze':'article-ncloze'
	}

f_all = open('compiled.json')
j_all = json.load(f_all)

dfs = {}

for psg in j_all:
	j = j_all[psg]
	for ttype in cnd2art.keys():
		key = ('' if ttype == 'cloth' else '-'+ttype)
		anss = j['answers' + key]
		opts = j['options' + key]
		if ttype != 'cloth':
			dfkey = qkey = '%s-%s'%(psg, ttype)
			dfs[dfkey] = pd.DataFrame()#columns=[str(x) for x in range(len(anss))])
		for i, ans in enumerate(anss):
			qkey = '%s-%s-%d'%(psg, ttype, i)
			answers[qkey] = ans
			options[qkey] = opts[i]
		if ttype != 'cloth':
			art = j[cnd2art[ttype]]
			for i in range(len(anss)):
				filled = art
				for k in range(len(anss)):
					if k != i:
						#print(opts[i])
						#print(ans2idx[anss[i]])
						filled = filled.replace('_', opts[i][ans2idx[anss[i]]], 1)
					else:
						filled = filled.replace('_', blk_tok, 1)
				fidx = filled.index(blk_tok)
				s = min(max(fidx-int(ctx/2), 0), len(filled)-ctx-len(blk_tok))
				context['%s-%s-%d'%(psg, ttype, i)] = '...' + ' '.join(filled[s:s+ctx+len(blk_tok)].split()[1:-1]) + '...'

print(dfs)
f = open(argv[1])
j = json.load(f)
f.close()
#print(answers)
results = []
nFail = 0
o = open(argv[1] + '.tsv', 'w')
import matplotlib.pyplot as plt
cnd2acc = {}
cnd2alpha = {}

for asn in j:
	wid = asn['WorkerId']
	#print(wid)
	counts = {}
	counts_even = {}
	counts_odd = {}
	correct = {}
	correct_even = {}
	correct_odd = {}
	failed = 0
	msg = ''
	graded = {}
	for k, v in json.loads(xmltodict.parse(asn['Answer'])['QuestionFormAnswers']['Answer']['FreeText'])[0].items():
		ttype = '-'.join(k.split('-')[1:-1])
		if 'cloth' in k:
			grp = 'ctl'
		else:
			dfkey = '-'.join(k.split('-')[:-1])
			grp = 'exp'
			cond = ttype
		pid = k.split('-')[0]
		n = int(k.split('-')[-1])
		print(wid, k, v, answers[k], n)
		if n != 9:
			if n%2:
				counts_odd[grp] = counts_odd.get(grp, 0) + 1
			else:
				counts_even[grp] = counts_even.get(grp, 0) + 1
			counts[grp] = counts.get(grp, 0) + 1
		
		if grp == 'exp':
			graded[str(n)]=int(v == answers[k])
		if v == answers[k]:
			if n != 9:
				if n%2:
					correct_odd[grp] = correct_odd.get(grp, 0) + 1
				else:
					correct_even[grp] = correct_even.get(grp, 0) + 1
				correct[grp] = correct.get(grp, 0) + 1
		elif ('cloth' not in k) and (n == 9):
			msg += 'For the passage "%s", you chose %s for the blank instead of %s. ' % (context[k], options[k][ans2idx[v]].upper(), options[k][ans2idx[answers[k]]].upper())
			#print("FAILED:\t%s\t%d\t%s\t%s"%(wid, n, v, answers[k]))
			failed += 1
	#print(graded)
	#print(dfkey)
	#print(dfs[dfkey])
	#print(dfs[dfkey])
	result = {}
	result['asn_id'] = asn['AssignmentId']
	result['wid'] = wid
	acc_ctl = correct.get('ctl', 0) / counts['ctl']
	acc_ctl_even = correct_even.get('ctl', 0) / counts_even['ctl']
	acc_ctl_odd = correct_odd.get('ctl', 0) / counts_odd['ctl']
	acc_exp = correct.get('exp', 0) / counts['exp']
	acc_exp_even = correct_even.get('exp', 0) / counts_even['exp']
	acc_exp_odd = correct_odd.get('exp', 0) / counts_odd['exp']
	if cnd2acc.get(cond, None) == None:
		cnd2acc[cond] = []
	if cnd2alpha.get(cond, None) == None:
		cnd2alpha[cond] = []
	if failed > 0 and acc_ctl < 0.25:
		nFail += 1
		result['msg'] = msg + 'You also scored less than chance level on a teacher-created gradeschool-level reading comprehension test. As state in the description, This task requires full attention and fluency in English and we cannot accept your results. If you believe this is an error, please contact the requester through Mechanical Turk.'
		#print(asn['AcceptTime'])
		#print(asn['SubmitTime'])
	else:
		if failed < 1 and acc_ctl >= 0.25:
			cnd2acc[cond].append((acc_ctl, acc_exp))
			cnd2alpha[cond].append((acc_exp_even, acc_exp_odd))
			dfs[dfkey] = dfs[dfkey].append(graded, ignore_index=True)
		result['msg'] = ''
	result['fail'] = failed
	if failed == 0:
		o.write('\t'.join([
			cond,
#			result['asn_id'],
			str(acc_ctl),
			str(acc_exp),
			str(acc_ctl_even),
			str(acc_ctl_odd),
			str(acc_exp_even),
			str(acc_exp_odd)
		])+'\n')
	results.append(result)

print(dfs)

import pingouin as pg

alphas = {}
counts = {}
for cond in cnd2art.keys():
	if cond != 'cloth':
		alphas[cond] = 0
		counts[cond] = 0

for key, df in dfs.items():
	cond = '-'.join(key.split('-')[1:])
	print(key, cond)
	print(df)
	if df.shape[0] > 2:
		result = pg.cronbach_alpha(data=df)
		print(result)
		alphas[cond] += result[0]
		counts[cond] += 1

for cond, alpha in alphas.items():
	print(cond, alpha / counts[cond])
#quit()


for k, v in cnd2acc.items():
	print(k, len(v), pearsonr([x[0] for x in v], [x[1] for x in v]))#[0][1])
	#print(v)
#	print(k)
#	print([x[0] for x in v])
#	print([x[1] for x in v])
#	plt.scatter([x[0] for x in v], [x[1] for x in v], alpha=0.5)
#	plt.show()

for k, v in cnd2alpha.items():
	print(k, len(v), pearsonr([x[0] for x in v], [x[1] for x in v]))#[0][1])
	#print(v)
#	print(k)
#	print([x[0] for x in v])
#	print([x[1] for x in v])
#	plt.scatter([x[0] for x in v], [x[1] for x in v], alpha=0.5)
#	plt.show()

o = open('results-parsed.json', 'w')
o.write(json.dumps(results))

print(nFail)
