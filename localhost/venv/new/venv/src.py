#!/usr/bin/python

import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn import datasets
from sklearn import svm
from sklearn.model_selection import KFold
from sklearn import cross_validation as cv

def accuracy(predicted, observations):
    observationsDataframe = observations.copy()
    observationsArray = observationsDataframe.values

    TP = 0
    TN = 0
    FP = 0
    FN = 0

    #for pred, obs in zip(predicted, observationsArray):
        #print("Predicted - " + str(pred) + "___ Observed - " + str(obs))

    count = 0

    #(range(len(predicted)))
    #print("RESULTS:   ")
    error = 0
    for i in range(len(zip(predicted, observationsArray))):
        predictedItem = predicted[i]
        observedItem = observationsArray[i]
        individualError = abs(predictedItem - observedItem)
        #print(str(predictedItem) + "__" + str(observedItem) + "__" + str(individualError))
        error += individualError
        count += 1

    #result = float((TP + TN)) / float((TP + TN + FN + FP))
    #print(result)
    print(error/count)
    return (error/count)


def testModel(model, test, tLabel):
    testCopy = test.copy()
    testVals = testCopy.drop(tLabel, axis=1)

    predictedModel = model.predict(testVals)
    targetVals = testCopy[tLabel].copy()
    return accuracy(predictedModel, targetVals)

def trainData(dataFrame, tLabel):
    df = dataFrame.copy()
    training = df.drop(tLabel, axis=1)
    targetData = dataFrame[tLabel].copy()

    #print(training)
    #print(targetData)
    reg = linear_model.LinearRegression()
    reg.fit(training, targetData)
    print(reg.coef_)
    return reg

def crossValidation(dataFrame, splits, tLabel): #Definitely called correct number of times
    df = dataFrame.copy()
    kf = KFold(n_splits=splits)

    bestModel = 10
    count = 0
    for training, test in kf.split(df):
        count += 1
        trainingData = df.ix[training]
        testData = df.ix[test]
        #print(trainingData)
        model = trainData(trainingData, tLabel)
        result = testModel(model, testData, tLabel)

        #print(result)

        if (result < bestModel):
            bestModel = result
    print("NUMBER OF MODELS MADE " + str(count))
    return bestModel


def scaleData(dataFrame, tLabel):
    df = dataFrame.copy()
    df = df.drop(tLabel, axis=1)

    mean = df.mean(axis=0)
    stdVar = df.std(axis=0)

    df = df.sub(mean, axis=1)
    df = df / stdVar
    #print(df)
    return df


def orderData(dataFrame, col1, col2, col3):
    df = dataFrame.copy()
    for index, row in df.iterrows():
        col1Val = row[col1]
        col2Val = row[col2]
        col3Val = row[col3]

        if (col1Val == col2Val == col3Val):
            continue

        maxVal = max(col1Val, col2Val, col3Val)
        minVal = min(col1Val, col2Val, col3Val)
        middleVal = 0
        # print(str(minVal) + "___" + str(maxVal))
        if (col1Val == minVal or col1Val == maxVal):
            if (col2Val == maxVal or col2Val == minVal):
                middleVal = col3Val
            elif (col3Val == maxVal or col3Val == minVal):
                middleVal = col2Val
        elif (col3Val == minVal or col3Val == maxVal):
            if (col1Val == maxVal or col1Val == minVal):
                middleVal = col2Val
            elif (col2Val == maxVal or col2Val == minVal):
                middleVal = col1Val

        row[col1] = minVal
        row[col2] = middleVal
        row[col3] = maxVal
    return df


def main():
    tLabel = 'tna'
    probeAData = pd.read_csv('../probeA.csv')
    firstChemOrdered = orderData(probeAData, 'c1', 'c2', 'c3')
    secondChemOrdered = orderData(firstChemOrdered, 'm1', 'm2', 'm3')
    thirdChemOrdered = orderData(secondChemOrdered, 'n1', 'n2', 'n3')
    fourthChemOrdered = orderData(thirdChemOrdered, 'p1', 'p2', 'p3')

    probeAData = fourthChemOrdered.copy()
    probeAScaled = scaleData(probeAData, tLabel)
    probeAConcatenated = pd.concat([probeAData['tna'], probeAScaled], axis=1)
    probeATraining = probeAScaled.copy()

    splits = 10
    result = crossValidation(probeAConcatenated, splits, tLabel)
    print("BEST MODEL - " + str(result))
main()