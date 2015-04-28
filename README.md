# Evaluation

WORK IN PROGRESS - WORK IN PROGRESS - WORK IN PROGRESS - WORK IN PROGRESS

This repository provides the definition of the official evaluation metric of the "Person Discovery" [MediaEval](http://www.multimediaeval.org/mediaeval2015/) task.

Official Python implementation is available and will be the one used for ranking submissions.

## Python

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
## File format

### Shot List (.shot)

```
videoID shotNumber startTime endTime startFrame endFrame
```

- `videoID`: unique video identifier
- `shotNumber`: shot number
- `startTime`: start time in seconds
- `endTime`: end time in seconds
- `startFrame`: start frame index
- `endFrame`: end frame index

#### Example

```
BFMTV_PlanetShowBiz_1981-04-17_091700 000023 00054.235 00057.890 0001354 0001440
```

### Reference (.ref)

```
videoID shotNumber personName isEvidence evidenceSource
```

- `videoID`: unique video identifier
- `shotNumber`: shot number
- `personName`: person name (according to convention)
- `isEvidence`: does this shot provide identity evidence for `personName` (`true`, `false` or `na`)
- `evidenceSource`: `na` or `audio` or `image` or `both` 

#### Example

```
BFMTV_PlanetShowBiz_1981-04-17_091700 000023 johann_poignant true
```

### Label submission (.label)

```
videoID shotNumber personName confidence
```

- `videoID`: unique video identifier
- `shotNumber`: shot number
- `personName`: person name (according to convention)
- `confidence`: confidence score

#### Example

```
BFMTV_PlanetShowBiz_1981-04-17_091700 000023 yohann_poignent 0.23
BFMTV_PlanetShowBiz_1981-04-17_091700 000024 yohann_poignent 0.32
BFMTV_PlanetShowBiz_1981-04-17_091700 000025 yohann_poignent 1.20
```

### Evidence submission (.evidence)

Evidence submission file MUST contain exactly one line per unique `personName` in label submission file.
In case no evidence is provided, the corresponding lines in the label submission file are removed prior evaluation. 

```
personName videoID shotNumber source
```

- `personName`: person name (according to convention)
- `videoID`: unique video identifier
- `shotNumber`: shot number
- `source`: `audio` or `image`

#### Example

```
yohann_poignent BFMTV_PlanetShowBiz_1981-04-17_091700 000024 image
```

## Contribute

Feel free to share your own implementations in alternative languages, using [GitHub's pull request](https://help.github.com/articles/using-pull-requests/) procedure.
We will gladly add them to this repository.
