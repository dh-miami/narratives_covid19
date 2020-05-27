# Travelog 

## Jerry Bonnell

### 4/26/20 (5 hours)

* Set up a Twitter developer account
* Reviewed the following books/tutorials on mining Twitter data: 
    - The Programming Historian's [Beginner's Guide to Twitter Data](https://programminghistorian.org/en/lessons/beginners-guide-to-twitter-data)
    - Marco Bonzanini's [Mining Twitter Data with Python](https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/)  
    - [Mining the Social Web](https://www.amazon.com/Mining-Social-Web-Facebook-Instagram-ebook/dp/B07L46FZ8Y/ref=sr_1_1?dchild=1&keywords=o+reiley+mining+the+social+web&qid=1588566463&sr=8-1) by Matthew A. Russell and Mikhail Klassen (Chapters 1 and 9)
    - Last two resources are nice for CS folks :-)

### 5/3/20 (4 hours)

* I am exploring the [Covid-19-TweetIDs](https://github.com/echen102/COVID-19-TweetIDs) dataset by Chen & Ferrara. 
    - Hydrating the Tweets is straightforward using Twarc and the Python script they have provided. 
    - However, there is a large volume of data in this dataset and they estimated approx. 25 hours to hydrate it all and *zipped* data size of 6.9GB. Definitely need to organize the data better for our research. See the TODO's for more on this. 
    - for some quick exploration, I focused on just one ID file, which corresponds to tweets collected during an hour on a given day.  
* Based on discussion from the [4/29](https://github.com/dh-miami/narratives_covid19/blob/master/travelogs/Minutes-04-29-2020.md) meeting, a preliminary task is to assess sentiment regarding Covid-19 with respect to different locations. 
    - Implemented the semantic orientation (unsupervised approach) defined in Bonzanini's tutorial. 
     
__TODO__ Evaluate the sentiment of select words, and apply on a dataset filtered for locations appropriate for our study.   

__TODO__ Working with Twitter data locally is infeasible. Will the database being built hold Twitter data from all the external datasets? What is the status of this database? Is this a component of my work?

__TODO__ Is there a server available that we can use to play around with the data? 

__TODO__ Need to refine further what kinds of computational studies will be conducted on the data.     

### 5/13/20 (2 hours)

* Successfully logged into Susanna's server and installed Python package manager `pip3`, 
and packages like `jupyter notebook`, `pandas`, `scikit-learn`, which we might need.
* Set up jupyter notebook so that we can run a jupyter notebook from the server, and open 
the notebook up in a browser on your local computer 
  - I make use of ssh tunneling to accomplish this. Can write a tutorial later.
  - I think this set-up is perfect for research purposes, but we may want an actual url
    that a user can follow to visit the notebooks.  

### 5/27/20 (8 hours)

* Begin work on frequency analysis Python tool, which interfaces directly with the database. 
This collection of scripts can be imported into a jupyter notebook later for obtaining
the top frequency lists, users, etc. 

## total hours: 19
