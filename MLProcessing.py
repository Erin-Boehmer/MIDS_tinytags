import os
import numpy
import cPickle
import sys
import operator
import json

from pyspark import SparkConf, SparkContext
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import RandomForest, DecisionTreeModel
from pyspark.mllib.classification import SVMWithSGD

import pydoop.hdfs as hdfs

spark_home = os.environ.get('SPARK_HOME', None)

def _unpickle(file):
        fo = open(file, 'rb')
        dict = cPickle.load(fo)
        fo.close()
        return dict

def _loadtraindata():
        data = [_unpickle('/root/cifar-10-batches-py/data_batch_1'),
        _unpickle('/root/cifar-10-batches-py/data_batch_2'),
        _unpickle('/root/cifar-10-batches-py/data_batch_3'),
        _unpickle('/root/cifar-10-batches-py/data_batch_4'),
        _unpickle('/root/cifar-10-batches-py/data_batch_5')]
        
        trainingdata = []
        traininglabels = []

        for data_i in data:
        trainingdata = trainingdata + data_i['data'].tolist()
        traininglabels = traininglabels + data_i['labels']
        return trainingdata, traininglabels

def createTrainRDD():
        (trainingdata, traininglabels) = _loadtraindata()
        labeled = [(x, traininglabels[i]) for i,x in enumerate(trainingdata)]
        trainrdd = sc.parallelize(labeled)
        trainlprdd = trainrdd.map(lambda x: LabeledPoint(x[1], x[0]))
        return trainlprdd

def createRFModel():
        trainlprdd = createTrainRDD()
        model = RandomForest.trainClassifier(trainlprdd, numClasses=10, categoricalFeaturesInfo={},
                                                numTrees=10, featureSubsetStrategy="auto",
                                                impurity='gini', maxDepth=10, maxBins=50)
        return model

model = createRFModel()

def predict_proba(rf_model, testRDD):

        trees = rf_model._java_model.trees()
        ntrees = rf_model.numTrees()
        scores_dict = {i: 0 for i in range(0,10)}
        scoresRDD = testRDD.map(lambda x: scores_dict.copy())

        for tree in trees:
                dtm = DecisionTreeModel(tree)
                currentScoreRDD = dtm.predict(testRDD)
                scoresRDD = scoresRDD.zip(currentScoreRDD)

                def reduceTuple(x):
                        x[0][int(x[1])] += 1
                        return x[0]

                scoresRDD = scoresRDD.map(reduceTuple)
        return scoresRDD

def getClassifiedRDD(rdd_file):
        testdataRDD = sc.pickleFile(rdd_file)
        testimageRDD = testdataRDD.map(lambda x: numpy.fromstring(x, dtype='uint8').tolist())
        scoresRDD = predict_proba(model, testimageRDD)

        finalRDD = testimageRDD.zip(scoresRDD)

        def finalizeRDD(x):
                max_label = -1
                max_value = -1
                for k in x[1]:
                        if x[1][k] > max_value:
                                max_value = x[1][k]
                                max_label = k
                return {'data': x[0], 'label': max_label, 'num_trees': max_value}

        finalRDD = finalRDD.map(finalizeRDD)
        finalRDD = finalRDD.filter(lambda x: x['num_trees'] >= 4)
        return finalRDD

def saveOutputRDDs(start, end):
        for i in range(start, end):
                infile = '/user/admin/RDD/rdd%d' % (i)
                outfile = '/user/admin/outputRDD/rdd%d' % (i)
                outputRDD = getClassifiedRDD(infile)
                outputRDD = outputRDD.map(lambda x: json.dumps(x))
                outputRDD.saveAsTextFile(outfile)
                print 'Wrote %s' % outfile

saveOutputRDDs(0, 4000)
