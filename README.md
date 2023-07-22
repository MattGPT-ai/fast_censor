# Fast Censor

## fast_censor

* A fast and flexible package for filtering out profanity or other strings from text, ~300 times faster than alternatives
* the fastest string utility for profanity detection / censoring
* allows for detection with repeated characters and character substition


## Installation

### From source
```
cd fast-censor  # enter into project directory
python setup.py install 
```

### From GitHub
`pip install git+https://github.com/mbuchove/fast_censor.git`


## Uses
```
from fast_censor import FastCensor

# to load default (encoded) profanity word list
censor = FastCensor()

# load alternate path, example is a plain text word list without encoding
censor_clean = fast_censor.FastCensor(
    wordlist=fast_censor.WordListHandler.get_default_wordlist_path("clean_wordlist_decoded.txt"), 
    wordlist_encoded=False,
)

# censor texts or simply get the indices of matches
matches = censor_clean.check_text("this bat is for riii1ick")
# >>> [(5, 9), (17, 25)]
censored_text = censor_clean.censor("fuuudge you")
# >>> "******* you"
```

###  Character substitutions
FastCensor's profanity matcher allows the flexibility to match words when specified characters are substituted for others, 
as is customary in 1337 speak. A default is set for commonly used substitutions.

To set your own, for example, you would pass the following into `FastCensor`

`substitutions = {'a': '@4'}`

### Character repititon
By default, words will still match even if a matching character is repeated any number of times.
This includes any valid substitute for that character

For example, `"baaa@@aatt"` will match `"bat"` 

You can turn this off by passing `allow_repititions=False` to `censor_text` or `check_text`

### Delimiters
Use the `delimiters` parameter of `FastCensor` to set the delimiter characters, which determine the boundaries of a word. 
Profanity matches will not extend across any delimiting character.

For example, if `'_'` is a delimiter, "ba_t" would not match "bat"


## Editing and saving wordlist
`censor.add_word('new_word')  # to add a new word`
`censor.write_words_file("word_lists/new_wordlist_encoded.txt", encode=True)`

### Encoding
By default, the word lists are base64-encoded, so you can avoid displaying vulgar or offensive words. 
If you would like to save a word list in plain text, set `encode=False` in `write_words_file`