file format
==============

## Shot List (.shot)

video shot tstart tend fstart fend

- video: unique video identifier
- shot: shot number
- tstart: start time in seconds
- tend: end time in seconds
- fstart: start frame index
- fend: end frame index

### Example

BFMTV_PlanetShowBiz_1981-04-17_091700 000023 000054.235 000057.890 0001354 0001440






## shot reference (.ref)
<video> <name> <shot> <evidence>

- video: video name
- name: person name
- shot: shot number
- evidence: as ths shot is an evidence (True or False)

## Hypothesis for shot (.hyp)
<video> <name> <shot> <confidence> <evidence>

- video: video name
- name: person name
- shot: shot number
- confidence: confidence score of the automatic system

## Hypothesis for evidence (.evid)
<video> <name> <shot> <evidence> <type>

- video: video name
- name: person name
- shot: shot number
- evidence: as ths shot is an evidence (True or False)
- type: type of the evidence (spoken or written)


