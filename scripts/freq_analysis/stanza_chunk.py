import sys
import pandas as pd
import stanza

print(sys.argv)
num_cores, index = int(sys.argv[1]), int(sys.argv[2])
fname = sys.argv[3]

df = pd.read_csv(fname,
    skiprows = lambda r: r % num_cores != index and r != 0)

stanza_es = stanza.Pipeline('es', processors='tokenize, pos, lemma')
stanza_en = stanza.Pipeline('en', processors='tokenize, pos, lemma')

groups = df.groupby(by=['lang'])
new_df = None
for lang, sub_df in groups:
    # double newline is needed for stanza
    sub_df = sub_df.fillna('か')
    total_str = sub_df['text'].str.cat(sep='\n\n')
    if lang == "en":
        tokenized = stanza_en(total_str)
    elif lang == "es":
        tokenized = stanza_es(total_str)
    else:
        raise ValueError("something bad happened")

    # list of list of words: list of tweets where each tweet is a list
    # of words
    tweets = [[dic['lemma'] for dic in t] for t in tokenized.to_dict()]
    tweets = [" ".join(tweet) for tweet in tweets]
    # overrwrite the text column with the lemmatized tweets
    sub_df['text'] = pd.Series(tweets)
    if new_df is None:
        new_df = sub_df
    else:
        # row-wise concatenation
        new_df = pd.concat([new_df, sub_df])

new_df = new_df.replace('か', '')
new_df = new_df.reset_index(drop = True)
new_df.to_csv(f'tmp_{index}.csv', index = False)
