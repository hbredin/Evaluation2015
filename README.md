## Evidence-weighted Mean Average Precision

The official evaluation metric is the Evidence-weighted Mean Average Precision (or EwMAP).  
A detailed description can be found in the [wiki](https://github.com/MediaevalPersonDiscoveryTask/evaluation/wiki/Evaluation-metric) of this repository.

### Evaluation tools

We provide a Python implementation of EwMAP.  
This implementation will used for ranking submissions.


#### Installation

```bash
git clone https://github.com/MediaevalPersonDiscoveryTask/evaluation.git
cd evaluation
pip install -r requirements.txt
```

#### Usage

```bash
$ python evaluation.py samples/dev.shot \    # reference list of shots
                       samples/dev.ref  \    # label reference
                       samples/dev.eviref \  # evidence reference
                       samples/dev.label \   # label hypothesis
                       samples/dev.evidence  # evidence hypothesis
EwMAP = xx.xx %  # <-- official evaluation metric (higher is better)
MAP = yy.yy %    # <-- standard mean average precision (higher is better)
C = zz.zz %      # <-- evidence correctness (higher is better)
```

More information about file formats can be found in the [wiki](https://github.com/MediaevalPersonDiscoveryTask/evaluation/wiki/File-format).

#### Contribute

Feel free to contribute to the tool or share your own implementations in alternative languages, using [GitHub's pull request](https://help.github.com/articles/using-pull-requests/) procedure. We will gladly add them to this repository.
