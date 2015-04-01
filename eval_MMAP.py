"""
Eval MMAP

Usage:
  eval_MMAP.py <hyp_file> <ref_file> <queries_list> <size_rank>
  eval_MMAP.py -h | --help
"""

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    hyp_file = arguments['<hyp_file>']
    ref_file = arguments['<ref_file>']
    queries_list = arguments['<queries_list>']
    size_rank = int(arguments['<size_rank>'])

    ref = {}
    hyp = {}
    queries = {}
    for line in open(queries_list):
        video, name = line[:-1].split(' ')
        queries.setdefault(name, set([])).add(video)
        ref.setdefault(name, {})
        ref[name][video] = set([])
        hyp.setdefault(name, {})
        hyp[name][video] = set([])

    for line in open(hyp_file):
        video, name, shot, confidence = line[:-1].split(' ')
        if name in hyp:
            if video in hyp[name]:
                hyp[name][video].add([confidence, shot])

    for line in open(ref_file):
        video, name, shot = line[:-1]
        if name in ref:
            if video in ref[name]:
                ref[name][video].add(shot)

    MMAP = 0.0
    for name in queries:
        MAP = 0.0
        for video in queries[name]:
            AP = 0.0
            rank = 0.0
            nb_cor = 0.0
            for conf, shot in sorted(hyp[name][video], reverse=True)[size_rank:]:
                rank += 1
                if shot in dic_ref[name][video]:
                    nb_cor+=1.0
                    AP += nb_cor/rank
            AP/=nb_cor 
            MAP += AP
        MAP /= len(queries[name])
        print 'MAP for:', name, MAP
        MMAP += MAP
    MMAP /= len(queries)
    print 'total MMAP:', MMAP
