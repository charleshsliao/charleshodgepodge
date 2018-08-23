import numpy as np
import jieba
import jieba.analyse

#读取文本文件
def read_from_file(directions):      
    decode_set=['utf-8','gb18030','ISO-8859-2','gb2312','gbk','Error']#编码集
    #编码集循环
    for k in decode_set:
        try:
            file = open(directions,"r",encoding=k)
            readfile = file.read()#这步如果解码失败就会引起错误，跳到except。
            
            #print("open file %s with encoding %s" %(directions,k))#打印读取成功
            #readfile = readfile.encode(encoding="utf-8",errors="replace")#若是混合编码则将不可编码的字符替换为"?"。
            file.close()
            break#打开路径成功跳出编码匹配
        except:
            if k=="Error":#如果碰到这个程序终止运行
                raise Exception("%s had no way to decode"%directions)
            continue
    return readfile

inputs = str(read_from_file('words.txt')) #加载要处理的文件的路径  

###textrank提取高频关键词
keylist_textrank=jieba.analyse.textrank(inputs,topK=5,withWeight=False)
print(keylist_textrank)

###tfidf提取特征词
tfidf=jieba.analyse.extract_tags
keylist_tfidf=tfidf(inputs,topK=5)
print(keylist_tfidf)
