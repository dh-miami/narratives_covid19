# coveet: database API + frequency analysis

`coveet` is a Python application to interface with the digital narratives database
for querying basic statistics and NLP information like word frequencies, bigrams,
trigrams, top users, etc. It also exposes a very basic API which returns a `pandas`
DataFrame object so that the results can be used in downstream experiments and analyses.

```
usage: coveet.py [-h] {query,nlp} ...

a very basic interface to the digital narratives database

positional arguments:
  {query,nlp}

optional arguments:
  -h, --help   show this help message and exit
```

Two modes are provided: `query` for querying the database according to some criteria, and `nlp` for executing basic NLP tasks.

The `query` function has the following options:

```
usage: coveet.py query [-h] [-date DATE DATE] [-lang {en,es} [{en,es} ...]]
                       [-geo {fl,ar,co,ec,es,mx,pe} [{fl,ar,co,ec,es,mx,pe} ...]]
                       [-number NUMBER] [-file FILE]

optional arguments:
  -h, --help            show this help message and exit
  -date DATE DATE
  -lang {en,es} [{en,es} ...]
  -geo {fl,ar,co,ec,es,mx,pe} [{fl,ar,co,ec,es,mx,pe} ...]
  -number NUMBER
  -file FILE
```

* `-h` to display the help menu.
* `-date <from_day> <to_day>` queries the database for all tweets with dates between `from_day` and `to_day` (inclusive), where dates are given as `yyyy-mm-dd`.
* `-lang` queries the database based on language criteria. Only two languages are supported here, `en` for English and `es` for Spanish. Both can be provided at once if the user wishes to query for tweets in both languages at once.
* `-geo` queries the database based on geographic location criteria. The following locations are supported: `fl` for Miami and South Florida, `ar` for Argentina, `co` for Columbia, `ec` for Ecuador, `es` for Spain, `mx` for Mexico, and `pe` for Peru. Many locations can be provided at once.
* `-number` specifies the number of results to fetch. Not supported currently.
* `-file <file_name>` dumps the results of the query into a file with name `file_name`. If not specified, the results are written to a default file named `query.data`.

The `nlp` function has the following options:

```
usage: coveet.py nlp [-h] [-top TOP] [-users] [-hashtags]
                     [-ngram NGRAM [NGRAM ...]] [-file FILE]

optional arguments:
  -h, --help            show this help message and exit
  -top TOP
  -users
  -hashtags
  -ngram NGRAM [NGRAM ...]
  -file FILE
```

* `-h` to display the help menu.
* `-top <n>` to fetch only the top `n` results.
* `-users` to query for top users.
* `-hashtags` to query for hashtags.
* `-ngram <num>` to query for n-grams where n is given by `num`. Multiple n-grams can be given at once.
* `-file <file>` the file containing the results of the query to perform NLP analysis on. If not specified, it tries using the default file named `query.data`.

## Prerequisites

Because Twitter data is sensitive, the database is not public access. You must provide the credentials given to you by filling in the `setting.json` file with that information. Please contact the DH@UM team for more details.

There may be some Python dependencies that are not available on your computer. Use `pip3` (or your Python package manager) to install them.

## Example usage

Issue the following at the prompt to obtain `English` tweets written in `Florida` between the dates `May 8, 2020` and `May 9, 2020`, and write the results to a file called `myquery.txt`:

```c
$ python3 coveet.py query -g fl -l en -d 2020-05-08 2020-05-09 -f myquery.txt
```

The following will return the top 10 words using the `myquery.txt` queried results as input:

```c
$ python3 coveet.py nlp -n 1 -t 10
```

The following results are produced:

```
[('covid', 723), ('responders', 61), ('us', 60), ('pandemic', 58), ('florida', 58), ('new', 56), ('may', 54), ('people', 51), ('workers', 45), ('frontline', 44)]
```

## API

`coveet` exposes an API for programatically querying the database and obtaining the results as a `pandas` DataFrame. The following will query all English tweets between April 27 and May 3 in Florida. It makes use of the `datetime` object from Python:

```python
start = datetime(year=2020, month=4, day=27) # start date
end = datetime(year=2020, month=5, day=3)    # end date
df = days_to_df(
     lang=['en'], geo=['fl'], start_date=start, end_date=end, metric=2, top_n=10)
# do stuff with df...
```

Each row corresponds to a day, and each column corresponds to a top word(s) or user.

