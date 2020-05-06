This folder will contain a corpus related to Covid-19 tweets and it will be organized as follows: 

* By Language: English, Spanish
* By Day: January 20th - 
* By geolocation: US, Latin America, Spain
* By hashtags 

We have different queries running, which correspond to the datasets in our 'twitter-corpus' folder. 

1. General query for Spanish harvesting all tweets which contain hashtags and keywords: `covid`, `coronavirus`, `pandemia`, `quarentena`, `confinamiento`, `quedateencasa`, `desescalada`, `distanciamiento social`

2. Specific query for English in Miami and South Florida. The hashtags and keywords harvested are: `covid`, `coronavirus`, `pandemic`, `quarantine`, `stayathome`, `outbreak`, `lockdown`, `socialdistancing`. 

3. Specific queries for Spanish in Argentina, Mexico, Colombia, Perú, Ecuador, Spain, using the tweet geolocalization when possible and/or the user information.

The corpus of tweets consists of a list of Tweet Ids, that need to be treated with an "hydratator" in order to revocer all metadata. 


