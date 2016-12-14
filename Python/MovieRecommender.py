# -*- coding: utf-8 -*-
"""
@author: johnj
"""
import unicodecsv
from math import sqrt
import pandas as pd

def read_csv(filename):
    ''' read csv files into dictionaries into a list '''
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)
        
def parse_maybe_float(i):
    '''Converts a float to a string, checks if string is empty as well'''
    if i != '':
        return float(i)
    else:
        return ''
#------------------------------------------------------------------------------
#Start MovieRecommender Class
class MovieRecommender:
    def __init__(self, data, k=1, metric = 'pearson', n = 5):
        '''Initialize MovieRecommender
        Data will be loaded in from a .csv file upon initalization
        param k is the k value for kth nearest neighbor
        param metric is which distance formula to use
        param n is the maximum number of recommendations to make
        note: instance of class should call the cleanData method in order to 
        correctly use the other methods to recommend a movie'''
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        self.data = read_csv(data)
        self.metric = metric
        self.fn = self.pearson
        if self.metric == 'pearson' :
            self.fn = self.pearson
        elif self.metric == 'manhattan':
            self.fn = self.manhattan
        elif self.metric == 'euclidean':
            self.fn = self.euclidean
    
    def cleanData(self):
        '''Cleans the current data so that it works correctly with the
        methods to recommend a movie'''
        myUsers = {}        
        for row in self.data:
            currentMovie = row['Movie']
            for item in row:
                if item == 'Movie' or row[item] == '':
                    continue
                elif item in myUsers:
                    currentRatings = myUsers[item]
                else:
                    currentRatings = {}
                currentRatings[currentMovie] = parse_maybe_float(row[item])
                myUsers[item] = currentRatings
        self.data = myUsers
        
    def convertProductID2name(self, id):
        '''Given product id number return product name'''
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id
                
    def userRatings(self,id,n):
        '''Return n top ratings for user with id'''
        print("Ratings for " + self.userid2name[id])
            
        
    def manhattan(self, rating1, rating2):
        '''Computes the Manhattan distance for both rating1 and rating2
        which are dictionaries.'''
        distance = 0
        for key in rating1:
            if key in rating2:
                distance += abs(rating1[key] - rating2[key])
        return distance
                
    def euclidean(self, rating1, rating2):
        '''Computes the distance of two neighbors using euclidean
        distance metric'''
        commonRatings = False
        distance = 0
        for key in rating1:
            if key in rating2:
                distance += (rating1[key] - rating2[key])**(2)
                commonRatings = True
        if commonRatings:
            return distance**(1/2)
        else:
            return 0
    
    def pearson(self, rating1, rating2):
        '''Calculates the approximation to the pearson correlation coefficient
        between rating1 and rating2 which are both dictionaries.
        Refer to the pearson formula for clarification of the method.'''
        sumXY = 0
        sumX = 0
        sumY = 0
        sumX2 = 0
        sumY2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sumXY += x * y
                sumX += x
                sumY += y
                sumX2 += pow(x, 2)
                sumY2 += pow(y, 2)
        if n == 0:
            return 0
            
        denominator = (sqrt(sumX2 - pow(sumX,2)/n)
                    * sqrt(sumY2 - pow(sumY, 2)/n))
        if denominator == 0:
            return 0
        else:
            return (sumXY - (sumX * sumY) / n) / denominator

    def computeNearestNeighbor(self, username):
        '''Creates a sorted list of users based on their distance to 
        username'''
        distances = []
        for instance in self.data:
            if instance != username:
                distance = self.fn(self.data[username], self.data[instance])
                distances.append((instance, distance))
        #Pearson requires greater numbers while euclidean and manhattan require
        #smaller numbers.
        if self.metric == 'pearson':
            distances.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        elif self.metric == 'manhattan' or self.metric == 'euclidean':
            distances.sort(key=lambda artistTuple: artistTuple[1], reverse = False)
        return distances
    
    def recommend(self, user):
        '''Creates a list of recommendations for the given user'''
        recommendations = {}
        nearest = self.computeNearestNeighbor(user)
        userRatings = self.data[user]
        totalDistance = 0.0
        
        for i in range(self.k):
            totalDistance += nearest [i][1]
        
        for i in range(self.k):
            weight = nearest[i][1] / totalDistance
            name = nearest[i][0]
            neighborRatings = self.data[name]

            for artist in neighborRatings:
                if not artist in userRatings:
                    if artist not in recommendations:
                        recommendations[artist] = (neighborRatings[artist] * weight)
                    else:
                        recommendations[artist] = (recommendations[artist] +
                            neighborRatings[artist] * weight)
                

        recommendations = list(recommendations.items())
        recommendations = [(self.convertProductID2name(k), round(v,2)) for (k, v) in recommendations]
        recommendations.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        
        return recommendations[:self.n]


    def recommenderTable(self, username):
        '''Creates a table of recommendations for readability'''
        titles = []
        ratings = []
        aList = self.recommend(username)

        for recommend in aList:
            titles.append(recommend[0])
            ratings.append(recommend[1])
        dataTable = pd.DataFrame({'Title':titles, 'Rating': ratings})
        dataTable = dataTable.reindex(columns = ['Title', 'Rating'])
        return dataTable.set_index('Title')
        
    def changeMetric(self, metric):
        '''Changes the metric and updates self.fn'''
        self.metric = metric
        if self.metric == 'pearson' :
            self.fn = self.pearson
        elif self.metric == 'manhattan':
            self.fn = self.manhattan
        elif self.metric == 'euclidean':
            self.fn = self.euclidean
        
    @property
    def metric(self):
        return self.__metric
        
    @metric.setter
    def metric(self, metric):
        if metric == 'manhattan':
            self.__metric = metric
        elif metric == 'euclidean':
            self.__metric = metric
        else:
            print('Pearson Default set')
            self.__metric = 'pearson'   
#End of MovieRecommender Class
#------------------------------------------------------------------------------
