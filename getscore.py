# 计算一个query与对应文档的余弦相似度
import math
import pickle
import re
import time

query = '(换位)AND(河里 OR 电动车 OR 墙纸Or成熟)and not(撕开)'
query = query.replace(' ', '')
query = query.upper()
file_list = [512, 513, 516, 517, 263, 521, 268, 271,
             530, 20, 23, 26, 29, 30, 289, 36, 37, 42,
             302, 305, 308, 61, 325, 82, 338, 344, 91,
             350, 354, 100, 104, 361, 362, 108, 364,
             365, 377, 123, 396, 401, 405, 165, 169,
             171, 176, 180, 189, 449, 196, 458, 204,
             211, 213, 469, 216, 478, 483, 234, 236,
             493, 240, 243, 244, 499, 501, 248, 505, 255]

# 获取到查询词
try:
    pos = query.find('NOT')
    query = query[0:pos]
    print(query)
finally:
    q_word = re.split('[()|AND|OR]', query)
    q_word = [i for i in q_word if i != '']
    print(q_word)

# 计算各个文档的得分,返回按文档得分排序后的文档列表
with open("file_tfidf_dict.pkl", "rb") as tf:
    with open("nlized.pkl", "rb") as tf1:
        # 加载文档tfidf和关键词文件

        file_score_list = []
        tfidf_dict = pickle.load(tf)
        nlized_dict = pickle.load(tf1)
        st = time.time()
        # 对每个文档计算其得分
        for file in file_list:
            # 该文档中词频信息字典
            dict1 = tfidf_dict[file]
            # 该文档得分字典
            score_dict = nlized_dict[file]
            words = dict1.keys()
            # 取交集词汇
            q_list = list(set(q_word).intersection(words))
            # 计算这些词汇的idf并与该文档中的该词tfidf相乘
            score = 0
            for q in q_list:
                idf = math.log(532 / dict1[q]['df'], 10)
                file_score = score_dict[q]
                score += idf * file_score
            item = (file, score)
            file_score_list.append(item)

        file_score_list.sort(key=lambda s: (-s[1], s[0]))
        ed = time.time()

print(file_score_list)

print("查询时间", (ed - st) * 1000, 'ms')
