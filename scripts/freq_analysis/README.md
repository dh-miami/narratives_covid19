# coveet: frequency analysis tool [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dh-miami/narratives_covid19/master)

`coveet` is a Python application to interface with the digital narratives database
API for querying basic statistics and NLP information like word frequencies, bigrams,
trigrams, top users, etc.

```
usage: coveet.py [-h] {query,nlp} ...

a very basic interface to the digital narratives database API

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
                       [-stopwords STOPWORDS [STOPWORDS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -date DATE DATE
  -lang {en,es} [{en,es} ...]
  -geo {fl,ar,co,ec,es,mx,pe} [{fl,ar,co,ec,es,mx,pe} ...]
  -stopwords STOPWORDS [STOPWORDS ...]
```

* `-h` to display the help menu.
* `-date <from_day> <to_day>` queries the database for all tweets with dates between `from_day` and `to_day` (inclusive), where dates are given as `yyyy-mm-dd`.
* `-lang` queries the database based on language criteria. Only two languages are supported here, `en` for English and `es` for Spanish. Both can be provided at once if the user wishes to query for tweets in both languages at once.
* `-geo` queries the database based on geographic location criteria. The following locations are supported: `fl` for Miami and South Florida, `ar` for Argentina, `co` for Columbia, `ec` for Ecuador, `es` for Spain, `mx` for Mexico, and `pe` for Peru. Many locations can be provided at once.
* `-stopwords` for supplying a list of filenames containing stopwords. Each word is given on a new line and comments can be specified using `//`. A sample stopwords
file has the following format:

```
// i
me
// this is a comment
my
myself
```

The results are written to a CSV file with form `dhcovid_yyyy-mm-dd_to_yyyy_mm-dd_lang_geo.csv`, based on the query given. CSV files can be read in using Excel or via pandas with `read_csv()`.

The `nlp` function has the following options:

```
usage: coveet.py nlp [-h] [-top TOP] [-ngram NGRAM] [-users] [-hashtags]
                     [-file FILE]

optional arguments:
  -h, --help    show this help message and exit
  -top TOP
  -ngram NGRAM
  -users
  -hashtags
  -mutex
  -file FILE
```

* `-h` to display the help menu.
* `-top <n>` to fetch only the top `n` results.
* `-ngram <num>` to query for n-grams where n is given by `num`. Multiple n-grams can be given at once.
* `-consecutive` will retrieve n-grams based on its formal definition. By default, false.
* `-users` to query for top users.
* `-hashtags` to query for hashtags.
* `-mutex` is a preprocessing setting to filter out words/hashtags that are not unique to a location-language pair. For example, for an input file that contains information about `mx-es`, `es-es`, and `fl-es`, `mx-es` rows will be filtered to contain words/hashtags that are unique to that pair. Likewise for `es-es` and `fl-es`.
* `-file <file>` the file containing the results of the query to perform NLP analysis on.

## Prerequisites

A `requirements.txt` file is provided in this directory with the packages
you need to install. You can do the following at the prompt to install them:

```
$ pip3 install -r requirements.txt
```

## Example usage

Issue the following at the prompt to obtain `English` tweets written in `Florida` between the dates `May 8, 2020` and `May 9, 2020`. This assumes two stopwords files `stopwords_en.txt` and `stopwords_es.txt` are available (sample ones are provided in this directory).

```c
$ python3 coveet.py query -g fl -l en -d 2020-05-08 2020-05-09 -s stopwords_en.txt stopwords_es.txt
```

where the results are written to a CSV file. The following will return the top 10 words using the above queried results as input:

```
$ python3 coveet.py nlp -n 1 -t 10 -f dhcovid_2020-5-8_to_2020-5-9_en_fl.csv
```

The following results are produced using a pandas DataFrame. It is also saved to CSV file.

```
   us  responders  pandemic  may  new  frontline  people  ...  thank  coronavirus  cases  positive  get  like       date
0  84          60        57   53   53         44      44  ...     39            0      0         0    0     0 2020-05-08
1  36           0        28    0   43          0      33  ...      0           38     32        30   28    25 2020-05-09
```

