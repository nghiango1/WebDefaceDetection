import os
# from sklearn.feature_extraction.text import CountVectorizer
import csv
from numpy import savetxt
from bs4 import BeautifulSoup

def get_valid_path(pages_path = ""):
	path = os.listdir()
	pages_path  = os.path.abspath(pages_path)
	valid_path = filter(lambda k: os.path.isdir(k), [os.path.join(pages_path,x) for x in os.listdir(pages_path)])
	valid_path = filter(lambda k: 'saved' in k, valid_path)
	n = []
	d = []
	for i in valid_path:
		if 'safe' in i: n += [i]
		else: d += [i] 

	for _normal_dirs in n:
		normal_valid_path = filter(lambda k: os.path.isdir(k), \
					[os.path.join(_normal_dirs,x) for x in os.listdir(_normal_dirs)])

	for _deface_dirs in d:
		deface_valid_path = filter(lambda k: os.path.isdir(k), \
					[os.path.join(_deface_dirs,x) for x in os.listdir(_deface_dirs)])
	return list(normal_valid_path),list(deface_valid_path)


def get_url(path):
	if not get_file(path,ARCHIVED_LOG): 
		print ('Error no ARCHIVED_LOG', path)
		return None
	file_path = get_file(path,ARCHIVED_LOG)
	f_input = open(file_path,'r', encoding='utf-8')
	reader = csv.DictReader(f_input)
	row_1 = reader.__next__()
	return(row_1['url'])

def get_file(path,name):
	files = name
	if not os.path.isdir(path):
		return None
	if os.path.exists(os.path.join(path,name)):
		return os.path.join(path,name)

def n_gram_counting(valid_path, fileName, n_gram):
	all_file_path = filter(lambda k: os.path.exists(k), \
					[os.path.join(path,fileName) for path in valid_path])
	result = {}
	for path in all_file_path:
		try:
			f_input = open(path,'r', encoding='utf-8')
			string = f_input.read()
		except Exception as e: 
			print('	|',path,e)
			continue
			
		# n_gram_matix = [string[i:i+n_gram] for i in range(0, len(string)- n_gram)]
		for i in [string[i:i+n_gram] for i in range(0, len(string)- n_gram)]:
			if not i in n_gram_matix:
				n_gram_matix += [i]
				
		for i in n_gram_matix:
			if i in result:
				result[i] += 1
			else:
				result[i] = 1
	return(result)

def getPureText(dom):
	soup = BeautifulSoup(dom, "html.parser")
	text = soup.getText()
	# for img in soup.findAll('img'):
		# text += img.get('alt','') + os.linesep
	return text

def tf_caculate(valid_path,fileName,n,n_gram_lists):
	
	all_file_path = filter(lambda k: os.path.exists(k), \
					[os.path.join(path,fileName) for path in valid_path])
	result = []
	for path in all_file_path:
		try:
			f_input = open(path,'r', encoding='utf-8')
			string = f_input.read()
		except Exception as e: 
			print('	|',path,e)
			print('		|',get_url(path))
			continue
		if tf_caculate_string:
			tf, max = tf_caculate_string(string,n,n_gram_lists)
			if max != 0:
				tf = [ i/max for i in tf]
				result += [tf]
		else:
			print (' |',path)
	return result
		
def tf_caculate_string(string,n,n_gram_lists, check=False):
		
	n_gram_matix = [string[i:i+n] for i in range(0, len(string)- n)]
	result = [0]*len(n_gram_lists)
	max = 0
	for n_gram in n_gram_matix:
		if n_gram in n_gram_lists:
			i = n_gram_lists.index(n_gram)
			result[i] += 1
			if result[i] > max:
					max = result[i]
	# if max == 0: return None
	# for i in range(n_gram_lists.__len__()):
		# result[i] = result[i]/max
	return result, max

def save_n_gram_count(N_GRAM_SAVE_PATH,sorted_keys,n_gram,filename):
	N_GRAM_COUNT_FILE_PATH = os.path.join(N_GRAM_SAVE_PATH,"_".join([filename,str(n_gram),'gram','count.csv']))
	N_GRAM_COUNT_FILE = open(N_GRAM_COUNT_FILE_PATH,'w',encoding = 'utf-8')
	N_GRAM_COUNT_FILE_writer = csv.writer(N_GRAM_COUNT_FILE, 'unix')
	for i in sorted_keys:
		N_GRAM_COUNT_FILE_writer.writerow([i[0],i[1]])
	N_GRAM_COUNT_FILE.close()
	
def save_n_gram_tf(TF_SAVE_PATH,rows,label, n_gram,filename, mode= 'w'):
	if rows.__len__() != label.__len__():
		return None
	TF_SAVE_FILE_PATH = os.path.join(TF_SAVE_PATH,"_".join([filename,str(n_gram),'gram','tf.csv']))
	TF_SAVE_FILE = open(TF_SAVE_FILE_PATH,mode,encoding = 'utf-8')
	TF_SAVE_FILE_writer = csv.writer(TF_SAVE_FILE, 'unix')
	for i in range(rows.__len__()):
		TF_SAVE_FILE_writer.writerow(rows[i]+[label[i]])
	TF_SAVE_FILE.close()
	
def open_n_gram_count(N_GRAM_SAVE_PATH,n_gram,filename):
	N_GRAM_COUNT_FILE_PATH = os.path.join(N_GRAM_SAVE_PATH,"_".join([filename,str(n_gram),'gram','count.csv']))
	if os.path.exists(N_GRAM_COUNT_FILE_PATH):
		result = []
		N_GRAM_COUNT_FILE = open(N_GRAM_COUNT_FILE_PATH,'r',encoding = 'utf-8')
		N_GRAM_COUNT_FILE_reader = csv.reader(N_GRAM_COUNT_FILE, 'unix')
		for row in N_GRAM_COUNT_FILE_reader:
			result += [row[0]]
		N_GRAM_COUNT_FILE.close()
		return result
	return None

def main():
	TF_SAVE_PATH = os.path.abspath('check-200-200')
	# TF_SAVE_PATH = os.path.join(TF_SAVE_PATH,"_".join(n_gram,'gram','tf.csv'))
	N_GRAM_SAVE_PATH = os.path.abspath('n_gram_count')
	n,d = get_valid_path()
	fileNames = ['text_only_index_loaded.html.txt','index_loaded.html','index.html']
	n_gram_tests = [2,3]
	for n_gram in n_gram_tests:
		for filename in fileNames:
			print("_".join([filename,str(n_gram),'gram','count.csv']))
			n_gram_lists = open_n_gram_count(N_GRAM_SAVE_PATH,n_gram,filename)[:300]
			
			if not n_gram_lists:
				n_gram_count_all = n_gram_counting(n+d, filename, n_gram)
				n_gram_count_all_sorted = sorted(n_gram_count_all.items() , reverse=True, key=lambda x: x[1])
				save_n_gram_count(N_GRAM_SAVE_PATH,n_gram_count_all_sorted,n_gram,filename)
				n_gram_lists = [i[0] for i in sorted_keys[:300]]
			
			normal_tf = tf_caculate(n,filename,n_gram,n_gram_lists)
			label = [0]* normal_tf.__len__()
			save_n_gram_tf(TF_SAVE_PATH, normal_tf ,label, n_gram,filename, 'w')
			deface_tf = tf_caculate(d,filename,n_gram,n_gram_lists)
			label = [1]* deface_tf.__len__()
			save_n_gram_tf(TF_SAVE_PATH, deface_tf ,label, n_gram,filename, 'a')
main()