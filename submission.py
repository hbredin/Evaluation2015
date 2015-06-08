#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2015 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


"""
MediaEval Person Discovery Task submission manager.

  - list         Print the list of submissions.
  - delete       Delete submissions (interactive).
  - check        Validate submission files content.
  - primary      Submit primary run.
  - contrastive  Submit contrastive run.

Usage:
  submission [options] list
  submission [options] delete
  submission [options] check <run.label> <run.evidence>
  submission [options] primary <run.label> <run.evidence>
  submission [options] contrastive <run> <run.label> <run.evidence>

Options:
  -h --help                Show this screen.
  --version                Show version.
  --dev                    Development set.
  --debug                  Show debug information.
  --url=URL                Submission server URL
                           [default: http://api.mediaeval.niderb.fr]
  --login=LOGIN            Username.
  --password=P45sw0Rd      Password.


Arguments:
  <run.label>              Path to label submission file.
  <run.evidence>           Path to evidence submission file.
  <run>                    Set name for contrastive run.
"""

from docopt import docopt
from getpass import getpass
from camomile import Camomile
from common import loadLabel, loadEvidence
import pandas as pd
import sys

# pretty pandas display
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# name conventions
CORPUS_NAME_DEV = 'mediaeval.development'
CORPUS_NAME_TEST = 'mediaeval.test'
SUBMISSION_STATUS_WIP = 'incomplete'
SUBMISSION_STATUS_OK = 'complete'
GROUP_ORGANIZER = 'organizer'
USER_ROBOT_SUBMISSION = 'robot_submission'
LAYER_SUBMISSION_SHOT = 'mediaeval.submission_shot'
QUEUE_SUBMISSION = 'mediaeval.submission.in'

DATATYPE_EVIDENCE = "mediaeval.persondiscovery.evidence"
DATATYPE_LABEL = "mediaeval.persondiscovery.label"
FRAGMENTTYPE_SUBMISSION = "mediaeval.persondiscovery._id_shot",

# Camomile client
GLOBAL_CLIENT = None

# submission shots
GLOBAL_DEV_OR_TEST = None
GLOBAL_CORPUS = None
GLOBAL_VIDEO_MAPPING = None
GLOBAL_SHOT_MAPPING = None

# users
GLOBAL_USERS = None
GLOBAL_ME = None
GLOBAL_ROBOT_SUBMISSION = None

# groups
GLOBAL_GROUPS = None
GLOBAL_TEAM = None
GLOBAL_ORGANIZER = None

# queues
GLOBAL_SUBMISSION_QUEUE = None

GLOBAL_DEBUG = False

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------------------------


# error reporting
def reportErrorAndExit(message):
    sys.stderr.write(message)
    sys.stderr.flush()
    sys.exit(-1)


def debug(message):
    sys.stdout.write('DEBUG: ' + message + '\n')
    sys.stdout.flush()


# find user name by its user id
def findUsername(id_user):
    for user in GLOBAL_USERS:
        if user._id == id_user:
            return user.username
    return '?'


def printSubmissions(submissions):
    if submissions.empty:
        return
    columns = ['type', 'name', 'user', 'date', 'status']
    print submissions[columns]


# -----------------------------------------------------------------------------
# INITIALIZATION
# -----------------------------------------------------------------------------

def initialize(url, username=None, password=None):

    if GLOBAL_DEBUG:
        debug('initialize')

    global GLOBAL_CLIENT

    global GLOBAL_CORPUS

    global GLOBAL_USERS
    global GLOBAL_GROUPS

    global GLOBAL_ME
    global GLOBAL_TEAM

    global GLOBAL_SUBMISSION_QUEUE

    # -------------------------------------------------------------------------
    # connect to Camomile server
    # -------------------------------------------------------------------------

    GLOBAL_CLIENT = Camomile(url)
    if username is None:
        username = raw_input('Login: ')
    if password is None:
        password = getpass()
    try:
        GLOBAL_CLIENT.login(username, password)
        GLOBAL_ME = GLOBAL_CLIENT.me()
    except Exception:
        reportErrorAndExit(
            'Unable to connect to %s with login %s' % (url, username))

    # -------------------------------------------------------------------------
    # find corpus identifier (development or test set)
    # -------------------------------------------------------------------------

    try:
        name = (CORPUS_NAME_DEV
                if GLOBAL_DEV_OR_TEST == "dev"
                else CORPUS_NAME_TEST)
        corpora = GLOBAL_CLIENT.getCorpora(name=name)
        GLOBAL_CORPUS = corpora[0]._id
    except Exception:
        reportErrorAndExit(
            'Unable to identify %s corpus.' % GLOBAL_DEV_OR_TEST)

    # -------------------------------------------------------------------------
    # get list of users and groups
    # -------------------------------------------------------------------------

    try:
        GLOBAL_GROUPS = GLOBAL_CLIENT.getGroups()
        GLOBAL_USERS = GLOBAL_CLIENT.getUsers()
    except Exception:
        reportErrorAndExit('Unable to obtain list of users and groups.')

    # -------------------------------------------------------------------------
    # get (supposedly unique) team of current user
    # -------------------------------------------------------------------------

    try:
        GLOBAL_TEAM = None
        userGroups = GLOBAL_CLIENT.getMyGroups()
        for group in GLOBAL_GROUPS:
            if group._id in userGroups and group.name.startswith('team_'):
                GLOBAL_TEAM = group
                break
    except Exception:
        pass

    if GLOBAL_TEAM is None:
        reportErrorAndExit('Unable to identify your team.')

    # -------------------------------------------------------------------------
    # identify submission queue
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('locate submission queue.')

    try:
        queues = [queue._id
                  for queue in GLOBAL_CLIENT.getQueues()
                  if queue.name == QUEUE_SUBMISSION]
        GLOBAL_SUBMISSION_QUEUE = queues[0]

    except Exception:
        reportErrorAndExit('Unable to locate submission queue.')


def initializeForSubmission():

    if GLOBAL_DEBUG:
        debug('initializeForSubmission')

    global GLOBAL_ORGANIZER
    global GLOBAL_ROBOT_SUBMISSION
    global GLOBAL_SHOT_MAPPING
    global GLOBAL_VIDEO_MAPPING
    global GLOBAL_SUBMISSION_QUEUE

    # -------------------------------------------------------------------------
    # find 'organizer' group
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('find %s group.' % GROUP_ORGANIZER)

    GLOBAL_ORGANIZER = None
    for group in GLOBAL_GROUPS:
        if group.name == GROUP_ORGANIZER:
            GLOBAL_ORGANIZER = group
            break
    if GLOBAL_ORGANIZER is None:
        reportErrorAndExit('Unable to find %s group.' % GROUP_ORGANIZER)

    # -------------------------------------------------------------------------
    # find 'robot_submission' user
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('find %s user.' % USER_ROBOT_SUBMISSION)

    GLOBAL_ROBOT_SUBMISSION = None
    for user in GLOBAL_USERS:
        if user.username == USER_ROBOT_SUBMISSION:
            GLOBAL_ROBOT_SUBMISSION = user
            break
    if GLOBAL_ROBOT_SUBMISSION is None:
        reportErrorAndExit('Unable to find %s user.' % USER_ROBOT_SUBMISSION)

    # -------------------------------------------------------------------------
    # get mapping for list of media
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('build mediumID ==> videoID mapping')

    try:
        media = GLOBAL_CLIENT.getMedia(corpus=GLOBAL_CORPUS)
        mediumMapping = {medium._id: medium.name for medium in media}
        GLOBAL_VIDEO_MAPPING = {medium.name: medium._id for medium in media}
    except Exception:
        reportErrorAndExit('Unable to build mediumID ==> videoID mapping')

    # -------------------------------------------------------------------------
    # get mapping for (supposedly unique) list of submission shots
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('build (videoID, shotNumber) ==> annotationID mapping.')

    try:
        layers = GLOBAL_CLIENT.getLayers(
            GLOBAL_CORPUS, name=LAYER_SUBMISSION_SHOT)
        shotLayer = layers[0]._id
        shots = GLOBAL_CLIENT.getAnnotations(layer=shotLayer)
        GLOBAL_SHOT_MAPPING = {
            (mediumMapping[s.id_medium], s.fragment.shot_number): s._id
            for s in shots
        }

    except Exception:
        reportErrorAndExit(
            'Unable to build (videoID, shotNumber) ==> annotationID mapping.')


def createNewSubmission(submissionType, submissionName, label, evidence):

    global GLOBAL_CLIENT
    global GLOBAL_TEAM
    global GLOBAL_CORPUS
    global GLOBAL_ORGANIZER
    global GLOBAL_ROBOT_SUBMISSION

    # -------------------------------------------------------------------------
    # create empty (evidence and label) submission layers
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('create submission layers.')

    try:
        # create empty evidence layer
        evidenceLayer = GLOBAL_CLIENT.createLayer(
            GLOBAL_CORPUS, submissionName,
            data_type=DATATYPE_EVIDENCE,
            fragment_type=FRAGMENTTYPE_SUBMISSION,
            description={
                "status": SUBMISSION_STATUS_WIP,
                "id_user": GLOBAL_ME._id,
                "id_team": GLOBAL_TEAM._id
            },
            returns_id=True
        )

        # set permissions on evidence layer
        #   * team: ADMIN
        #   * organizer: READ
        #   * robot: READ
        GLOBAL_CLIENT.setLayerPermissions(
            evidenceLayer, GLOBAL_CLIENT.ADMIN,
            group=GLOBAL_TEAM._id)

        GLOBAL_CLIENT.setLayerPermissions(
            evidenceLayer, GLOBAL_CLIENT.READ,
            group=GLOBAL_ORGANIZER._id)

        GLOBAL_CLIENT.setLayerPermissions(
            evidenceLayer, GLOBAL_CLIENT.READ,
            user=GLOBAL_ROBOT_SUBMISSION._id)

        # create empty label layer
        labelLayer = GLOBAL_CLIENT.createLayer(
            GLOBAL_CORPUS, submissionName,
            data_type=DATATYPE_LABEL,
            fragment_type=FRAGMENTTYPE_SUBMISSION,
            description={
                "status": SUBMISSION_STATUS_WIP,
                "id_evidence": evidenceLayer,
                "id_user": GLOBAL_ME._id,
                "id_team": GLOBAL_TEAM._id
            },
            returns_id=True
        )

        # set permissions on label layer
        #   * team: ADMIN
        #   * organizer: READ
        #   * robot: READ
        GLOBAL_CLIENT.setLayerPermissions(
            labelLayer, GLOBAL_CLIENT.ADMIN,
            group=GLOBAL_TEAM._id)

        GLOBAL_CLIENT.setLayerPermissions(
            labelLayer, GLOBAL_CLIENT.READ,
            group=GLOBAL_ORGANIZER._id)

        GLOBAL_CLIENT.setLayerPermissions(
            labelLayer, GLOBAL_CLIENT.READ,
            user=GLOBAL_ROBOT_SUBMISSION._id)

        # cross-reference evidence and label layers
        GLOBAL_CLIENT.updateLayer(
            evidenceLayer,
            description={
                "status": SUBMISSION_STATUS_WIP,
                "id_label": labelLayer,
                "id_user": GLOBAL_ME._id,
                "id_team": GLOBAL_TEAM._id
            }
        )

    except Exception:
        reportErrorAndExit('Unable to create submission layers.')

    # -------------------------------------------------------------------------
    # fill (evidence and label) submission layers
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('upload submissions.')

    try:

        # prepare list of evidences in Camomile format
        evidences = []
        for _, row in evidence.iterrows():
            (personName, videoID, shotNumber, source) = tuple(row)
            annotation = {
                "id_layer": evidenceLayer,
                "id_medium": GLOBAL_VIDEO_MAPPING[videoID],
                "fragment": GLOBAL_SHOT_MAPPING[videoID, shotNumber],
                "data": {
                    "person_name": personName,
                    "source": source
                }
            }
            evidences.append(annotation)

        # prepare one list of label per video in Camomile format
        labels = {}
        for _, row in label.iterrows():
            (videoID, shotNumber, personName, confidence) = tuple(row)
            annotation = {
                "id_layer": labelLayer,
                "id_medium": GLOBAL_VIDEO_MAPPING[videoID],
                "fragment": GLOBAL_SHOT_MAPPING[videoID, shotNumber],
                "data": {
                    "person_name": personName,
                    "confidence": confidence
                }
            }
            labels.setdefault(videoID, []).append(annotation)

        # submit all evidences at once
        GLOBAL_CLIENT.createAnnotations(evidenceLayer, evidences)

        # submit labels video by video
        for videoID in labels:
            GLOBAL_CLIENT.createAnnotations(labelLayer, labels[videoID])

    except Exception:
        reportErrorAndExit('Unable to upload submissions.')

    # -------------------------------------------------------------------------
    # update (evidence and label) status and push to submission queue
    # -------------------------------------------------------------------------

    if GLOBAL_DEBUG:
        debug('finalize submissions.')

    try:
        GLOBAL_CLIENT.updateLayer(
            evidenceLayer,
            description={
                "submission": submissionType,
                "status": SUBMISSION_STATUS_OK,
                "id_label": labelLayer,
                "id_user": GLOBAL_ME._id,
                "id_team": GLOBAL_TEAM._id
            }
        )

        GLOBAL_CLIENT.updateLayer(
            labelLayer,
            description={
                "submission": submissionType,
                "status": SUBMISSION_STATUS_OK,
                "id_evidence": evidenceLayer,
                "id_user": GLOBAL_ME._id,
                "id_team": GLOBAL_TEAM._id
            }
        )

        GLOBAL_CLIENT.enqueue(
            GLOBAL_SUBMISSION_QUEUE,
            {
                "submittedBy": GLOBAL_ME._id,
                "id_team": GLOBAL_TEAM._id,
                "date": GLOBAL_CLIENT.getDate().date,
                "type": submissionType,
                "name": submissionName,
                "id_evidence": evidenceLayer,
                "id_label": labelLayer
            })

    except Exception:
        reportErrorAndExit('Unable to finalize submissions.')


def getSubmissions():

    # get all readable layers
    allLayers = GLOBAL_CLIENT.getLayers(GLOBAL_CORPUS, history=True)

    submissionLayers = []
    for layer in allLayers:

        data_type = layer.get('data_type', None)
        if data_type != DATATYPE_LABEL:
            continue

        submissionLayers.append({
            'date': layer.history[-1].date,
            'user': findUsername(layer.history[-1].id_user),
            'type': layer.description.submission,
            'name': layer.name,
            'label': layer._id,
            'evidence': layer.description.id_evidence,
            'status': layer.description.status,
        })

    df = pd.DataFrame(submissionLayers)
    return df


def checkSubmission(label, evidence):

    shots = set(GLOBAL_SHOT_MAPPING)

    # check that labels are only provided for selected shots
    labelShots = set(tuple(s)
                     for _, s in label[['videoID', 'shotNumber']].iterrows())
    if not labelShots.issubset(shots):
        msg = ('Labels should only be computed for provided shots.')
        raise ValueError(msg)

    # check that evidence is provided for every unique label
    labelNames = set(label['personName'].unique())
    evidenceNames = set(evidence['personName'].unique())
    if labelNames != evidenceNames:
        msg = ('There must be exactly one evidence '
               'per unique name in label submission.')
        raise ValueError(msg)

    # check that there is no more than one evidence per label
    if len(evidenceNames) != len(evidence):
        msg = ('There must be exactly one evidence '
               'per unique name in label submission.')
        raise ValueError(msg)

    # check that evidences are chosen among selected shots
    evidenceShots = set(
        tuple(s) for _, s in evidence[['videoID', 'shotNumber']].iterrows())
    if not evidenceShots.issubset(shots):
        msg = ('Evidences should only be chosen among provided shots.')
        raise ValueError(msg)


def modeList():
    submissions = getSubmissions()
    printSubmissions(submissions)


def modeDelete():

    while True:

        # print list of submissions
        submissions = getSubmissions()
        printSubmissions(submissions)

        # ask user which submission to delete
        nSubmissions = len(submissions)
        if nSubmissions == 0:
            print 'No submissions.'
            break

        choices = range(nSubmissions)
        strChoices = '|'.join(str(i) for i in range(nSubmissions))
        userInput = raw_input('Delete submission [%s]: ' % strChoices).strip()

        # check user input
        try:
            submissionIndex = int(userInput)
            assert submissionIndex in choices
        except Exception:
            break

        # actual submission deletion
        submission = dict(submissions.iloc[submissionIndex])
        labelLayer = submission['label']
        evidenceLayer = submission['evidence']

        try:
            GLOBAL_CLIENT.deleteLayer(labelLayer)
            GLOBAL_CLIENT.deleteLayer(evidenceLayer)

            GLOBAL_CLIENT.enqueue(
                GLOBAL_SUBMISSION_QUEUE,
                {
                    "deletedBy": GLOBAL_ME._id,
                    "id_team": GLOBAL_TEAM._id,
                    "date": GLOBAL_CLIENT.getDate().date,
                    "id_evidence": evidenceLayer,
                    "id_label": labelLayer
                })

        except Exception:
            reportErrorAndExit('Unable to delete submission.')


def modeCheck(pathToLabel, pathToEvidence):

    initializeForSubmission()

    label = loadLabel(pathToLabel)
    evidence = loadEvidence(pathToEvidence)
    try:
        checkSubmission(label, evidence)
    except ValueError, e:
        reportErrorAndExit(e.message)


def modePrimary(pathToLabel, pathToEvidence):

    # get list of submission
    submissions = getSubmissions()

    if not submissions.empty:
        nPrimary = len(submissions[submissions.type == 'primary'])
        if nPrimary > 0:
            reportErrorAndExit(
                'Please delete your existing '
                'primary submission first.')

    initializeForSubmission()

    # load evidence/label files and check their validity
    label = loadLabel(pathToLabel)
    evidence = loadEvidence(pathToEvidence)
    try:
        checkSubmission(label, evidence)
    except ValueError, e:
        reportErrorAndExit(e.message)

    createNewSubmission('primary', 'primary', label, evidence)

    submissions = getSubmissions()
    printSubmissions(submissions)


def modeContrastive(pathToLabel, pathToEvidence, submissionName):

    # get list of submission
    submissions = getSubmissions()

    if submissionName == 'primary':
        reportErrorAndExit(
            'Please use a different name for your contrastive submission.')

    if not submissions.empty:
        nContrastive = len(submissions[submissions.type == 'contrastive'])
        if nContrastive > 3:
            reportErrorAndExit(
                'Please delete one of your existing '
                'contrastive submissions first.')

        nSameName = len(submissions[submissions.name == submissionName])
        if nSameName > 0:
            reportErrorAndExit(
                'Please choose a different name or '
                'delete the existing submission with same name.')

    initializeForSubmission()

    # load evidence/label files and check their validity
    label = loadLabel(pathToLabel)
    evidence = loadEvidence(pathToEvidence)
    try:
        checkSubmission(label, evidence)
    except ValueError, e:
        reportErrorAndExit(e.message)

    createNewSubmission('contrastive', submissionName, label, evidence)

    submissions = getSubmissions()
    printSubmissions(submissions)


if __name__ == '__main__':

    arguments = docopt(__doc__, version='0.1')

    GLOBAL_DEV_OR_TEST = 'test'
    if arguments['--dev']:
        GLOBAL_DEV_OR_TEST = 'dev'

    GLOBAL_DEBUG = False
    if arguments['--debug']:
        GLOBAL_DEBUG = True

    url = arguments['--url']
    username = arguments['--login']
    password = arguments['--password']
    initialize(url, username=username, password=password)

    if arguments['list']:
        modeList()

    if arguments['delete']:
        modeDelete()

    if arguments['check']:
        pathToLabel = arguments['<run.label>']
        pathToEvidence = arguments['<run.evidence>']
        modeCheck(pathToLabel, pathToEvidence)

    if arguments['primary']:
        pathToLabel = arguments['<run.label>']
        pathToEvidence = arguments['<run.evidence>']
        modePrimary(pathToLabel, pathToEvidence)

    if arguments['contrastive']:
        submissionName = arguments['<run>']
        pathToLabel = arguments['<run.label>']
        pathToEvidence = arguments['<run.evidence>']
        modeContrastive(pathToLabel, pathToEvidence, submissionName)
