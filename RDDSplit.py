#pydoop requires setting path to HADOOP_HOME and javac

import os
import numpy
from pyspark import SparkConf, SparkContext
import pydoop.hdfs as hdfs

spark_home = os.environ.get('SPARK_HOME', None)

for i in range(0, 80):
	infile = '/user/admin/%sm_%sm.bin' % (str(i), str(i + 1))
	f = hdfs.open(infile)
	byte_count = 32 * 32 * 3
	total_bytes = f.size
	for j in range(0,50):
		images = []
		if i*50+j <= 1809:
			continue
		for k in range(0,total_bytes/byte_count/50):
			data = f.read(byte_count)
			images.append(data)
		rdd = sc.parallelize(images)
		outfile = '/user/admin/RDD/rdd%s' % str(i*50+j)
		print 'Writing %s from %s' % (outfile, infile)
		rdd.saveAsPickleFile(outfile)
		print 'Wrote %s' % outfile
