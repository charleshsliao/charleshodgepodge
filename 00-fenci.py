# -*- coding: utf-8 -*-

from collections import Counter  
import jieba  
import jieba.posseg as pseg
import multiprocessing
import gensim
from gensim.models import word2vec
import re
  
# 创建停用词list  
def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r',encoding="utf-8").readlines()]  
    return stopwords  
  
  
# 对句子进行分词  
def seg_sentence(sentence):  
    sentenec=re.sub(r'\s{2,}', '', sentence) #去除两个空格
    #结巴分词后的停用词性 [标点符号、连词、助词、副词、介词、时语素、‘的’、数词、方位词、代词],并去除
    stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r']
    sentence_seged = pseg.cut(sentence.strip())  
    stopwords = stopwordslist('stopwords.txt')  # 这里加载停用词的路径  

    outstr = ''  
    for word,flag in sentence_seged:  
        if word not in stopwords and flag not in stop_flag:  
            if word != '\t':
                outstr += word
                outstr += " "  
    return outstr  
  
  
inputs = open('ludingji.txt', 'r',encoding="utf-8") #加载要处理的文件的路径  
outputs = open('words.txt', 'w',encoding="utf-8") #加载处理后的文件路径  
for line in inputs:  
    line_seg = seg_sentence(line)  # 这里的返回值是字符串  
    outputs.write(line_seg)  
outputs.close()  
inputs.close()  

# WordCount输出为txt
with open('words.txt', 'r',encoding="utf-8") as fr: #读入已经去除停用词的文件  
    data = jieba.cut(fr.read())  
data = dict(Counter(data))
with open('wordscount.txt', 'w',encoding="utf-8") as fw: #读入存储wordcount的文件路径  
    for k,v in data.items():  
        fw.write('%s,%d\n' % (k, v))  

#规定每个词的向量维度
size=3000
#规定词向量训练时的上下文扫描窗口大小，窗口为5就是考虑前5个词和后5个词
window=100
#设置最低频率，默认是5，如果一个词语在文档中出现的次数小于5，那么就会丢弃
min_count = 5
workers=multiprocessing.cpu_count()
train_corpus_text="words.txt"
sentences = word2vec.Text8Corpus(train_corpus_text)
model = word2vec.Word2Vec(sentences=sentences, size=size, window=window, min_count=min_count, workers=workers)
model_text = 'w2v_size_{0}.model'.format(size)  
model.save(model_text)
model = gensim.models.Word2Vec.load(model_text)  

#print(model['运动会'])，参照词频文档调整使用  

#计算一个词的最近似的词，倒序
#similar_words = model.most_similar('韦大人')
#for word in similar_words:
#    print(word[0], word[1])


#计算两词之间的余弦相似度
#sim1 = model.similarity('运动会', '总成绩')
#sim2 = model.similarity('排名', '运动会')
#sim3 = model.similarity('展示', '学院')
#sim4 = model.similarity('学院', '体育')
#print(sim1)
#print(sim2)
#print(sim3)
#print(sim4)  

#计算两个集合之间的余弦似度
#list1 = ['运动会', '总成绩']
#list2 = ['排名', '运动会']
#list3 = ['学院', '体育']
#list_sim1 = model.n_similarity(list1, list2)
#print(list_sim1)
#list_sim2 = model.n_similarity(list1, list3)
#print(list_sim2)  

# 选出集合中不同类的词语
#list = ['队员', '足球比赛', '小组', '代表队']
#print(model.doesnt_match(list))
#list = ['队员', '足球比赛', '小组', '西瓜']
#print(model.doesnt_match(list))