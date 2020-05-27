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

from metrics import ngrams

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
TMP_FILE = "data.tmp"
# file that contains user information for database connection
# (too sensitive to keep in a source code file)
SETTINGS_FILE = "my_settings.json"

with open(SETTINGS_FILE, 'r') as f:
    user_json = json.load(f)

HOSTNAME = user_json["hostname"]
USERNAME = user_json["username"]
PASSWORD = user_json["password"]
DATABASE = user_json["database"]

QUERY_FORMAT = "SELECT t.text, dq.date, dq.qid, u.userid\n \
                FROM tweets as t, datasetsbyqueries as dq, users as u\n \
                WHERE t.tid=dq.tid AND t.tid=u.tid AND\n \
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

# def format_query(args):
#     country_codes = ', '.join(
#         [f"'{g.upper()}'" for g in args.geo if g != 'fl'])
#     place_full_name = '% FL' if 'fl' in args.geo else '%'
#     lang = ', '.join([f"'{l}'" for l in args.lang])
#     start_date = int(args.date[0].total_seconds())
#     end_date = int(args.date[1].total_seconds())
#     return QUERY_FORMAT.format(
#         country_codes, place_full_name, lang, start_date, end_date)

def format_query(args):
    qids = []
    geos = [g for g in args.geo if g != 'fl']
    # if you have spanish, do all the countries that have spanish
    if 'es' in args.lang:
        for g in geos:
            # gives all the qid's we are looking for
            qids.append(LOC_TO_QID[(g, 'es')])
    if 'fl' in args.geo:
        for l in args.lang:
            qids.append(LOC_TO_QID[('fl', l)])
    qids = [f"'{q}'" for q in qids]

    start_date = int((args.date[0] - UNIX_EPOCH_DATE).total_seconds())
    end_date = int((args.date[1] - UNIX_EPOCH_DATE).total_seconds())
    return QUERY_FORMAT.format(', '.join(qids), start_date, end_date)

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
    # Open database connection
    args.lang = list(set(args.lang))
    args.geo = list(set(args.geo))

    sql = format_query(args)
    # print(sql)
    with pymysql.connect(host=HOSTNAME,
                         user=USERNAME,
                         password=PASSWORD,
                         db=DATABASE) as cursor:
        cursor.execute(sql)
        tweet_tuples = cursor.fetchall()
        print(f"{len(tweet_tuples)} tweets found")
        with open(TMP_FILE, 'wb') as f:
            pickle.dump(tweet_tuples, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"wrote to {TMP_FILE}")


def handle_metrics(args):
    args.metric = list(set(args.metric))
    if not path.exists(TMP_FILE):
        # TODO issue a query
        pass
    with open(TMP_FILE, 'rb') as f:
        tweet_tuples = pickle.load(f)
    tweets_main_text = [t[0] for t in tweet_tuples]
    print(ngrams(tweets_main_text))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='coveet', allow_abbrev=True)
    subparsers = parser.add_subparsers()
    query = subparsers.add_parser("query")
    ml = subparsers.add_parser("ml")

    ml.add_argument(
        '-metric', default=METRIC_OPS[:1], choices=METRIC_OPS, nargs='+')
    ml.set_defaults(func=handle_metrics)
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
    query.set_defaults(func=handle_query)
    # parser.add_argument('-update', action='store_true', default=False)

    args = parser.parse_args()
    print(args)
    args.func(args)

