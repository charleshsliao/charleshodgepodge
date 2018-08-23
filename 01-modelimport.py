from collections import Counter  
import jieba  
import multiprocessing
import gensim
from gensim.models import word2vec

model_text = 'w2v_size_3000.model' ###注意更改模型文件名
model = gensim.models.Word2Vec.load(model_text)  

#计算一个词的最近似的词，倒序
similar_words = model.most_similar('郑克爽')
for word in similar_words:
    print(word[0], word[1])
    
#print(model['韦爵爷'])

#计算两词之间的余弦相似度
sim1 = model.similarity('大清', '太监')
#sim2 = model.similarity('排名', '运动会')
#sim3 = model.similarity('展示', '学院')
#sim4 = model.similarity('学院', '体育')
print(sim1)
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