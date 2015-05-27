
This repository provides both evaluation and submission scripts.

## Installation

```bash
git clone https://github.com/MediaevalPersonDiscoveryTask/evaluation.git
cd evaluation
pip install -r requirements.txt
```
## Evaluation metric

The official evaluation metric is the Evidence-weighted Mean Average Precision (or EwMAP).  
A detailed description can be found in the [wiki](https://github.com/MediaevalPersonDiscoveryTask/evaluation/wiki/Evaluation-metric) of this repository.

We provide a Python implementation of EwMAP.  
This implementation will be used for the final ranking of submissions.

```bash
$ python evaluation.py --queries=samples/queries.lst  # list of queries
                       samples/dev.test2.shot \       # reference list of shots
                       samples/dev.test2.ref  \       # label reference
                       samples/dev.test2.eviref \     # evidence reference
                       samples/dev.test2.label \      # label hypothesis
                       samples/dev.test2.evidence     # evidence hypothesis
EwMAP = 51.39 %  # <-- official evaluation metric (higher is better)
MAP = 51.77 %    # <-- standard mean average precision (higher is better)
C = 58.75 %      # <-- evidence correctness (higher is better)
```

More information about file formats can be found in the [wiki](https://github.com/MediaevalPersonDiscoveryTask/evaluation/wiki/File-format).

## Submission

Each team must submit *exactly one primary* run, following strict "no supervision" constraints described in the [private task wiki](http://mediaeval15.pbworks.com/w/page/95456627/PersonDiscovery).  
Additionally, each team is allowed to submit *up to four contrastive* runs.  
The official ranking will be based on *primary* runs.

We provide a Python script to manage (list, delete, create) your submissions.

```bash
$ python submission.py --help
```

## Contribute

Feel free to contribute to the evaluation tool or share your own implementations in alternative languages, using [GitHub's pull request](https://help.github.com/articles/using-pull-requests/) procedure. We will gladly add them to this repository.
