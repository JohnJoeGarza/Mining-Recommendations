# Mining-Recommendations
Project that uses different mining formulas to find relationships in the data of users and ratings to provide recommendations of different products such as movies and music. 

##Python
####MovieRecommender.py
Recommends movies based on the current ratings of the users. The current metrics implemented are **Pearsons Correlations Coefficient approximation**, **Manhattan Distance**, and **Euclidean Distance**.

This class uses the *Movie_Ratings.csv* file which houses the data used to make recommendations. It should be noted that the data must be cleaned up in order to work properly with the methods of the MovieRecommender class. A cleanData() method has been created to do the cleaning. Example implementation is shown below.

```python
mr = MovieRecommender('Movie_Ratings.csv', 5, 'pearsons', 5)
mr.cleanData()

mr.recommenderTable('Josh')
```
The code above will produce the following recommendations for the users Josh based on his ratings.

|Title   |     Rating|
|:--------:|:-----------:|
|Old School          | 3.90|
|Dodgeball           | 3.05|
|Lord of the Rings   | 3.01|
|Braveheart          | 2.69|
|Napolean Dynamite   | 2.44|

####Recommender.py
Generalized recommender class similar to the MovieRecommender but the data wrangling and data scrubbing should happen outside of the class so the data parameter is a dictionary of the form {'Users' : {'ItemKey' : rating}}. Example implementation is shown below.
```python
import pandas as pd
myUsers = pd.read_csv('Band_Ratings.csv', index_col = 'Band').to_dict()
r = Recommender(myUsers, 3, 'pearson', 5)
r.recommenderTable('Hailey')
```
The Code will produce the following recommendations for the user Hailey based on her ratings.
                 
|Title           |  Rating |
|:--------------:|:--------:|
|Phoenix          |  5.00 |
|Blues Traveler   |  2.59 |
|Slightly Stoopid |  2.54 |

#####Weighted Slope One
The recommender class also contains a method to predict what a user may rate items that they haven't rated based on their ratings and the deviations of other ratings computed from the ratings of the users in the data. The .computeDeviations needs to be called before .weightedSlopeOne() method is called or the method will not work properly. It should be noted that the method handles NaN but it is more efficient to call the method without these types of values in the data. A example of data containing NaN values is shown below but it takes a while to run based on the .pickle file that has over 900 users that have rated over a thousand movies.
```python
myUsers = pd.read_pickle('L_MovieRatings.pickle').to_dict()
r = Recommender(myUsers)
r.computeDeviations() #Will take some time to run based on the size of L_MovieRatings.pickle
r.slopeOneRecommenderTable(myUsers['1'])
```
Which will result in the following table of predicitons that user '1' will rate items they haven't rated yet.

|Title                                            |  Rating  |
|:-----------------------------------------------:|:--------:|                                                      
|Entertaining Angels: The Dorothy Day Story (1996)|  6.375000|
|Aiqing wansui (1994)                             |  5.849057|
|Boys, Les (1997)                                 |  5.644970|
|Someone Else's America (1995)                    |  5.391304|
|Santa with Muscles (1996)                        |  5.380952|


The L_MovieRatings file is from the MovieLens data set that can be found at www.grouplens.org.

