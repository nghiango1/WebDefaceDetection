import sys
import numpy
from sklearn import metrics
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def input_data(train_file_path, test_size):
	train_vector = []
	train_label = []
	lines = open(train_file_path,'r').read().split('\n')
	for line in lines:
		if line.__len__() > 0:
			data = line.split(',')
			try:
				train_vector += [[float(i[1:-1]) for i in data[:-1]]]
				train_label += [int(data[-1][1:-1])]
			except Exception as e:
				raise e
				pass
	X_train, X_test, y_train, y_test = train_test_split(train_vector,train_label ,test_size=test_size, random_state=42)
	return X_train, X_test, y_train, y_test 

def evaluate(actual, pred):
	m_precision = metrics.precision_score(actual, pred)
	m_recall = metrics.recall_score(actual, pred)
	m_acc = metrics.accuracy_score(actual, pred)
	print('	|precision:{0:.3f}'.format(m_precision))
	print('	|recall:{0:0.3f}'.format(m_recall))
	print('	|acc  :{0:0.3f}'.format(m_acc))
	TP, FP, TN, FN = perf_measure(actual, pred)
	print('	|FailAlarm:{0:0.3f}'.format(FP/(FP+TN)))
	test_size = actual.__len__()
	print('	|TP:{0} FP:{1} TN:{2} FN:{3}'.format(TP, FP, TN, FN))
	return [m_precision, m_recall, m_acc, FP/(FP+TN),TP, FP, TN, FN]
	
def perf_measure(y_actual, y_predict):
	TP = 0
	FP = 0
	TN = 0
	FN = 0
	for i in range(len(y_predict)): 
		if y_actual[i]==y_predict[i]==1: #actual == predict ==deface 
		   TP += 1
		if y_predict[i]==1 and y_actual[i]!=y_predict[i]: #actual == safe ; predict ==deface 
		   FP += 1
		if y_actual[i]==y_predict[i]==0: #actual == safe ; predict == safe 
		   TN += 1
		if y_predict[i]==0 and y_actual[i]!=y_predict[i]: #actual == deface ; predict == safe
		   FN += 1

	return(TP, FP, TN, FN)


def train_clf(X, y):
	clf = {}
	clf['RandomForest']	= RandomForestClassifier(n_estimators = 100).fit(X, y)
	clf['NaiveBayes'] = MultinomialNB().fit(X, y)
	return clf


def main():
	import os
	import csv
	
	path = os.path.abspath('tf_para_top_300')

	# fileNames = ['index.html','index_loaded.html','text_only_index_loaded.html.txt']
	# n_gram = [2,3]
	get_valid_file = list(filter(lambda k: not os.path.isdir(k), [i for i in os.listdir(path)]))
	for test_size in [0.25,0.5]:
		final = open('_'.join([str(test_size),'final.csv']),'w')
		csv_writer = csv.writer(final, 'unix', delimiter=',')
		csv_writer.writerow(['algorithm','name','n-gram','percision','recall','acc','FailAlarm','TP','FP','TN','FN'])
		for file in get_valid_file:
			print(file)
			X_train, X_test, y_train, y_test = input_data(os.path.join(path,file),test_size)
			clf = train_clf(numpy.asarray(X_train),numpy.asarray( y_train))
			for algorithm in ['RandomForest','NaiveBayes']:
				print(algorithm)
				pred = clf[algorithm].predict(numpy.asarray(X_test))
				fileName = '_'.join(file.split('_')[:-3])
				n_gram = file.split('_')[-3]
				csv_writer.writerow([algorithm,fileName, n_gram]+evaluate(y_test, pred))
		final.close()

if __name__ == '__main__':
	main()
