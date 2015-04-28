import os
import subprocess
import pydoop.hdfs as hdfs
import json
import requests

def solr_post(json_line, rdd_num):
  image = json.loads(json_line)
  json_dict = {'add':{'doc':{'label_i':image['label'], 
                             'rdd_num_i':rdd_num,
                             'data':json.dumps(image['data'], separators=(',',':')), 
                             'num_tree_i':image['num_trees']}, 'commitWithin':1000}}
  r = requests.post("http://192.155.209.244:8983/solr/TinyImages_shard1_replica1/update?wt=json",
    headers={'Content-type':'application/json'},
    data=json.dumps(json_dict))

for i in range(0, 4000):
  infile = sc.textFile('/user/admin/output10RDD/rdd%d' % (i))
  infile.foreach(lambda l: solr_post(l,i))
  print 'Completed file rdd%d' % (i)
