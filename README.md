# Fast Censor
## fast_censor

* A fast and flexible utility for filtering out profanity or other strings from text
* the fastest string utility for profanity detection / censoring
* allows for detection with repeated characters and character substition

## Installation

### PiP
`pip install fast-censor`

### From source
```
cd fast-censor  # enter into project directory
python setup.py install 
```

### From GitHub
`pip install git+https://github.com/mbuchove/fast_censor.git`

## Uses
```
from fast_censor import ProfanityTrie

censor = ProfanityTrie()
censor.censor("test text")

# load alternate path


```

### Encryption
By default, the word lists are encrypted so you can avoid displaying vulgar or offensive words 