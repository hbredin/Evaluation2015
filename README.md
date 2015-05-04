# Evaluation

WORK IN PROGRESS - WORK IN PROGRESS - WORK IN PROGRESS - WORK IN PROGRESS

This repository provides the definition of the official evaluation metric of the "Person Discovery" MediaEval task, along with tools to compute this metric.

## Evaluation metric

The official metric for the MediaEval "Person Discovery" task is the [Evidence-weighted Mean Average Precision](https://github.com/MediaevalPersonDiscoveryTask/evaluation/wiki/Evaluation-metric) (EwMAP).

## Evaluation tools

We provide a Python implementation of EwMAP.  
This implementation will be the one used for ranking submissions.

### Installation

```bash
git clone https://github.com/MediaevalPersonDiscoveryTask/evaluation.git
cd evaluation
pip install -r requirements.txt
```

### Usage

```bash
python evaluation.py dev.shot dev.ref dev.label dev.evidence
```

More information about file formats can be found in the [wiki](https://github.com/MediaevalPersonDiscoveryTask/evaluation/wiki/Evaluation-metric).


## Contribute

Feel free to contribute to the tool or share your own implementations in alternative languages, using [GitHub's pull request](https://help.github.com/articles/using-pull-requests/) procedure.  
We will gladly add them to this repository.
