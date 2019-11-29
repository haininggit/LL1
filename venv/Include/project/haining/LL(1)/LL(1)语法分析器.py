import re
import copy
import queue
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox

#*----全局变量--------*
#存入语法产生式
production = {}
#存入非终结符集
nofinal = []
#存入终结符集
final = []
#存储FIRST集
FIRST = dict()
#存储FOLLOW集
FOLLOW = dict()
#存储开始符号
start = ''
# 分析表
Table = dict()

list1 = "1\n2\n3\n4\n5\n6\n7\n8\n9"



#+++++++++++++++++++++++++++++++++
"""
这一部分判断输入文法是否正确  
并将文法存储在字典中  production = {}
同时得到非终结集      nofinal = []
终结集                final = []
"""
#存储与产生终结符集与非终结符集
def init(filename):
    flag = 0
    """
    进行文法的初始化
    存储产生式
    产生终结符集
    产生非终结符集
    """
    global nofinal, final, start
    condition = lambda t: t != '\n'  # 过滤器用于过滤回车换行键   创建一个小函数
    # print("请输入文法产生式：")
    pattern = re.compile('[A-Za-z]+->[A-Za-z]*[|A-Za-z]*|ε')
    try:
        f = open(filename, "r", encoding="utf-8")
        str1 = f.readline()
        str1 =  ''.join(list(filter(condition, str1)))
        while True:
            # str1 = input()
            # print(str1)
            if str1 == "":  # 如果读入空则退出
                start = list(production.keys())[0]  # 得到开始符号
                nofinal = list(reversed(list(production.keys())))  # 得到非终结符集
                final = list(set(removeparenthes(list(production.values()))))  # 得到终结符集
                break
            elif pattern.match(str1):  # 如果符合文法产生式则进行储存
                list1 = str1.split('->')
                str2 = list1[1]
                production[list1[0]] = list()
                if str2.count("|"):
                    list2 = str2.split('|')
                    for i in range(len(list2)):
                        production[list1[0]].append(list(list2[i]))
                else:
                    production[list1[0]].append(list(list1[1]))
            else:
                print("文法产生式格式不正确，请重新选择正确文法")
                # 输入串中含有非法符号，请输入正确分析串
                flag = 1
                break
            str1 = f.readline()
            str1 = ''.join(list(filter(condition, str1)))
    except:
        print("文件打开错误！")
        return 2
    else:
        print("文件打开成功！")
    f.close()
    if flag:
        return 0
    else:
        return 1



#去掉list里面的括号
def removeparenthes(list1):
    """
    去除list集合中包含的list集合
    并把内部的list元素加在外部list集合中
    """
    list4 = []
    for list2 in list1:
        for list3 in list2:
            for str1 in list3:
                if str1 > 'Z' or str1 < 'A':
                    list4.append(str1)
    return list4
#+++++++++++++++++++++++++++++++++


#---------------------------------

"""
这一部分的作用是
判断文法是否为左递归文法
消除左递归
并且删除多余产生式(无用产生式)

"""
def contain(a,b):
    """
    判断a所能推到出来的式子
    是否含有b开头的非终结符
    例如  a等于S  b等于A 并且有S->Ac|c
    则返回True  否则反之
    :param a:
    :param b:
    :return:
    """
    list2 = production[a]
    for i in range(len(list2)):
        if list2[i][0] == b:
            return True
    return False

#删除多余产生式
def dispel(start):
    """
    函数作用是消除没有用到的产生式
    :return:
    """
    # global production, nofinal
    # for i in range(len(usedsubstr)):
    #     production.pop(usedsubstr[i])
    # nofinal = [x for x in nofinal if x not in usedsubstr]
    global production, nofinal
    usesd = []
    temproduct = {}
    visited = set()
    q = queue.Queue()  # 初始化一个队列
    q.put(start)  # 入队列
    while not q.empty():
        u = q.get()  # 出队列并打印
        temproduct[u] = production[u]
        usesd.append(u)  # 存入
        # print(u)
        for list1 in production.get(u, []):  # S [['a', 'b', 'c', 'S*'], ['b', 'c', 'S*'], ['c', 'S*']]
            for char in list1:
                if char[0].isupper():
                    if char not in visited:
                        visited.add(char)
                        q.put(char)
    production = temproduct
    nofinal = usesd

#消除左递归
def removedirect(a):
    """
    消除直接左递归
    例如S->Sabc|abc|bc|c
    转换成
    S->abcS*|bcS*|cS*
    S*->abcS*|ε
    并且更新非终结符集
    更新终结符集
    更新存储文法的字典
    :return:
    """
    global production,nofinal,final
    list6 = [x for x in production[a] if x[0] == a]   #存放含有左递归的式子
    list7 = []                              #存放不含左递归的式子
    # list7 = [x.append(a+'*') for x in production[a] if x[0] != a]
    for t in production[a]:
        if t[0] != a:
            list7.append(t+[a+'*'])
    production[a] = list7
    list8 = []
    for i in range(len(list6)):
        list8.append(list6[i][1::]+[a+'*'])
    list8.append(['ε'])
    production[a+'*'] = list8
    nofinal.append(a+'*')
    if 'ε' not in final:
        final.append('ε')

#间接左递归代入
def substitution(a, b):
    """
    把b代入a
    把a中的间接左递归用b中的产生式右部进行替换
    例如  A->Bc|c   B->Ds|s
    则函数作用产生  A->Dsc|sc|c  把B产生式带入A产生式
    :param a:
    :param b:
    :return:
    """
    list3 = production[a]
    list4 = production[b]
    list5 = []
    for list1 in list3:
        if b == list1[0]:
            list2 = list1[1 ::]
            for j in list4:
                if len(list2):
                    list5.append(j+list2)
                else:
                    list5.append(j)
        else:
            list5.append(list1)
    return list5

#找出直接左递归文法，并且调用消除左递归方法
def removefinal():
    flag = 0
    tem = copy.deepcopy(production)
    for i in tem.keys():
        for j in tem[i]:
            if j[0] == i:
                flag = 1
                removedirect(i)
                break
    return flag

#主调用函数
def substitutlift():
    """
    代入
    :return:
    """
    """
    函数的主要作用是
    递归产生式的代入
    把间接左递归转换成直接左递归
    消除直接左递归
    并且删除无用的产生式
    :return:
    """
    global production,nofinal,final
    flag = 0
    for i in range(1,len(nofinal)):
        for j in range(0, i):
            if contain(nofinal[i], nofinal[j]):
                production[nofinal[i]] = substitution(nofinal[i], nofinal[j])
                if removefinal():
                    flag = 1
    # print(start)
    dispel(start)  # 去除多余产生式
    final = list(set(removeparenthes(list(production.values()))))  # 得到终结符集
    return flag
#---------------------------------

#*********************************
"""
构造Frist集与Fallow集
得到文法分析表
"""


def get_first():
    global FIRST
    flag = 1   #标志位如果有改变则在进行遍历
    for k in production:
        l = production[k]
        FIRST[k] = list()
        for s in l:
            if not (s[0][0].isupper()):
                FIRST[k].append(s[0])
    while flag:
        flag = 0
        for k in production:
            l = production[k]
            lenth = len(FIRST[k])
            for s in l:
                if (s[0][0].isupper()):
                    FIRST[k].extend(FIRST[s[0]])
                    FIRST[k] = list(set(FIRST[k]))  # 去重
                    if len(FIRST[k]) != lenth:
                        flag = 1
    print("+++++++++++FIRST+++++++++++=")
    for key, value in zip(FIRST.keys(), FIRST.values()):
        print(key, " : ", value, end='\n')

def get_follow():
    condition = lambda t: t != 'ε'  # 过滤器用于过滤空串   创建一个小函数
    flag = 1        #标志位
    for k in production:  # 新建list
        FOLLOW[k] = list()
        if k == list(production.keys())[0]:
            FOLLOW[k].append('#')
    while flag:
        flag = 0
        for k in production:
            l = production[k]       #[['a', 'b', 'c', 'S*'], ['b', 'c', 'S*'], ['c', 'S*']]
            lenth1 = len(FOLLOW[k])
            for s in l:             #['a', 'b', 'c', 'S*']
                if s[len(s) - 1][0].isupper():  #如果产生式最后一个是非终结符
                    lenth2 = len(FOLLOW[s[len(s) - 1]])
                    FOLLOW[s[len(s) - 1]].extend(FOLLOW[k])  # 若A→αB是一个产生式，则把FOLLOW(A)加至FOLLOW(B)中
                    FOLLOW[s[len(s) - 1]] = list(filter(condition, FOLLOW[s[len(s) - 1]]))  # 去除空串
                    FOLLOW[s[len(s) - 1]] = list(set(FOLLOW[s[len(s) - 1]]))     #去重
                    if lenth2 != len(FOLLOW[s[len(s) - 1]]):
                        flag = 1
                for index in range(len(s) - 1):
                    if s[index][0].isupper():
                        lenth3 = len(FOLLOW[s[index]])
                        if s[index + 1][0].isupper():  # 若A→αBβ是一个产生式，则把FIRST(β)\{ε}加至FOLLOW(B)中；
                            FOLLOW[s[index]].extend(FIRST[s[index + 1]])
                            FOLLOW[s[index]] = list(filter(condition, FOLLOW[s[index]]))  # 去除空串
                            FOLLOW[s[index]] = list(set(FOLLOW[s[index]]))   #去重
                            if lenth3 != len(FOLLOW[s[index]]):
                                flag = 1
                        if not (s[index + 1][0].isupper()) and (s[index + 1] != 'ε'):  #Ac  则把c加入FOLLOW(A)中
                            FOLLOW[s[index]].append(s[index + 1])
                            FOLLOW[s[index]] = list(set(FOLLOW[s[index]]))       #去重
                            if lenth3 != len(FOLLOW[s[index]]):
                                flag = 1
                        emptyflag = 1
                        for i in range(index + 1, len(s)):
                            if not (s[i][0].isupper()) or (s[i][0].isupper() & ('ε' not in FIRST[s[i]])):
                                emptyflag = 0
                                break
                        if emptyflag == 1:
                            FOLLOW[s[index]].extend(FOLLOW[k])  # A→αBβ是一个产生式而(即ε属于FIRST(β))，则把FOLLOW(A)加至FOLLOW(B)中
                            FOLLOW[s[index]] = list(filter(condition, FOLLOW[s[index]]))  # 去除空串
                            FOLLOW[s[index]] = list(set(FOLLOW[s[index]]))      #去重
                            if lenth3 != len(FOLLOW[s[index]]):
                                flag = 1
    # for k in FOLLOW:  # 去重
    #     FOLLOW[k] = list(set(FOLLOW[k]))
    print("+++++++++++FOLLOW+++++++++++=")
    for key, value in zip(FOLLOW.keys(), FOLLOW.values()):
        print(key, " : ", value, end='\n')

def generate_table():
    condition = lambda t: t != 'ε'  # 过滤器用于过滤空串   创建一个小函数
    temfinal = copy.deepcopy(final)
    temfinal = list(filter(condition, temfinal))  #去除空串
    for k in production:  # 初始化分析表
        Table[k] = dict()
        for e in temfinal:
            Table[k][e] = None
    for k in production:
        l = production[k]
        for s in l:
            if s[0][0].isupper():
                for e in temfinal:
                    if e in FIRST[s[0]]: Table[k][e] = s
            if s[0] in temfinal:
                Table[k][s[0]] = s
            if (s[0][0].isupper() and ('ε' in FIRST[s[0]])) or (s[0] == 'ε'):
                for c in FOLLOW[k]:
                    Table[k][c] = s
    print("+++++++++++Table+++++++++++=")
    for key, value in zip(Table.keys(), Table.values()):
        print(key, " : ", value, end='\n')
#*********************************


#如果有左递归则进行消除，如果没有则不进行操作
def identifyRecursive():
    """
    左递归函数进行消除
    如果是间接左递归则进行消除
    入股不是则不进行操作
    :return:
    """
    global production, nofinal, final
    temproduct = copy.deepcopy(production)
    temnofinal = copy.deepcopy(nofinal)
    temfinal = copy.deepcopy(final)
    # 消除直接左递归
    removefinal()
    # 代入
    # 如果代入之后没有进行消除左递归，则不进行代入
    if not substitutlift():
        production = temproduct
        nofinal = temnofinal
        final = temfinal
        removefinal()
        final = list(set(removeparenthes(list(production.values()))))  # 得到终结符集

#判别文法是否为LL(1)文法
def identifyLL1():
    for key in production.keys():  #首符集不相交
        i = production[key]
        for j in range(len(i)):
            for k in range(len(i)):
                if j == k:
                    continue
                else:
                    if i[j][0] == i[k][0]:
                        return False
    for i in nofinal:  #非终结符A 若first集有'ε'  则FIRST(A)∩FOLLW(A)为空集
        if 'ε' in FIRST[i]:
            if len(set(FIRST[i]) & set(FOLLOW[i])) > 0:
                return False
    return True

#进行分析串操作
def analyze(analystr):
    flag = 1  #标志位 如果分析成功则为1  如果分析失败则为0
    #保存信息
    str1, str2, str3, str4 = '', '', '', ''
    #list1保存分析栈   list2保存剩余输入串    list3保存所用产生式   list4保存所产生的动作
    list1, list2 = [], []
    list1.append('#')
    list1.append(start)
    list2.append('#')
    for str in reversed(list(analystr)):
        list2.append(str)
    str1 += ''.join(list1)
    str1 += '\n'
    str2 += ''.join(reversed(list2))
    str2 += '\n'
    str3 += '\n'
    str4 += "初始化\n"
    while len(list1) > 1:
        #分析栈栈顶元素
        stackstr = list1.pop()
        #输入串栈顶元素
        inputstr = list2.pop()
        if (stackstr in nofinal or stackstr in final) and (inputstr in final or inputstr == '#'):
            if stackstr in nofinal:   #如果栈顶元素是非终结符则进行移进
                tablevar = Table[stackstr][inputstr]

                if tablevar == None: #出错
                    str1 += ''.join(list1)
                    str1 += '\n'
                    str2 += ''.join(reversed(list2))
                    str2 += '\n'
                    str3 += '\n'
                    str4 += '错,M[{},{}]=None\n'.format(stackstr,inputstr)

                    if stackstr == start:  #如果开始符号不匹配
                        list1.append(stackstr)
                        str1 += ''.join(list1)
                        str1 += '\n'
                        str2 += ''.join(reversed(list2))
                        str2 += '\n'
                        str3 += '\n'
                        str4 += '错,跳过{}\n'.format(inputstr)

                    else:
                        list2.append(inputstr)
                        str1 += ''.join(list1)
                        str1 += '\n'
                        str2 += ''.join(reversed(list2))
                        str2 += '\n'
                        str3 += '\n'
                        str4 += '错,{}已弹出栈\n'.format(stackstr)

                else:  #移进
                    if tablevar[0] == 'ε':
                        pass
                    else:
                        list1.extend(reversed(tablevar))
                    list2.append(inputstr)  #移进时候  输入串元素不出栈
                    str1 += ''.join(list1)
                    str1 += '\n'
                    str2 += ''.join(reversed(list2))
                    str2 += '\n'
                    str3 += '{}->{}\n'.format(stackstr,''.join(tablevar) )
                    str4 += '移进\n'

            else:   #如果栈顶元素是非终结符
                if stackstr == inputstr:
                    str1 += ''.join(list1)
                    str1 += '\n'
                    str2 += ''.join(reversed(list2))
                    str2 += '\n'
                    str3 += '\n'
                    str4 += '{}匹配\n'.format(stackstr)

                else:
                    str1 += ''.join(list1)
                    str1 += '\n'
                    str2 += ''.join(reversed(list2))
                    str2 += '\n'
                    str3 += '\n'
                    str4 += '错,{}与{}不匹配\n'.format(stackstr,inputstr)
                    flag = 0
                    break
        else:
            return (2,str1,str2,str3,str4)

    print("输入要分析的串为：",analystr)
    if len(list2) == 1:
        return (flag,str1,str2,str3,str4)
    else:
        return (0,str1,str2,str3,str4)

#图形化界面的展示与操作
def show():

    root = Tk()
    root.title("LL（1）分析器")
    root.geometry('800x800+200+200')
    # root.config(bg='Gainsboro')

    frm1 = Frame(root)
    frm2 = Frame(root)
    frm3 = Frame(root)
    frm4 = Frame(root)

    # 记录文件位置
    var1 = StringVar()
    # var1.set("张海宁")

    #记录提示的错误信息
    var2 = StringVar()

    # 记录输入的分析串
    var3 = StringVar()

    # 记录结果
    var4 = StringVar()

    #记录分析栈所要显示的信息
    frim1var = StringVar()

    #记录剩余输出串所要显示的信息
    frim2var = StringVar()

    #记录所用产生式所要显示的信息
    frim3var = StringVar()

    #记录动作所要显示的信息
    frim4var = StringVar()

    #当没有选择文件时候是不能进行分析串操作的
    boolean = BooleanVar()
    boolean.set(False)


    def clear():
        var2.set('')
        var1.set('')
        var3.set('')
        var4.set('')
        frim1var.set('')
        frim2var.set('')
        frim3var.set('')
        frim4var.set('')



    def print_menu():
        inputvar = input2.get()
        if inputvar != '' and boolean.get():
            tuple1 = analyze(inputvar)
            frim1var.set(tuple1[1])
            frim2var.set(tuple1[2])
            frim3var.set(tuple1[3])
            frim4var.set(tuple1[4])
            if tuple1[0] == 1:
                var4.set("分析成功")
            elif tuple1[0] == 2:
                # var2.set("输入串中含有非法符号，请输入正确分析串")
                tkinter.messagebox.showwarning(title='预警信息', message='输入串中含有非法符号，请输入正确分析串!')
            else:
                var4.set("分析失败")
            boolean.set(False)
            # print(var2)



    def selectfile():   #触发选择文件的事件，就进行构造文法
        global str2
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            var1.set(filename)
            str2 = readandbuild(filename)
            if str2 != '1':
                # var2.set(str2)
                tkinter.messagebox.showwarning(title='预警信息', message=str2)
            boolean.set(True)
            # print(filename)




    #选择文件
    label1 = Label(root,text='请选择文法文件的位置：',font=('微软雅黑', 13))
    label1.place(x=20, y=10)
    input1 = Entry(root, show=None, highlightcolor='green',bd=1,width=40,textvariable=var1,font=('微软雅黑', 13))
    input1.place(x=200, y=10)

    button1 = Button(root, text='...',bg='SkyBlue', width=6,height=1,command=selectfile)
    button1.place(x=650,y=5)

    button3 = Button(root, text='重置',bg='SkyBlue', width=6, height=1, command=clear)
    button3.place(x=720, y=5)

    #输入要分析的串
    label2 = Label(root, text='请输入要分析的字符串：', font=('微软雅黑', 13))
    label2.place(x=20, y=50)
    input2 = Entry(root, show=None, highlightcolor='green', bd=1, width=40,textvariable=var3,font=('微软雅黑', 13))
    input2.place(x=200, y=50)

    button2 = Button(root, text='分析',bg='SkyBlue', width=6,height=1,command=print_menu)
    button2.place(x=650,y=45)

    # label3 = Label(root, textvariable=var2, font=('微软雅黑', 16),fg='red')
    # label3.place(x=210, y=100)

    label4 = Label(root, textvariable=var4, font=('微软雅黑', 16),fg='Coral')
    label4.place(x=350, y=85)

    frm1.config(height=700, width=180)
    Label(frm1, text='分析栈',font=('微软雅黑', 16)).place(in_=frm1, anchor=NW)
    frm1.place(x=20, y=120)
    frm1message = Message(frm1, textvariable=frim1var,font=('微软雅黑', 16), width=250)
    frm1message.place(x=-10,y=40)

    frm2.config(height=700, width=180)
    Label(frm2, text='剩余输出串',font=('微软雅黑', 16),bd=2).place(in_=frm2,anchor=NW)
    frm2.place(x=210, y=120)
    frm2message = Message(frm2, textvariable=frim2var,font=('微软雅黑', 16), width=250)
    frm2message.place(x=-10,y=40)

    frm3.config(height=700, width=180)
    Label(frm3, text='所用产生式',font=('微软雅黑', 16)).place(in_=frm3, anchor=NW)
    frm3.place(x=400, y=120)
    frm3message = Message(frm3, textvariable=frim3var,font=('微软雅黑', 16), width=250)
    frm3message.place(x=-10,y=40)

    frm4.config( height=700, width=180)
    Label(frm4, text='动作',font=('微软雅黑', 16)).place(in_=frm4, anchor=NW)
    frm4.place(x=590, y=120)
    frm4message = Message(frm4, textvariable=frim4var,font=('微软雅黑', 16), width=250)
    frm4message.place(x=-10,y=40)



    root.mainloop()

#传入文件，读取文件，如果是
def readandbuild(file):
    tem = init(file)
    if tem == 0:#进行读取文件初始化操作
        return "所选文件中文法不正确，请重新选择"
    if tem == 2:
        return "所选文件，打开错误， 请重新选择"
    identifyRecursive()  #消除左递归
    print("++++++++++文法+++++++++++=")
    for key, value in zip(production.keys(), production.values()):
        print(key, " : ", value, end='\n')
    get_first()
    get_follow()
    if identifyLL1():  #如果是LL(1)文法则构造分析表
        generate_table()
    else:
        return "文件中文法不是LL(1)文法，请重新选择"

    return '1'




if __name__ == '__main__':
    show()



# E->TA
# A->+TA|ε
# T->FB
# B->*FB|ε
# F->(E)|i
# #