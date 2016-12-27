# -*- coding: utf-8 -*-
"""
@author: johnjoegarza
"""
from math import sqrt
from math import isnan
from numpy import nan
import time
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
        self.frequencies = {}
        self.deviations = {}
        self.usersRatingAverages = {}
        self.simMatrix = {}
        if self.metric == 'pearson' :
            self.fn = self.pearson
        elif self.metric == 'manhattan':
            self.fn = self.manhattan
        elif self.metric == 'euclidean':
            self.fn = self.euclidean
            
        if type(data).__name__ == 'dict':
            self.data = data
            
    def computeDeviations(self):
        '''Create a deviation matrix that will be used for the slope one
        method.'''
        for ratings in self.data.values():
            for(item, rating) in ratings.items():
                self.frequencies.setdefault(item,{})
                self.deviations.setdefault(item,{})
                
                for(item2, rating2) in ratings.items():
                    if item != item2 and not isnan(rating) and not isnan(rating2):
                        self.frequencies[item].setdefault(item2, 0)
                        self.deviations[item].setdefault(item2, 0.0)
                        self.frequencies[item][item2] += 1
                        self.deviations[item][item2] += rating - rating2

        for (item, ratings) in self.deviations.items():
            for item2 in ratings:
                ratings[item2] /= self.frequencies[item][item2]

    def computeAverages(self):
        '''Computes the average rating of a user and stores it in a dictionary with their user id
        as the key'''
        n = 0
        ratingsSum = 0
        for (userID, ratings) in self.data.items():
            for (band, itemRating) in ratings.items():
                if not isnan(itemRating):
                    n+=1
                    ratingsSum += itemRating
            self.usersRatingAverages[userID] = float(ratingsSum/n)
            n = 0
            ratingsSum = 0

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
        
    def weightedSlopeOne(self, userRatings):
        '''Computes weighted Slope One of a user and returns a prediciton of 
        what a user may rate items they haven't rated yet. Only returns the top
        'n' items. 
        userRatings should be a dictionary of the form {'item': rating,...} which
        represents the items that one user has rated.
        self.computeDeviations() method should be called before this method is
        called or else this method will not work.'''
        recommendations = {}
        currentFreq = {}
        for(userItem, userRating) in userRatings.items():
            if not isnan(userRating ):
                for(diffItem, diffRatings) in self.deviations.items():
                    if (diffItem not in userRatings or isnan(userRatings[diffItem])) and userItem in self.deviations[diffItem]:
                        freq = self.frequencies[diffItem][userItem]
                        recommendations.setdefault(diffItem, 0.0)
                        currentFreq.setdefault(diffItem, 0)
                        
                        recommendations[diffItem] += (diffRatings[userItem] + userRating) * freq
                        currentFreq[diffItem] += freq

        recommendations = [(self.convertProductID2name(k),
                           v/currentFreq[k]) 
                            for (k, v) in recommendations.items()]

        recommendations.sort(key = lambda artistTuple: artistTuple[1],
                             reverse = True)
        
        return recommendations[:self.n]

    def slopeOneRecommenderTable(self, userRatings):
        '''Creates a table of recommendations based on weighted slope one 
        for readability'''
        titles = []
        ratings = []
        aList = self.weightedSlopeOne(userRatings)
        for recommend in aList:
            titles.append(recommend[0])
            ratings.append(recommend[1])
        dataTable = pd.DataFrame({'Title':titles, 'Rating': ratings})
        dataTable = dataTable.reindex(columns = ['Title', 'Rating'])
        return dataTable.set_index('Title')
        
    def cosineSimilarity(self, itemI, itemJ):
        '''Computes the cosine similarity of two items.
        itemI is an item in user ratings
        itemJ is an item in user ratings'''
        sumNumer = 0
        sumDenomRi = 0
        sumDenomRj = 0
        
        for (user, ratings) in self.data.items():
            if itemI in ratings and itemJ in ratings:
                if not (isnan(ratings[itemI]) or isnan(ratings[itemJ])):
                    userAverage = self.usersRatingAverages[user]
                    sumNumer += float((ratings[itemI] - userAverage) * (ratings[itemJ] - userAverage))
                    sumDenomRi += (ratings[itemI] - userAverage)**2
                    sumDenomRj += (ratings[itemJ] - userAverage)**2
        
        denom = sqrt(sumDenomRi) * sqrt(sumDenomRj)
                                   
        if denom == 0.0:
            return 0.0
        else:
            return sumNumer / (sqrt(sumDenomRi) * sqrt(sumDenomRj))
    
    def computeSimilarityMatrix(self):
        '''Populates a similarity matrix using cosine similarity based on the user data passed
        to the Recommender class.'''
        for ratings in self.data.values():
            for (itemI, ratingI) in ratings.items():
                self.simMatrix.setdefault(itemI, {})
                for(itemJ, ratingJ) in ratings.items():
                    if itemI != itemJ and not (isnan(ratingI) or isnan(ratingJ)):
                        self.simMatrix.setdefault(itemJ, {})
                        self.simMatrix[itemJ].setdefault(itemI, 0.0)
                        self.simMatrix[itemI].setdefault(itemJ, 0.0)
                        if self.simMatrix[itemJ][itemI] == 0.0:
                            self.simMatrix[itemI][itemJ] = self.cosineSimilarity(itemI, itemJ)
                        else:
                            self.simMatrix[itemI][itemJ] = self.simMatrix[itemJ][itemI]     
        #if item != item2 and not isnan(rating) and not isnan(rating2)
    
    def cosineSimPredict(self, userRatings):
        '''Predicts items a user may like based on a cosine similarity matrix
        user is the name of the user that we wish to predict recommendations for. '''
        minR = 1
        maxR = 5
        self.normalizeRuN(userRatings, minR, maxR)
        recommendations = {}
        denom = {}
        
        for(userItem, rating) in userRatings.items():
            if not isnan(rating):
                for(diffItem, diffRating) in self.simMatrix.items():
                    if (diffItem not in userRatings or isnan(userRatings[diffItem])) and userItem in self.simMatrix[diffItem]:
                        recommendations.setdefault(diffItem, 0.0)
                        denom.setdefault(diffItem, 0.0)
                        recommendations[diffItem] += self.simMatrix[diffItem][userItem] * rating
                        denom[diffItem] += abs(self.simMatrix[diffItem][userItem])
                        
        recommendations = [(self.convertProductID2name(key),
                           round(self.deNormSingle(value/denom[key], minR, maxR), 2)) for (key, value) in recommendations.items()]
                            
        recommendations.sort(key = lambda artistTuple: artistTuple[1],
                             reverse = True)        
        self.deNormalizeRuN(userRatings, minR, maxR)
        return recommendations[:self.n]

                            
    def cosineSimTable(self, userRatings):
        '''Creates a table of recommendations based on cosine similarity prediciton'''
        titles = []
        ratings = []
        aList = self.cosineSimPredict(userRatings)
        for recommend in aList:
            titles.append(recommend[0])
            ratings.append(recommend[1])
        dataTable = pd.DataFrame({'Title':titles, 'Rating': ratings})
        dataTable = dataTable.reindex(columns = ['Title', 'Rating'])
        return dataTable.set_index('Title')
        
    def normalizeRuN(self, nRatings, minR, maxR):
        '''Normalize R_u,N for use with prediction function.
        userRatings is the dictionary of user ratings to be normalized.
        minR and maxR are the min and max rating a user can give an item.'''
        for(item, rating) in nRatings.items():
            nRatings[item] = (2*(rating - minR) - (maxR - minR)) / (maxR - minR)
        return nRatings
    
    def deNormalizeRuN(self, nRatings, minR, maxR):
        '''deNormalize a normalized rating to be used with prediction function.
        nRuN is the dictionary of normalized values
        minR and maxR are the minimum and Maximum rating that a user can give an item.'''
        for(item, rating) in nRatings.items():
            nRatings[item] = 0.5 * ((rating + 1) * (maxR - minR)) + minR
        return nRatings
    
    def deNormSingle(self, rating, minR, maxR):
        '''De-Normalizes a single data value, to be used with cosineSimPredict method'''
        rating = 0.5 * ((rating + 1) * (maxR - minR)) + minR
        return rating
        
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

 