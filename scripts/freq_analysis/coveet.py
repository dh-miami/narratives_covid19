import argparse
import requests
import string
import pandas as pd
import sys
import os
import multiprocessing
import subprocess
from datetime import datetime, timedelta
from functools import reduce
from itertools import combinations
from collections import defaultdict, Counter
from tqdm import tqdm
import IPython

# https://covid.dh.miami.edu/twitter-texts/
BASE_QUERY_URL = 'https://covid.dh.miami.edu/get/?'
LANG_OPS = ['en', 'es']
# geography options: florida, argentina, columbia, ecuador, spain,
# mexico, peru
GEO_OPS = ['fl', 'ar', 'co', 'ec', 'es', 'mx', 'pe']
COMMENT_TOKEN = '//'
HEADER_TOKEN = '$'
COVID_EPOCH = datetime(month = 4, day = 24, year = 2020) # dawn of time
# TODO create a settings.py file with these constants
ALL_FNAME = "dhcovid_en_es_ar_co_ec_es_fl_mx_pe_all.csv"
WORD_UUID_FNAME = "word_uuid_table.csv"

def pos_type(string):
    value = int(string)
    if value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not positive")
    return value


def date_type(string):
    try:
        return datetime.strptime(string, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"{string} should be YYYY-MM-DD")

def get_data_df(lang, geo, start_date, end_date):
    tweet_dic = {'date': [], 'lang': [], 'geo': [], 'text': [], 'hashtags': []}
    for l in lang:
        for g in geo:
            if l == 'en' and g != 'fl':
                continue
            diff = end_date - start_date + timedelta(days=1)
            for date in (start_date + timedelta(n) for n in range(diff.days)):
                tweets = requests.get(query_url(l, g, date), stream=True).text
                for t in tweets.splitlines():
                    words = t.split()
                    hashtags = [w for w in words if w[0] == '#']
                    clean = [w for w in words if w[0] != '@'
                             and w != 'URL' and w[0] != '#']
                    tweet_dic['date'].append(date)
                    tweet_dic['lang'].append(l)
                    tweet_dic['geo'].append(g)
                    tweet_dic['text'].append(' '.join(clean))
                    tweet_dic['hashtags'].append(' '.join(hashtags))

    return pd.DataFrame(tweet_dic)

def query_url(lang, geo, start_date, end_date=None):
    # make sure first two parameters valid
    assert lang in LANG_OPS
    assert geo in GEO_OPS
    base_url = f"{BASE_QUERY_URL}lang={lang}&geo={geo}&date="
    start_date_str = start_date.strftime('%Y-%m-%d')

    if end_date is not None:
        end_date_str = end_date.strftime('%Y-%m-%d')
        return base_url + f"from-{start_date_str}-to-{end_date_str}"

    return base_url + start_date_str

def handle_query(args):
    today = datetime.today()
    today = datetime(day = today.day-1, month = today.month, year = today.year)
    if args.all:
        args.lang = list(set(LANG_OPS))
        args.geo = list(set(GEO_OPS))
        # 3 possibilities: download everything, download a part, up-to-date
        if not os.path.exists(ALL_FNAME):
            start_date = COVID_EPOCH
            end_date = today
        else:
            # TODO always assuming the last row has the biggest uuid;
            # this may be violated if the data is sorted; watch out for order
            # dependency
            # good sanity check would be to check that uuid is non-decreasing with
            # no repetitions
            uuid, date = subprocess.check_output(
                ['tail', '-1', ALL_FNAME]).decode().split(",")[:2]
            uuid = int(uuid)
            date = datetime.strptime(date, '%Y-%m-%d')
            # where we should start downloading
            start_date = date + timedelta(days = 1)
            end_date = today
        if start_date >= end_date:
            print("up to date")
            return
    else:
        args.lang = list(set(args.lang))
        args.geo = list(set(args.geo))
        start_date, end_date = args.date

    df = get_data_df(args.lang, args.geo, start_date, end_date)
    if args.all:
        df.insert(loc=0, column='uuid', value=[i for i in range(len(df))])
        fname = ALL_FNAME
        if os.path.exists(ALL_FNAME):
            df['uuid'] = df['uuid'] + uuid + 1
            with open(ALL_FNAME, 'a') as f:
                df.to_csv(f, header=False, index=False)
        else:
            df.to_csv(fname, index = False)
    else:
        fname = f"dhcovid_" + \
                f"{args.date[0].year}-{args.date[0].month}-{args.date[0].day}" + \
                f"_{args.date[1].year}-{args.date[1].month}-{args.date[1].day}"
        for l in sorted(args.lang):
            fname += f"_{l}"
        for g in sorted(args.geo):
            fname += f"_{g}"
        fname += ".csv"
        df.to_csv(fname)
    print(f"wrote df to {fname} 🎉")

def handle_nlp(args):
    df = pd.read_csv(args.file, index_col=0)
    # convert dates encoded as strings to formal datetime object
    df['date'] = pd.to_datetime(df['date'])
    df['text'] = df['text'].str.split()
    df['hashtags'] = df['hashtags'].str.split()
    all_metrics = [args.ngram, args.hashtags, args.users]
    # assuming only one possible value for metric currently
    metrics = [m for m in all_metrics if m is not False]
    if len(metrics) > 1:
        raise ValueError("only one metric supported at a time")
    if isinstance(metrics[0], int):
        col_name = 'text'
    elif metrics[0] == 'h':
        col_name = 'hashtags'
        metrics[0] = 1
    elif metrics[0] == 'u':
        col_name = 'users'
        raise ValueError("users not supported currently")

    df = df.dropna(subset=[col_name])
    if args.mutex:
        grouping = df.groupby(["geo", "lang"])["text"]
        vocab_dic = uniq_vocab_by_group(grouping)
        df[col_name] = df.apply(
            lambda x : set(x[col_name]) & vocab_dic[(x['geo'], x['lang'])],
            result_type='reduce', axis=1)

    freq_df = data2freq(df, metrics[0], args.top, args.consecutive,
        text_col_name=col_name)

    new_fname = args.file[:args.file.rfind('.')] + f"_{metrics[0]}"
    if args.consecutive:
        new_fname += "consec"
    new_fname += ".csv"
    print(freq_df.head())
    print(f"wrote freq df to {new_fname} 🎉")
    freq_df.to_csv(new_fname)

def handle_tidy(args):
    df = pd.read_csv(args.file, index_col=0)
    # handle lemmatization
    # TODO udpipe puts in NA for out of vocabulary words
    if args.lemmatize:
        num_cpu = multiprocessing.cpu_count() // 2
        l_fname = args.file.split(".")[0] + "_udpipe.csv"
        os.system(f"Rscript run_udpipe.R {args.file} {num_cpu} {l_fname}")
        # pick up the lemmatized file and keep going; also delete the
        # file as it is possibly intermediary
        assert os.path.exists(l_fname)
        df = pd.read_csv(l_fname)
        os.remove(l_fname)

    # handle stopwords
    text_stopwords = []
    hashtag_stopwords = []
    mode = "BOTH"  # default mode if no header specified
    if args.stopwords is not None:
        # go for each file in stopwords
        for fn in args.stopwords:
            with open(fn, 'r') as f:
                for line in f.readlines():
                    if line.startswith(COMMENT_TOKEN):
                        # ignore lines with comments
                        pass
                    elif line.startswith(HEADER_TOKEN):
                        params = line[len(HEADER_TOKEN):].split()
                        assert 0 < len(params) < 3  # sanity check
                        if "HASHTAGS" in params and "TEXT" in params:
                            mode = "BOTH"
                        elif "HASHTAGS" in params:
                            mode = "HASHTAGS"
                        elif "TEXT" in params:
                            mode = "TEXT"
                        else:
                            msg = "found a bad keyword in a stopwords file"
                            raise ValueError(msg)
                    else:
                        if mode == "BOTH":
                            text_stopwords.extend(line.split())
                            hashtag_stopwords.extend(line.split())
                        elif mode == "TEXT":
                            text_stopwords.extend(line.split())
                        else:
                            hashtag_stopwords.extend(line.split())
        # specify that some stopwords are for the text
        # and others are for the hashtags
        df['text'] = df['text'].apply(lambda text: " ".join(
            [w for w in text.split() if w not in text_stopwords])
            if text == text else "")
        df['hashtags'] = df['hashtags'].apply(lambda text: " ".join(
            [w for w in text.split() if w not in hashtag_stopwords])
            if text == text else "")

    # prepare the output file
    out_fname = args.file.split(".")[0]
    if args.stopwords is not None:
        out_fname += "_stopworded"
    if args.lemmatize:
        out_fname += "_lemmatized"
    out_fname += ".csv"

    if out_fname == args.file:
        print("❗️you did not ask me to do any tidying")
    else:
        df.to_csv(out_fname)
        print(f"wrote tidied df to {out_fname} 🎉")


def count_ngrams(df, ngram, consecutive, col_name=None, count_dic=None):
    # assumes the column identified by col_name is a tokenized list of words
    if count_dic is None:
        count_dic = defaultdict(int)

    itr = df if col_name is None else df[col_name]
    for text in itr:
        if text == text:
            if consecutive:
                # traditional approach to getting n-grams
                for i in range(len(text) - ngram + 1):
                    window = text[i:i+ngram]
                    count_dic[tuple(sorted(window))] += 1
            else:
                # treating entire tweet as context
                for comb in combinations(set(text), ngram):
                    count_dic[tuple(sorted(comb))] += 1
    return count_dic

def uniq_vocab_by_group(groups):
    vocab_dic = {
        k: [set(row) for row in g if row == row] for k, g in groups}
    # collapse tweet units into one set for each geo-lang pair
    for k, v in vocab_dic.items():
        vocab = set()
        for s in v:
            vocab.update(s)
        vocab_dic[k] = vocab

    # universe of words
    # TODO if there is a slowdown, it might be the reduce
    all_words = reduce(set.union, [v for v in vocab_dic.values()])
    complement_vocab_dic = {k: all_words - v for k, v in vocab_dic.items()}
    unique_vocab_dic = {}
    # uniq_v2 = v2 \cap v1' \cap v3' \cap v4' ... vn'
    for k, v in vocab_dic.items():
        unique_vocab_dic[k] = v
        for k2, v2 in complement_vocab_dic.items():
            if k != k2:
                unique_vocab_dic[k] &= v2  # do intersection and assignment

    return unique_vocab_dic

def data2freq(df, ngram, top_n, csc, date_col_name='date', text_col_name='text'):
    #uniq_vocab_by_gl(df, text_col_name)
    group = df.groupby([date_col_name])[text_col_name]
    # list of all the top words for every day
    counts = [dict(
        Counter(count_ngrams(g, ngram, csc)).most_common(top_n)) for _, g in group]
    dates = [date for date, _ in group]

    df_dic = {k: [] for top in counts for k in top.keys()}
    for k in df_dic.keys():
        for top in counts:
            df_dic[k].append(0)
            if k in top:
                df_dic[k][-1] += top[k]
    df_dic['date'] = dates
    df = pd.DataFrame(df_dic)
    # remove tuple notation
    df.rename(columns=lambda x: ' '.join(x) if x != 'date' else x, inplace=True)
    # prepare the new df
    return df

def handle_search(args):
    words = args.search
    search_dic = {"query_words" : [], "uuid": []}
    df = pd.read_csv(ALL_FNAME)

    for text, uuid in tqdm(zip(df['text'], df['uuid']), total=len(df)):
        if text != text:
            # skip rows with empty text fields
            continue
        for word in words:
            if word in text:
                search_dic['query_words'].append(word)
                search_dic['uuid'].append(uuid)

    search_df = pd.DataFrame(search_dic)
    search_df.sort_values(by = ["query_words", "uuid"], inplace = True)

    search_df.to_csv("word_uuid_table.csv", index = False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='a very basic interface to the digital narratives database',
        allow_abbrev=True)
    subparsers = parser.add_subparsers()

    nlp = subparsers.add_parser("nlp")
    nlp.add_argument('-top', default=20, type=pos_type)
    nlp.add_argument('-ngram', default=False, type=pos_type)
    nlp.add_argument('-users', action='store_const', const='u', default=False)
    nlp.add_argument('-hashtags', action='store_const', const='h', default=False)
    nlp.add_argument('-mutex', action='store_true', default=False)
    nlp.add_argument('-consecutive', action='store_true', default=False)
    nlp.add_argument('-file')
    nlp.set_defaults(func=handle_nlp)

    # if want same day, just give same day twice
    # ask for days=6 because of subtract one (7-1) before you go rule
    query = subparsers.add_parser("query")
    default_start = datetime.today() - timedelta(days=7)
    default_start = datetime(day = default_start.day,
                                      month = default_start.month,
                                      year = default_start.year)
    default_end = datetime.today() - timedelta(days=1)
    default_end = datetime(day=default_end.day,
                                      month=default_end.month,
                                      year=default_end.year)

    query.add_argument('-date', default=[default_start, default_end], nargs=2,
                       type=date_type)
    query.add_argument('-lang', default=LANG_OPS,
                       choices=LANG_OPS, nargs='+')
    query.add_argument('-geo', default=GEO_OPS,
                       choices=GEO_OPS, nargs='+')
    # this one overrides all other options
    query.add_argument('-all', action='store_true', default=False)
    query.set_defaults(func=handle_query)

    tidy = subparsers.add_parser("tidy")
    tidy.add_argument('-file')
    tidy.add_argument('-stopwords', default=None, nargs='+')
    tidy.add_argument('-lemmatize', action='store_true', default=False)
    tidy.set_defaults(func=handle_tidy)

    parser.add_argument('-search', nargs='+')
    parser.set_defaults(func=handle_search)

    args = parser.parse_args()
    print(args)
    args.func(args)
