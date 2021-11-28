# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: Python [conda env:profanity_check2]
#     language: python
#     name: conda-env-profanity_check2-py
# ---

# %%
import profanity_check_trie
from pympler import asizeof
# %load_ext memory_profiler

# %memit pf = profanity_check_trie.ProfanityTrie()
print(asizeof.asized(pf))

text = "oh craaa@@a@p  " * 50

# first implementation
# %time pf.check_text(text, debug=False)
# %timeit pf.check_text(text, debug=False)

# %%
import profanity_check_trie
from pympler import asizeof
# %load_ext memory_profiler

# %memit pf = profanity_check_trie.ProfanityTrie()
print(asizeof.asized(pf))

text = "oh craaa@ap " * 50

# second implementation
# %time result = pf.check_text(text)
print(f"{result} instances of profanity found!")
# %timeit pf.check_text(text)


# %%
import better_profanity

print(better_profanity.__version__)
print(asizeof.asized(better_profanity.profanity))

# %time better_profanity.profanity.contains_profanity(text)
# %timeit better_profanity.profanity.contains_profanity(text)

# %%
import profanity_check
print(asizeof.asized(profanity_check))

# %time profanity_check.predict([text])
# %timeit profanity_check.predict([text])

# %%
import sys, profanity_check_trie, better_profanity

if 'pf' not in vars():
    pf = profanity_check_trie.ProfanityTrie()

tests = ['rii11ick', 'ajbaoa', "You p1ec3 of fUdge.",
         'fvudge', 'fvudcge', 'fuvdge', 'fuudge', 'Spl1t', '', 'mbass', 'fudge', 'ifudge']

for test in tests:
    #print(better_profanity.profanity.contains_profanity(test), bool(pf.check_text(test)))
    if bool(better_profanity.profanity.contains_profanity(test)) == bool(pf.check_text(test, False)):
        print('passed', test)
    else:
        print('failed', test)

# %%
s1 = {' ', '\t', '_', ',', '_', '\n'}
s2 = " \t_,.\n"
c = '\n'
# %timeit c in s1
# %timeit c in s2
print(c in s1, c in s2)


# %%
x = list('string')
x[1:4] = '*' * 3
x
