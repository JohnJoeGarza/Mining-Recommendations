# Mining-Recommendations
Project that uses different mining formulas to find relationships in the data of users and ratings to provide recommendations of different products such as movies and music. 

#### MovieRecommender.py
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
