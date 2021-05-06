import numpy as np
from itertools import permutations

def calc(list1):

    p = [c for c in permutations(list1, 4)]

    symbols = ["+", "-", "*", "/"]

    list2 = []  # 算出24的排列组合的列表

    flag= False

    for n in p:
        one, two, three, four = n
        for s1 in symbols:
            for s2 in symbols:
                for s3 in symbols:
                    if s1+s2+s3 == "+++" or s1+s2+s3 == "***":
                        express = ["{0} {1} {2} {3} {4} {5} {6}".format(one, s1, two, s2, three, s3, four)]  # 全加或者乘时，括号已经没有意义。
                    else:
                        express= ["(({0} {1} {2}) {3} {4}) {5} {6}".format(one, s1, two, s2, three, s3, four),
                                "({0} {1} {2}) {3} ({4} {5} {6})".format(
                                    one, s1, two, s2, three, s3, four),
                                "(({0} {1} ({2} {3} {4})) {5} {6})".format(
                                    one, s1, two, s2, three, s3, four),
                                "{0} {1} (({2} {3} {4}) {5} {6})".format(
                                    one, s1, two, s2, three, s3, four),
                                "{0} {1} ({2} {3} ({4} {5} {6}))".format(one, s1, two, s2, three, s3, four)]

                    for e in express:
                        try:
                            if abs(eval(e)-24) == 0:
                                list2.append(e)
                                flag= True
                        except ZeroDivisionError:
                            pass


    list3 = set(list2)  # 去除重复项

    result = []
    for c in list(list3)[0:1]:
        b = c.replace(' ', '')
        result.append(b)
        break

    if flag == False:
        print("无法算出")
    return result

