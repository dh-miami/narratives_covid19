# Twitter Dataset and Hydratator

To be discussed April 27th, 2020 & You can add comments, troubles, and useful indications.

## Apply for a Twitter developer account

Otherwise you won't be able to recover the tweets. Here is the link <https://developer.twitter.com/en/apply-for-access>. If you have already a Twitter account it won't take long.

Description of the use of Twitter data for research: <https://developer.twitter.com/en/use-cases/academic-researchers>
Twitter's goal is to: "Learn about public conversation"

## Twitter datasets 

As we discussed, let's all start by familiarizing with a Twitter dataset. Please read, [this blog post](https://covid.dh.miami.edu/2020/04/23/mining-twitter-and-covid-19-datasets/) that I wrote and visit all different datasets to give you an idea of what we will be doing. All four datasets are very interesting, specially these two: 

* [Covid-19 Twitter chatter dataset for scientific use](Covid-19 Twitter chatter dataset for scientific use) (Panacea Lab).
   * They start their corpus on January 1st, 2020. 
   * They collect English, Spanish, French
   * They structure the dataset in folders by day, eachone containing a csv file: 
    - 2 version: 1 clean version of tweets (clean-dataset.tsv.gz), and a version with tweets and retweets (dataset.tsv.gz)
    - By using NPL they built a dataset of the 1000 frequent words, bigrams, and trigrams.
* [COVID-19-TweetIDs](https://github.com/echen102/COVID-19-TweetIDs) (Chen & Ferrara)
  * They start their corpus on January 21th
  * Only in English
  * They structure the dataset in files .txt per hour (year-month-date-hour). 
  * Check their list of [keywords](https://github.com/echen102/COVID-19-TweetIDs/blob/master/keywords.txt)

I propose to start working with the Panacea Lab: <https://github.com/thepanacealab/covid19_twitter/tree/master/dailies> Download the file [full_dataset-clean.tsv.gz](https://zenodo.org/record/3757272/files/full_dataset-clean.tsv.gz?download=1) in Zenodo that contains the last version released.

## Hydratate 

There are different tools to hydratate tweets, and that the two best known are [Hydratator](https://github.com/DocNow/hydrator) and [Twarc](https://github.com/DocNow/twarc)

We are going to use Hydrator for now because it seems easier and has a GUI. 

Follow the instructions to install it: https://github.com/DocNow/hydrator 

Also, we recommend that you follow the Lesson from the programming historian: Brad Rittenhouse, Ximin Mi, and Courtney Allen, "Beginner's Guide to Twitter Data," The Programming Historian 8 (2019), <https://programminghistorian.org/en/lessons/beginners-guide-to-twitter-data> 

# Questions
- Dieyun started drafting a [list of question](https://github.com/dh-miami/narratives_covid19/blob/master/twitter-corpus/questions.md). Let's modify this list begining with simple questions and keep adding more. 


