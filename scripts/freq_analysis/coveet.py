import argparse
from datetime import datetime, timedelta
import requests
import string
import pandas as pd
from itertools import combinations
from collections import defaultdict, Counter
from nltk.corpus import stopwords
from tqdm import tqdm

BASE_QUERY_URL = 'https://covid.dh.miami.edu/get/?'
DEFAULT_QUERY_FILE = "query.csv"
DEFAULT_NLP_FILE = "nlp.csv"

LANG_OPS = ['en', 'es']
# geography options: florida, argentina, columbia, ecuador, spain,
# mexico, peru
GEO_OPS = ['fl', 'ar', 'co', 'ec', 'es', 'mx', 'pe']

STOPWORDS = stopwords.words('english') + stopwords.words('spanish') + \
        list(string.punctuation) + ['rt', 'via', '…', '’', 'covid19']

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


def handle_query(args):
    args.lang = list(set(args.lang))
    args.geo = list(set(args.geo))
    start_date, end_date = args.date
    df = get_data_df(args.lang, args.geo, start_date, end_date)
    fname = f"dhcovid_" + \
            f"{args.date[0].year}-{args.date[0].month}-{args.date[0].day}" + \
            f"_to_{args.date[1].year}-{args.date[1].month}-{args.date[1].day}"
    for l in args.lang:
        fname += f"_{l}"
    for g in args.geo:
        fname += f"_{g}"
    fname += ".csv"
    df.to_csv(fname)
    print(f"wrote df to {fname}!")

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
                             and w != 'URL' and w[0] != '#'
                             and w not in STOPWORDS]
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

def handle_nlp(args):
    df = pd.read_csv(args.file)
    # convert dates encoded as strings to formal datetime object
    df['date'] = pd.to_datetime(df['date'])
    all_metrics = [args.ngram, args.hashtags, args.users]
    # assuming only one possible value for metric currently
    metrics = [m for m in all_metrics if m is not False]
    if len(metrics) > 1:
        raise ValueError("only one metric supported at a time")
    if isinstance(metrics[0], int):
        freq_df = data2freq(df, metrics[0], args.top)
    elif metrics[0] == 'h':
        freq_df = data2hashtags(df, args.top)
    elif metrics[0] == 'u':
        raise ValueError("users not supported currently")
    print(freq_df)
    new_fname = args.file[:args.file.rfind('.')] + f"_{metrics[0]}.csv"
    print(f"wrote freq df to {new_fname}!")
    freq_df.to_csv(new_fname)

def data2hashtags(df, top_n):
    group = df.groupby(['date'])['hashtags']
    # list of all the top words for every day
    counts = []
    dates = []

    for n, g in group:
        dates.append(n)
        d = defaultdict(int)
        for hashtags in g:
            # skip empty hashtags
            if hashtags == hashtags:
                tags_list = "".join(hashtags.replace(' ', '')).split("#")[1:]
                for tag in tags_list:
                   d[tag] += 1
        counts.append(dict(Counter(d).most_common(top_n)))

    df_dic = {k:[] for top in counts for k in top.keys()}
    for k in df_dic.keys():
        for top in counts:
            df_dic[k].append(0)
            if k in top:
                df_dic[k][-1] += top[k]
    df_dic['date'] = dates
    # prepare the new df
    return pd.DataFrame(df_dic)

def data2freq(df, ngram, top_n):
    group = df.groupby(['date'])['text']
    # list of all the top words for every day
    counts = []
    dates = []

    for n, g in group:
        dates.append(n)
        d = defaultdict(int)
        for tweet in g:
            # treating the tweet as an atomic unit
            # skip empty tweets
            if tweet == tweet:
                for comb in combinations(set(tweet.split()), ngram):
                    d[tuple(sorted(comb))] += 1

        tup_values = [(' '.join(value), count)
                      for value, count in Counter(d).most_common(top_n)]
        counts.append(dict(tup_values))

    df_dic = {k: [] for top in counts for k in top.keys()}
    for k in df_dic.keys():
        for top in counts:
            df_dic[k].append(0)
            if k in top:
                df_dic[k][-1] += top[k]
    df_dic['date'] = dates
    # prepare the new df
    return pd.DataFrame(df_dic)


def days_to_df(lang, geo, start_date, end_date, metric=1, top_n=10):
    lang = list(set(lang))
    geo = list(set(geo))
    print(f"l {lang} g {geo} start {start_date} end {end_date} m {metric} top {top_n}")
    df = get_data_df(lang, geo, start_date, end_date)
    if isinstance(metric, int):
        freq_df = data2freq(df, metric, top_n)
    elif metric == 'h':
        freq_df = data2hashtags(df, top_n)
    elif metric == 'u':
        raise ValueError("users not supported currently")

    return freq_df

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
    nlp.add_argument('-file')
    nlp.set_defaults(func=handle_nlp)

    # if want same day, just give same day twice
    # ask for days=6 because of subtract one (7-1) before you go rule
    query = subparsers.add_parser("query")
    query.add_argument(
        '-date',
        default=[datetime.today() - timedelta(days=6), datetime.today()],
        nargs=2, type=date_type)
    query.add_argument('-lang', default=LANG_OPS,
                       choices=LANG_OPS, nargs='+')
    query.add_argument('-geo', default=GEO_OPS,
                       choices=GEO_OPS, nargs='+')
    query.set_defaults(func=handle_query)

    args = parser.parse_args()
    print(args)
    args.func(args)
