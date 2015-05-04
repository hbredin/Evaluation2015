"""
MediaEval Person Discovery Task evaluation.

Usage:
  evaluation [options] <reference.shot> <reference.ref> <reference.eviref> <hypothesis.label> <hypothesis.evidence>

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  --queries=<queries.lst>    Query list.
  --levenshtein=<threshold>  Levenshtein ratio threshold [default: 0.95]
"""

from docopt import docopt
import pandas as pd
from Levenshtein import ratio
import numpy as np


def loadFiles(shot, reference, evireference, label, evidence):

    # shot list format:
    # videoID shotNumber startTime endTime startFrame endFrame
    names = ['videoID', 'shotNumber',
             'startTime', 'endTime',
             'startFrame', 'endFrame']
    shot = pd.read_table(shot, sep=' ', names=names, index_col=[0, 1])

    # label submission format:
    # videoID shotNumber personName confidence
    names = ['videoID', 'shotNumber', 'personName', 'confidence']
    label = pd.read_table(label, sep=' ', names=names)

    # check that labels are only provided for selected shots
    shotShots = set(shot.index)
    labelShots = set(tuple(s) for _, s in label[['videoID', 'shotNumber']].iterrows())
    if not labelShots.issubset(shotShots):
        msg = ('Labels should only be computed for provided shots.')
        raise ValueError(msg)

    # evidence submission format:
    # personName videoID shotNumber source
    names = ['personName', 'videoID', 'shotNumber', 'source']
    evidence = pd.read_table(evidence, sep=' ', names=names)

    # check that evidence is provided for every unique label
    labelNames = set(label['personName'].unique())
    evidenceNames = set(evidence['personName'].unique())
    if labelNames != evidenceNames:
        msg = ('There must be exactly one evidence '
               'per unique name in label submission.')
        raise ValueError(msg)

    # check that evidences are chosen among selected shots
    evidenceShots = set(tuple(s) for _, s in evidence[['videoID', 'shotNumber']].iterrows())
    if not evidenceShots.issubset(shotShots):
        msg = ('Evidences should only be chosen among provided shots.')
        raise ValueError(msg)

    # reference format
    names = ['videoID', 'shotNumber', 'personName']
    reference = pd.read_table(reference, sep=' ', names=names)

    # evireference format
    # personName videoID shotNumber source
    names = ['videoID', 'shotNumber', 'personName', 'source']
    evireference = pd.read_table(evireference, sep=' ', names=names)

    return shot, reference, evireference, label, evidence


def closeEnough(personName, query, threshold):
    return ratio(query, personName) >= threshold


def computeAveragePrecision(vReturned, vRelevant, n=100):

    nReturned = len(vReturned)
    nRelevant = len(vRelevant)

    if nRelevant == 0 and nReturned == 0:
        return 1.

    if nRelevant == 0 and nReturned > 0:
        return 0.

    if nReturned == 0 and nRelevant > 0:
        return 0.

    returnedIsRelevant = np.array([item in vRelevant for item in vReturned])
    precision = np.cumsum(returnedIsRelevant) / (1. + np.arange(nReturned))
    return np.sum(precision * returnedIsRelevant) / min(nReturned, nRelevant)


if __name__ == '__main__':

    arguments = docopt(__doc__, version='0.1')

    shot = arguments['<reference.shot>']
    reference = arguments['<reference.ref>']
    evireference = arguments['<reference.eviref>']
    label = arguments['<hypothesis.label>']
    evidence = arguments['<hypothesis.evidence>']
    threshold = float(arguments['--levenshtein'])

    shot, reference, evireference, label, evidence = loadFiles(
        shot, reference, evireference, label, evidence)

    if arguments['--queries']:
        with open(arguments['--queries'], 'r') as f:
            queries = [line.strip() for line in f]

    else:
        # build list of queries from reference
        queries = sorted(set(reference['personName'].unique()))

    # query --> averagePrecision dictionary
    averagePrecision = {}
    correctness = {}

    for query in queries:

        # find most similar personName
        ratios = [(personName, ratio(query, personName))
                  for personName in evidence.personName.unique()]
        best = sorted(ratios, key=lambda x: x[1], reverse=True)[0]

        personName = best[0] if best[1] > threshold else None

        if personName is None:
            averagePrecision[query] = 0.
            correctness[query] = 0.
            continue

        # =====================================================================
        # Evaluation of LABELS
        # =====================================================================

        # get relevant shots for this query, according to reference
        qRelevant = reference[reference.personName == query]
        qRelevant = qRelevant[['videoID', 'shotNumber']]
        qRelevant = set((videoID, shotNumber)
                        for _, videoID, shotNumber in qRelevant.itertuples())

        # get returned shots for this query
        # (i.e. shots containing closest personName)
        qReturned = label[label.personName == personName]

        # sort shots by decreasing confidence
        # (in case of shots returned twice for this query, keep maximum)
        qReturned = (qReturned.groupby(['videoID', 'shotNumber'])
                              .aggregate(np.max)
                              .sort(['confidence'], ascending=False))

        # get list of returned shots in decreasing confidence
        qReturned = list(qReturned.index)

        # compute average precision for this query
        averagePrecision[query] = computeAveragePrecision(qReturned,
                                                          qRelevant)

        # =====================================================================
        # Evaluation of EVIDENCES
        # =====================================================================

        # get evidence shots for this query, according to reference
        qRelevant = evireference[evireference.personName == query]
        qRelevant = qRelevant[['videoID', 'shotNumber', 'source']]

        _qRelevant = set([])
        for _, videoID, shotNumber, source in qRelevant.itertuples():

            if source == 'both':
                _qRelevant.add((videoID, shotNumber, 'audio'))
                _qRelevant.add((videoID, shotNumber, 'image'))
            else:
                _qRelevant.add((videoID, shotNumber, source))

        qRelevant = _qRelevant

        qReturned = evidence[evidence.personName == personName][['videoID', 'shotNumber', 'source']]
        for _, videoID, shotNumber, source in qReturned.itertuples():
            break

        if (videoID, shotNumber, source) in qRelevant:
            correctness[query] = best[1] if best[1] > threshold else 0.
        else:
            correctness[query] = 0.
            print query, personName, videoID, shotNumber, source

    MAP = np.mean([averagePrecision[query] for query in queries])
    mCorrectness = np.mean([correctness[query] for query in queries])
    EwMAP = np.mean([correctness[query] * averagePrecision[query] for query in queries])

    print 'EwMAP = %.2f %%' % (100 * EwMAP)
    print 'MAP = %.2f %%' % (100 * MAP)
    print 'C = %.2f %%' % (100 * mCorrectness)
