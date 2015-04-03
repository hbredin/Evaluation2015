file format
==============

## Shot List (.shot)

```
videoID shotNumber startTime endTime startFrame endFrame
```

- `videoID`: unique video identifier
- `shotNumber`: shot number
- `startTime`: start time in seconds
- `endTime`: end time in seconds
- `startFrame`: start frame index
- `endFrame`: end frame index

### Example

```
BFMTV_PlanetShowBiz_1981-04-17_091700 000023 000054.235 000057.890 0001354 0001440
```

## Reference (.ref)

```
videoID shotNumber personName isEvidence
```

- `videoID`: unique video identifier
- `shotNumber`: shot number
- `personName`: person name 
- `isEvidence`: does this shot provide identity evidence for `personName` (`true`, `false` or `maybe`)

### Example

```
BFMTV_PlanetShowBiz_1981-04-17_091700 000023 johann_poignant true
```

### Person name

Field `personName` must only contain lower case latin alphabet characters (`a` to `z`) with diacritical.
Hyphens and white spaces must be replaced by `_` (underscore). 

Whenever possible, person name should include both the first name and the last name.
You may use aliases if the person is introduced by their alias (e.g. `madonna` for Madonna Louise Ciccone)

#### Example of valid person names

- `johann_poignant` for Johann Poignant
- `herve_bredin` for Herv**é** Bredin
- `marie_antoinette_josephe_jeanne_de_habsbourg_lorraine` for Marie**-**Antoinette Jos**è**phe Jeanne de Habsbourg**-**Lorraine 

#### Example of invalid person names

- `Herve_Bredin` (lower case only)
- `claude barras` (no space)
- `françois_hollande` (no diacritical)
- `obama_barack` (first name should come first)


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


