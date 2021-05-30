import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def generate_lexicon_file_from_memolon(en_tsv, es_tsv, vader_dir="vaderSentiment"):
    memolon_en = pd.read_csv(en_tsv, delimiter='\t', encoding='utf-8')[
        ['word', 'valence', 'arousal', 'dominance']].dropna()
    memolon_es = pd.read_csv(es_tsv, delimiter='\t', encoding='utf-8')[
    ['word', 'valence', 'arousal', 'dominance']].dropna()
    lexicon_en_es = pd.concat([memolon_es, memolon_en])[
        ['word', 'valence', 'arousal', 'dominance']]

    # take average for duplicate words like vamos
    lexicon_en_es = lexicon_en_es.groupby('word').mean().reset_index()

    # from the paper: "VAD uses 1-to-9 scales ('5' encodes the neutral value)"
    # ref: https://www.aclweb.org/anthology/2020.acl-main.112.pdf
    lexicon_en_es[['valence', 'arousal', 'dominance']] = \
        lexicon_en_es[['valence', 'arousal', 'dominance']] - 5

    lexicon_en_es.to_csv(f'{vader_dir}/memolon_vader.txt',
                         sep='\t', index=False, header=False)
    print(f'wrote {vader_dir}/memolon_vader.txt to file!')

def plot_pos_neg_senti_words(df, x, y, n=10, num_cols=2):
    df = df.sort_values(by=['geo', y])
    num_rows = len(df['geo'].unique()) // num_cols
    num_rows += 1 if num_rows * num_cols < len(df['geo'].unique()) else 0

    fig, axes = plt.subplots(num_rows, num_cols)
    flattened = axes.flatten()
    geo_lang_pairs = set(
        [(g, l) for (g, l) in df[['geo', 'lang']].to_numpy()])
    for i, (geo, lang) in enumerate(geo_lang_pairs):
        words = df[(df['geo'] == geo) &
                            (df['lang'] == lang)][[x, y]]
        bottom_n = words.head(n)
        top_n = words.tail(n)
        extreme_2n = pd.concat([bottom_n, top_n])
        colors = plt.get_cmap('cool').reversed()(
            np.linspace(0, 1, len(extreme_2n[x])))
        flattened[i].barh(extreme_2n[x],
                        extreme_2n[y], color=colors)
        flattened[i].set_title(f"{geo} {lang}")



#generate_lexicon_file_from_memolon('en.tsv', 'es.tsv')

