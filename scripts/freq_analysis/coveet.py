import argparse
import pymysql
from datetime import datetime, timedelta
import sys
from tqdm import tqdm
from pprint import pprint
from os import path
import requests
import pickle
import json
import pandas as pd
from collections import Counter

import metrics

"""
integer means an n-gram
h: (h)ashtag frequency
u: top (u)sers
t: how many results to fetch
"""
METRIC_OPS = ["w", "b", "t", "h", "u"]
# language options: english and spanish only
LANG_OPS = ['en', 'es']
# geography options: florida, argentina, columbia, ecuador, spain,
# mexico, peru
GEO_OPS = ['fl', 'ar', 'co', 'ec', 'es', 'mx', 'pe']
# format of datetimes in the database
DB_TIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"
# DB_TIME_FORMAT = "%Y%m%d"
DEFAULT_FILE = "query.data"
# file that contains user information for database connection
# (too sensitive to keep in a source code file)
SETTINGS_FILE = "settings.json"

with open(SETTINGS_FILE, 'r') as f:
    user_json = json.load(f)

HOSTNAME = user_json["hostname"]
USERNAME = user_json["username"]
PASSWORD = user_json["password"]
DATABASE = user_json["database"]

QUERY_FORMAT = "SELECT t.text, dq.date, dq.qid, u.userid, um.screen_name\n \
                FROM tweets as t, datasetsbyqueries as dq, users as u, users_meta as um\n \
                WHERE t.tid=dq.tid AND t.tid=u.tid AND u.userid = um.user_id AND\n \
                dq.qid IN ({}) AND\n \
                dq.date BETWEEN '{}' AND '{}';"

UNIX_EPOCH_DATE = datetime(year=1970, month=1, day=1)

LOC_TO_QID = {('fl', 'es'): 1,
              ('fl', 'en'): 2,
              ('ar', 'es'): 3,
              ('mx', 'es'): 4,
              ('co', 'es'): 5,
              ('pe', 'es'): 6,
              ('ec', 'es'): 7,
              ('es', 'es'): 8}
QID_TO_LOC = {v: k for k, v in LOC_TO_QID}

def format_query(lang, geo, start_date, end_date):
    qids = []
    geos = [g for g in geo if g != 'fl']
    # if you have spanish, do all the countries that have spanish
    if 'es' in lang:
        for g in geos:
            # gives all the qid's we are looking for
            qids.append(LOC_TO_QID[(g, 'es')])
    if 'fl' in geo:
        for l in lang:
            qids.append(LOC_TO_QID[('fl', l)])
    qids = [f"'{q}'" for q in qids]

    start_date_sec = int((start_date - UNIX_EPOCH_DATE).total_seconds())
    end_date_sec = int((end_date - UNIX_EPOCH_DATE).total_seconds())
    return QUERY_FORMAT.format(', '.join(qids), start_date_sec, end_date_sec)

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


def day_to_row(lang, geo, date, metric, top_n):
    # metric: 1, 2, 3, u, h
    # get all data occuring in one day
    print(f"querying date {date} with lang={lang}, loc={geo}")
    sql = format_query(lang, geo, date, date + timedelta(days=1))
    with pymysql.connect(host=HOSTNAME,
                         user=USERNAME,
                         password=PASSWORD,
                         db=DATABASE) as cursor:
        cursor.execute(sql)
        tweet_tuples = cursor.fetchall()

    tweets_main_text = [t[0] for t in tweet_tuples]
    users = [t[4] for t in tweet_tuples]
    if isinstance(metric, int):
        print(f"getting ngrams n={metric}")
        tuples = metrics.ngrams(tweets_main_text, metric)
    elif metric == 'users':
        print("getting top users")
        tuples = Counter(users).most_common()
    elif metric == 'hashtags':
        print("getting top hashtags")
        tuples = metrics.hashtags(tweets_main_text)
    else:
        raise ValueError("something bad happened")

    if len(tuples) > top_n:
        tuples = tuples[:top_n]

    df = pd.DataFrame([])
    for t, freq in tuples:
        df[str(t)] = [freq]
    df['date'] = date
    return df

def days_to_df(lang, geo, start_date, end_date, metric=1, top_n=10):
    """
    note that the dates are inclusive
    may want to save the result of this function if big query
    """
    current_date = start_date
    df = pd.DataFrame([])
    while current_date <= end_date:
        row = day_to_row(lang, geo, current_date, metric, top_n)
        df = pd.concat([df, row], axis=0, sort=False, ignore_index=True)
        df.fillna(0, inplace=True)
        current_date += timedelta(days=1)
    return df

def handle_query(args):
    # Open database connection
    args.lang = list(set(args.lang))
    args.geo = list(set(args.geo))

    sql = format_query(args.lang, args.geo, args.date[0], args.date[1])
    # print(sql)
    with pymysql.connect(host=HOSTNAME,
                         user=USERNAME,
                         password=PASSWORD,
                         db=DATABASE) as cursor:
        cursor.execute(sql)
        tweet_tuples = cursor.fetchall()
        print(f"{len(tweet_tuples)} tweets found")
        with open(args.file, 'wb') as f:
            pickle.dump(tweet_tuples, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"wrote to {args.file}")


def handle_metrics(args):
    if not path.exists(args.file):
        raise FileNotFoundError(f"{args.file} does not exist!")
    with open(args.file, 'rb') as f:
        tweet_tuples = pickle.load(f)
    args.ngram = list(set(args.ngram))
    tweets_main_text = [t[0] for t in tweet_tuples]
    users = [t[4] for t in tweet_tuples]
    for n in args.ngram:
        print(metrics.ngrams(tweets_main_text, n)[:args.top])
    if args.users:
        print(Counter(users).most_common(args.top))
    if args.hashtags:
        print(metrics.hashtags(tweets_main_text)[:args.top])



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='a very basic interface to the digital narratives database',
        allow_abbrev=True)
    subparsers = parser.add_subparsers()
    query = subparsers.add_parser("query")
    nlp = subparsers.add_parser("nlp")
    nlp.add_argument('-top', default=50, type=int)
    nlp.add_argument('-users', action='store_true', default=False)
    nlp.add_argument('-hashtags', action='store_true', default=False)
    nlp.add_argument('-ngram', default=[], nargs='+', type=int)
    #nlp.add_argument(
    #    '-metric', default=METRIC_OPS[:1], choices=METRIC_OPS, nargs='+')
    nlp.add_argument('-file', default=DEFAULT_FILE)
    nlp.set_defaults(func=handle_metrics)

    # if want same day, just give same day twice
    # ask for days=6 because of subtract one (7-1) before you go rule
    query.add_argument(
        '-date',
        default=[datetime.today() - timedelta(days=6), datetime.today()],
        nargs=2, type=date_type)
    query.add_argument('-lang', default=LANG_OPS,
                                  choices=LANG_OPS, nargs='+')
    query.add_argument('-geo', default=GEO_OPS,
                                 choices=GEO_OPS, nargs='+')
    # TODO never implemented
    query.add_argument('-number', default=500, type=pos_type)
    query.add_argument('-file', default=DEFAULT_FILE)
    query.set_defaults(func=handle_query)
    # parser.add_argument('-update', action='store_true', default=False)

    args = parser.parse_args()
    print(args)
    args.func(args)

