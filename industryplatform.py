import pandas as pd
import numpy as np
import csv
import openpyxl

###################### 回答第一题 #####################
IPALL = pd.DataFrame(pd.read_csv('IP_intime_clean.csv',encoding='utf-8'))  # 读取训练数据
IP_IT=IPALL[IPALL.pindustry_name=='IT/通信/电子/互联网']
IP_IT_20181h=IP_IT[IP_IT.end_time>'2018-01-01']
IP_IT_20181h=IP_IT_20181h[IP_IT_20181h.start_time<'2018-06-30']
print(IP_IT_20181h.shape)

###################### 整体处理 #####################
## save= pd.DataFrame(pd.read_csv('data_list.csv',encoding='utf-8'))
## save['end_time'] = save['end_time'].replace(np.nan, '2018/07/01')
## save['end_time'] = save['end_time'].replace('1970-01-01', '2018/07/01')
## save['company_city'] = save['company_city'].replace('北京市', '北京')
## save['company_city'] = save['company_city'].replace('上海市', '上海')
## save['company_city'] = save['company_city'].replace('深圳市', '深圳')
## save['company_city'] = save['company_city'].replace('广州市','广州')
## save['company_city'] = save['company_city'].replace('天津市', '天津')
## #
## IP_intime=save[save.end_time>'2015-06-30']
## print(IP_intime.shape)
## save = pd.DataFrame(IP_intime) 
## save.to_csv('IP_intime.csv',index=False,header=True)   
## #
## IP_intime_clean = IP_intime.dropna()
## IP_intime_clean.to_csv('IP_intime_clean.csv',index=False,header=True)   
## print(IP_intime_clean.shape)

###################### DROP NAN #####################
## IPALLCLEAN = IPALL.dropna()
## IPALLCLEAN.to_csv('data_list clean.csv',index=False,header=True)   
## print(IPALLCLEAN.shape)

###################### 去除离职时间早于2015/06/30的工作经历 #################### 

## IP_clean = pd.DataFrame(pd.read_csv('data_list clean.csv',encoding='utf-8'))
## IP_intime=IP_clean[IP_clean.end_time>'2015/06/30']
## print(IP_intime.shape)
## save = pd.DataFrame(IP_intime) 
## save.to_csv('IP_intime.csv',index=False,header=True)   

###################### 取前N条数据 #################### 
## N = 10001
## IPALL_10k = pd.read_csv('data_list clean.csv',nrows=10001,encoding='utf-8')  
## save = pd.DataFrame(IPALL_10k) 
## save.to_csv('IP_batch.csv',index=False,header=True)   

## train_IP_batch= IP_batch[list(range(3, 6))]  # 取这20条数据的3到5列值(索引从0开始)
## print(train_IP_batch)


###################### CSV to Xlsx #################### 
## IPALL_10k = pd.read_csv('data_list clean.csv',nrows=10001,encoding='utf-8')  # 读取训练数据
## print(IPALL_10k.shape)  ## 
## ##
## writer = pd.ExcelWriter('IPALL_10k.xlsx')
## IPALL_10k.to_excel(writer, index = False)
## writer.save()
