"""
时间：2021/03/09
版本号：1.3
重点：窗口用于输入-Entry ，窗口输出界面-Text
"""
import time
import tkinter as tk
import pickle
import math
from PIL import Image, ImageTk
import re

f1 = open('file_tfidf_dict.pkl', 'rb')
f2 = open('nlized.pkl', 'rb')
f3 = open('name_docID.pkl', 'rb')
tfidf_dict = pickle.load(f1)
nlized_dict = pickle.load(f2)
name_docID_dict = pickle.load(f3)
tf = open("word_Dict.pkl", "rb")
new_dict = pickle.load(tf)
file_name=''

def and_search(input1):
    and_list = input1.split('AND')
    print(and_list)
    global file_name
    file_name=''
    for i in and_list:
        file_name+=i
        file_name+=' '

    # 求and项的对应docid的交集
    and_term = []
    for word in and_list:
        and_term.append(list(new_dict[word].keys())[1:])

    # 先找到最短的and项
    mm = set(min(and_term, key=len))

    for item in and_term:
        mm.intersection_update(set(item))

    and_docID = sorted(list(mm))
    return and_docID


def or_search(input1):
    or_list = input1.split('OR')
    or_term = []
    global file_name
    file_name=''
    for i in or_list:
        file_name+=i
        file_name+=' '

    or_set = set()
    for word in or_list:
        or_set = or_set | set(list(new_dict[word].keys())[1:])
    or_docID = sorted(list(or_set))
    return or_docID

def not_search(input1):
    not_list=input1.split('NOT')
    global file_name
    file_name=''
    for i in not_list:
        file_name+=i
        file_name+=' '

    term=set(and_search(not_list[0]))
    not_term=set(and_search(not_list[1]))
    p=list(term.difference(not_term))
    return p



def mix_search(input1):
    print("输入格式：[A1 AND A2...AN] AND [B1 OR B2...BM] AND NOT [C1 OR C2...CK]")
    input1 = input1.replace(' ', '')  # 去除用户输入可能多输的空格
    input1 = input1.upper()
    global file_name
    file_name=''
    try:
        file_name='mix'
        start_time = time.time()
        term = list(input1.split("]"))
        term1 = term[0][1:]
        and_term = and_search(term1)
        # print("and",and_term)
        term2 = term[1][4:]
        or_term = or_search(term2)
        # print("or",or_term)
        term3 = term[2][7:]
        not_term = and_search(term3)
        p1 = list(set(and_term).intersection(or_term))  # 第一第二个括号对应的文档列表求交集
        p2 = list(set(p1).difference(not_term))  # 第一第二个括号和第三个括号对应的文档列表求差集
        end_time = time.time()
        print("共找到" + str(len(p2)) + "篇文档")
        print("程序运行时间：%.6f毫秒\n" % ((end_time - start_time) * 1000))
        print(p2)
        return p2

    except:
        print("输入错误！输出的词项不在语料库中！请重新输入...")


# print(or_search(input))
# input = '指名道姓AND想and馋嘴and饭量'
# input = input.upper()
# print(and_search(input))

# input = '(换位)AND(河里 OR 电动车 OR 墙纸Or成熟)and not(撕开)'
# print(mix_search(input))

def ans_sort(query, file_list):
    # 获取到查询词
    try:
        pos = query.find('NOT')
        query = query[0:pos]
        # print(query)
    finally:
        q_word = re.split('[()|AND|OR]', query)
        q_word = [i for i in q_word if i != '']
        # print(q_word)

    # 计算各个文档的得分,返回按文档得分排序后的文档列表
    file_score_list = []
    # st = time.time()
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
    # ed = time.time()

    return file_score_list


def deal(query_way, query):
    query = query.upper()
    query = query.replace(' ', '')
    if query_way == 1:
        # query = input("请按:xxANDxxxANDxxx格式输入查询关键词:")
        file_list = and_search(query)

    if query_way == 2:
        # query = input("请按:xxORxxxORxxx格式输入查询关键词:")
        file_list = or_search(query)

    if query_way == 3:
        # query = input("请按:(xxANDxxxANDxxx)AND(xxxORxxx)AND NOT(xxxANDxxx)格式输入查询关键词:")
        file_list = mix_search(query)
    if query_way==4:
        file_list=not_search(query)

    if file_list:
        # print(query)
        # print(file_list)
        # print(type(file_list))
        st = time.time()
        sort_list = ans_sort(query, file_list)
        ed = time.time()
        ans_list = [name_docID_dict[i[0]] for i in sort_list]
        print("查询时间", (ed - st) * 1000, 'ms')
        print(ans_list)

    return ans_list


root = tk.Tk()  # 实例化对象
root.title('zbb-tfidf向量空间模型检索')  # 给窗口取名
root.geometry("800x700")
root.config(bg='#50C1E9')

photo = Image.open("多啦头像.jpg")  # 括号里为需要显示在图形化界面里的图片

photo = photo.resize((100, 100))  # 规定图片大小
img0 = ImageTk.PhotoImage(photo)
img1 = tk.Label(text="照片:", image=img0)
img1.pack()

e = tk.Entry(root, show=None, width=50, bg='#E0F4FF')
e.pack()
var = tk.StringVar()


def print_selection():
    choose = var.get()
    print(choose)


r1 = tk.Radiobutton(root, text='xxxANDxxxANDxxx',
                    variable=var, value="1",
                    command=print_selection, bg='white')
r1.pack()

r2 = tk.Radiobutton(root, text='xxxORxxxORxxx',
                    variable=var, value="2",
                    command=print_selection, bg='white')
r2.pack()


r3 = tk.Radiobutton(root, text='[xxANDxxxANDxxx]AND[xxxORxxx]AND NOT[xxxANDxxx]',
                    variable=var, value="3",
                    command=print_selection, bg='white')
r3.pack()




# 索取到entry的值,将值放置在光标位置"insert"形式
def get_ans():
    t.delete("1.0", "end")
    query = e.get()
    query_way = int(var.get())
    st = time.time()
    ans_list = deal(query_way, query)
    ed = time.time()
    # print(ans_list)
    count = 1
    lenl = 0
    lenl = len(ans_list)
    file_path=r'D:\query'
    file_path+='\\'+file_name+'.txt'
    f = open(file_path, 'w')
    if lenl > 50:
        ans_list = ans_list[:50]
    for item in ans_list:
        t.insert("end", "[" + str(count) + "]\t" + item + '\n')
        f.write(item + '\n')
        count += 1
    t.insert("end", "共找到" + str(lenl) + "篇相关文件,按相关度排序如上" + "\n")
    f.close()


# 在光标处插入
b1 = tk.Button(root, text='Search!',
               bg='#FFCC00', font=("Arial,12"),
               width=15, height=2, command=get_ans)  # 给窗口添加按钮
b1.pack()

t = tk.Text(root, height=32, bg='#E0F4FF')
t.pack()
root.mainloop()  # 大型的while循环
f1.close()
f2.close()
f3.close()
