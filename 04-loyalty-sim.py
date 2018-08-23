import gensim 
from gensim import models, corpora,similarities
import jieba
import jieba.posseg as pseg 
import codecs 

def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r',encoding="utf-8").readlines()]  
    return stopwords  
stopwords = stopwordslist('stopwords.txt') 

#结巴分词后的停用词性 [标点符号、连词、助词、副词、介词、时语素、‘的’、数词、方位词、代词]
stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r']

def tokenization(files) :
	tokens=[]
	with open(files,"r",encoding="utf-8") as inputs:
		text=inputs.read()
		words=pseg.cut(text)
	for word, flag in words:
		if flag not in stop_flag and word not in stopwords:
			tokens.append(word)
	return tokens

###三个样本，第一个为相关度较高，第二个为相关度较低，第三个为干扰
files=['loyalsample01.txt','loyalsample02.txt','loyalsample03.txt']

corpus=[]
for each in files:
	corpus.append(tokenization(each))
print(len(corpus))

dictionary=corpora.Dictionary(corpus)
doc_vectors=[dictionary.doc2bow(text) for text in corpus]

###Build the query text
query=tokenization('loyalquery.txt')
query_bow=dictionary.doc2bow(query)


### to build tf-idf model and evaluate the simiality with query###
tfidf=models.TfidfModel(doc_vectors)
tfidf_vectors=tfidf[doc_vectors]
index=similarities.MatrixSimilarity(tfidf_vectors)
sim=index[query_bow]
print(list(enumerate(sim)),'\n')

#构建LSI模型，设置主题数为2（理论上这两个主题应该分别为党忠诚和干扰样本）
lsi=models.LsiModel(tfidf_vectors,id2word=dictionary,num_topics=2)
lsi_vector=lsi[tfidf_vectors]

for doc in lsi_vector:
	print(doc)
print('\n')

query_lsi=lsi[query_bow]
index = similarities.MatrixSimilarity(lsi_vector)
sims = index[query_lsi]
print (list(enumerate(sims)))

