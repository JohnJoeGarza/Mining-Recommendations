# -*- coding: utf-8 -*-
"""
@author: johnjoegarza
"""
from math import sqrt
from math import isnan
import pandas as pd

#------------------------------------------------------------------------------
#Start of recommender class
class Recommender:
    def __init__(self, data, k=1, metric = 'pearson', n=5):
        '''Initialize MovieRecommender
        Data should be a dictionary of the form {'User' : {'ItemKey': rating}}
        param k is the k value for kth nearest neighbor
        param metric is which distance formula to use
        param n is the maximum number of recommendations to make
        '''
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        self.metric = metric
        if self.metric == 'pearson' :
            self.fn = self.pearson
        elif self.metric == 'manhattan':
            self.fn = self.manhattan
        elif self.metric == 'euclidean':
            self.fn = self.euclidean

        if type(data).__name__ == 'dict':
            self.data = data
        
    def convertProductID2name(self, id):
        '''Given product id number return product name'''
        if id in self.productid2name:
            return self.productid2name[id]
        else:
            return id
    
        
    def manhattan(self, rating1, rating2):
        '''Computes the Manhattan distance. Both rating1 and rating2
        are dictionaries.'''
        distance = 0
        for key in rating1:
            if isnan(rating1[key]) or isnan(rating2[key]):
                continue
            distance += abs(rating1[key] - rating2[key])
        return distance
                
    def euclidean(self, rating1, rating2):
        '''Computes the distance of two neighbors using euclidean
        distance metric'''
        commonRatings = False
        distance = 0
        for key in rating1:
            if isnan(rating1[key]) or isnan(rating2[key]):
                continue
            distance += (rating1[key] - rating2[key])**(2)
            commonRatings = True
        if commonRatings:
            return distance**(1/2)
        else:
            return 0 #The event that there are no ratings in common.
    
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
            if isnan(rating1[key]) or isnan(rating2[key]):
                continue
            n+= 1
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
                if isnan(neighborRatings[artist]):
                    continue
                if isnan(userRatings[artist]):
                    if artist not in recommendations:
                        recommendations[artist] = (neighborRatings[artist] * weight)
                    else:
                        recommendations[artist] = (recommendations[artist] +
                            neighborRatings[artist] * weight)
                

        recommendations = list(recommendations.items())
        recommendations = [(self.convertProductID2name(key), round(value,2)) 
                            for (key, value) in recommendations]
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
#End of Recommender class
#------------------------------------------------------------------------------        

