This folder contains a corpus related to Covid-19 tweets and it is organized as follows: 

* By Language: English, Spanish
* By Day: January 20th - 
* By geolocation: US, Latin America, Spain
* By hashtags 

We have different queries running, which correspond to the datasets in our 'twitter-corpus' folder. 

1. General query for Spanish harvesting all tweets which contain hashtags and keywords: `covid`, `coronavirus`, `pandemia`, `quarentena`, `confinamiento`, `quedateencasa`, `desescalada`, `distanciamiento social`

2. Specific query for English in Miami and South Florida. The hashtags and keywords harvested are: `covid`, `coronavirus`, `pandemic`, `quarantine`, `stayathome`, `outbreak`, `lockdown`, `socialdistancing`. 

3. Specific queries for Spanish in Argentina, Mexico, Colombia, Perú, Ecuador, Spain, using the tweet geolocalization when possible and/or the user information.

Folders are organized by day; in each day-folder you will find 9 different files: 

* `dhcovid_YEAR-MONTH-DAY_en_fl.txt` We are gathering only tweets in English that refer to the area of Miami and South Florida. The reason behind this choice is that there are multiple projects harvesting English data, and, our project is particulary interested in this area because of our home institution (University of Miami) and because we aim to study public conversations from a bilingual (EN/ES) point of view. 
* `dhcovid_YEAR-MONTH-DAY_es_fl.txt`: Dataset containing tweets geolocalized (by georeferences, by place, or by user) in South Florida.
* `dhcovid_2020-04-24_es.txt` This datasets contains all tweets in Spanish, regardless its geolocation. 
* `dhcovid_YEAR-MONTH-DAY_es_ar.txt`: Dataset containing tweets geolocalized (by georeferences, by place, or by user) in Argentina. 
* `dhcovid_YEAR-MONTH-DAY_es_co.txt`: Dataset containing tweets geolocalized (by georeferences, by place, or by user) in Argentina. 
* `dhcovid_YEAR-MONTH-DAY_es_ec.txt`: Dataset containing tweets geolocalized (by georeferences, by place, or by user) in Ecuador. 
* `dhcovid_YEAR-MONTH-DAY_es_es.txt`: Dataset containing tweets geolocalized (by georeferences, by place, or by user) in Spain.  
* `dhcovid_YEAR-MONTH-DAY_es_mx.txt`: Dataset containing tweets geolocalized (by georeferences, by place, or by user) in Mexico. 	
* `dhcovid_YEAR-MONTH-DAY_es_pe.txt`: Dataset containing tweets geolocalized (by georeferences, by place, or by user) in Perú. 

The corpus of tweets consists of a list of Tweet Ids, that need to be treated with an "hydratator" in order to revocer all metadata. 

We started collecting our dataset on April 24th 2020. For prior dates (January - April 24th), we will use the [PanaceaLab dataset](https://github.com/thepanacealab/covid19_twitter), since it is one of the few that collects data in all languages.

A first version of this dataset is published in Zenodo: 

Susanna Allés Torrent, Gimena del Rio Riande, Nidia Hernández, Jerry Bonnell, & Dieyun Song. (2020). Digital Narratives of Covid-19: a Twitter Dataset (Version 1.0) [Data set]. Zenodo. http://doi.org/10.5281/zenodo.3824950 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3824950.svg)](https://doi.org/10.5281/zenodo.3824950)
