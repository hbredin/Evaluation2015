"""
MediaEval Person Discovery Task evaluation.

Usage:
  evaluation [options] <reference.shot> <reference.ref> <hypothesis.label> <hypothesis.evidence>

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  --levenshtein=<threshold>  Levenshtein ratio threshold [default: 1.00]
"""

from docopt import docopt
import pandas as pd
from Levenshtein import ratio
import numpy as np


def loadFiles(shot, reference, label, evidence):

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
        print evidenceShots - shotShots
        print shotShots - evidenceShots
        msg = ('Evidences should only be chosen among provided shots.')
        raise ValueError(msg)

    # reference submission format:
    # personName videoID shotNumber source
    names = ['videoID', 'shotNumber', 'personName', 'isEvidence', 'source']
    reference = pd.read_table(reference, sep=' ', names=names)

    return shot, reference, label, evidence


def closeEnough(personName, query, threshold):
    return ratio(query, personName) >= threshold


def computeAveragePrecision(vReturned, vRelevant):

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
    label = arguments['<hypothesis.label>']
    evidence = arguments['<hypothesis.evidence>']
    threshold = float(arguments['--levenshtein'])

    shot, reference, label, evidence = loadFiles(shot, reference,
                                                 label, evidence)

    # =========================================================================
    # Evaluation of LABELS
    # =========================================================================

    # build list of queries from reference
    queries = sorted(set(reference['personName'].unique()))

    # helper object for subsequent filtering by distance to query
    personNames = label['personName']

    # query --> averagePrecision dictionary
    averagePrecision = {}

    for query in queries:

        # get relevant shots for this query, according to reference
        qRelevant = reference[reference['personName'] == query]
        qRelevant = qRelevant[['videoID', 'shotNumber']]
        qRelevant = set((videoID, shotNumber)
                        for _, videoID, shotNumber in qRelevant.itertuples())

        # get returned shots for this query
        # (i.e. shots containing close enough labels)
        qReturned = label[personNames.apply(closeEnough,
                                            args=(query, threshold))]

        # corner case when no label are close enough to the query
        if qReturned.empty:
            qReturned = []

        # general case when at least one label matches the query
        else:

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

    # average over all queries
    meanAveragePrecision = np.mean([averagePrecision[query] for query in queries])

    # =========================================================================
    # Evaluation of EVIDENCES
    # =========================================================================

    accuracy = {}

    for _, personName, videoID, shotNumber, source in evidence.itertuples():

        # list of person names for which
        # reference says this shot is evidence
        isEvidenceFor = list(reference[(
            (reference.videoID == videoID) *
            (reference.shotNumber == shotNumber) *
            (reference.isEvidence))]['personName'])

        if isEvidenceFor:
            accuracy[personName] = max(ratio(personName, name) for name in isEvidenceFor)
        else:
            accuracy[personName] = 0

    meanAccuracy = np.mean([accuracy[personName] for personName in accuracy])

    print 'Labels    = {label:5.2f} %'.format(label=100 * meanAveragePrecision)
    print 'Evidences = {evidence:5.2f} %'.format(evidence=100 * meanAccuracy)
