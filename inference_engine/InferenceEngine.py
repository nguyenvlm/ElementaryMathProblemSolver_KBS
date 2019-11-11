# -*- coding: utf-8 -*-

from .utilities import *
from functools import reduce
import os
import re
from fractions import Fraction


class InferenceEngine:
    def __init__(self, kbmodel_dir_path=""):
        if kbmodel_dir_path == "":
            kbmodel_dir_path = os.path.dirname(
                os.path.abspath(__file__)) + "/KBModel/"

        self.relations = read_json(kbmodel_dir_path + 'relations.json')
        self.rules = read_json(kbmodel_dir_path + 'rules.json')
        self.patterns = read_json(kbmodel_dir_path + 'patterns.json')
        self.opmap = {
            '+': lambda a: reduce(lambda x, y: x+y, a),
            '-': lambda a: reduce(lambda x, y: x-y, a),
            '*': lambda a: reduce(lambda x, y: x*y, a),
            '//': lambda a: reduce(lambda x, y: x//y, a),
            '/': lambda a: reduce(lambda x,y: x/y, a)
        }
        self.dictonary = []
        self.facts = []
        self.queries = []
        self.answer = ''
    
    def __repr__(self):
        return '<%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

    def fit(self, input_str):
        self.dictonary = []
        self.facts = []
        self.queries = []
        self.answer = ''
        clauses = filter(lambda c: len(c), input_str.strip().replace(',', '.').split('.'))
        for clause in clauses:
            words = clause.split()
            isquery = "?" in clause or clause.lower().find("hỏi") != -1
            found = False
            for regex in self.patterns:
                if re.search(regex, clause.lower()) is not None:
                    found = True
                    rela = self.patterns[regex]
                    fact = self.getFact(rela, clause, isquery)
                    if fact is None:
                        return "Có lỗi trong phân tích dữ kiện của giả thiết \"%s\"." % (clause)
                    if isquery:
                        self.queries.append(fact)
                    else:
                        self.facts.append(fact)
                    break
            if not found:
                if isquery:
                    return "Không thể nhận dạng câu hỏi \"%s\"." % (clause)
                return "Không thể nhận dạng giả thiết \"%s\"." % (clause)
        
        # print('dictonary', self.dictonary)
        # print('fact')
        # for i in self.facts:
        #     print(i)
        # print('queries',self.queries)
        self.infer()
        return self.answer

    def getFact(self, rela, clause, isquery=False):
        if rela not in self.relations:
            return None
        varProto = self.relations[rela]["var"]
        varSep = self.relations[rela]["split"]
        varFilter = self.relations[rela]["filter"]
        for w in varFilter[:]:
            varFilter.append(w[0].upper()+w[1:])
        clause = re.sub("(%s)" % ("|".join(varFilter)), "", clause)

        num_regex = r"[-+]?\d*[\.\/]?\d+|\d+"
        numbers = re.findall(num_regex, clause)
        # clause = re.sub(num_regex, "", clause)

        if isquery:
            clause = re.sub("(Hỏi|mấy|bao nhiêu|\?)", "", clause)
        
        objects = [
            re.sub("\\s+", " ", re.sub(num_regex, "", w.lower())).strip()
            for w in re.split("(%s)" % ("|".join(varSep)), clause)
        ]

        objects = list(filter( lambda w: all((len(w), re.match("\\s*$", w) is None, w not in varSep)), objects))

        varList = []

        # print(objects)
        # print(numbers)

        for objects_ind in range(len(objects)):
            if objects[objects_ind] in self.dictonary: continue
            Avalable = False
            # print('--',objects[objects_ind])
            for dictonary_ind in range(len(self.dictonary)):
                if self.dictonary[dictonary_ind].find(objects[objects_ind]) == 0:
                    objects[objects_ind] = self.dictonary[dictonary_ind]
                    Avalable = True
                elif objects[objects_ind].find(self.dictonary[dictonary_ind]) == 0:
                    # print('fail in ',objects[objects_ind])
                    # print('fact')
                    # for i in self.facts:
                    #     print(i)
                    for ind in range(len(self.facts)):
                        for var_ind in range(len(self.facts[ind]['var'])):
                            if self.facts[ind]['var'][var_ind] == self.dictonary[dictonary_ind]:
                                self.facts[ind]['var'][var_ind] = objects[objects_ind]
                    self.dictonary[dictonary_ind] = objects[objects_ind]
                    # print('fact')
                    # for i in self.facts:
                    #     print(i)
                    Avalable = True
            if not Avalable:
                self.dictonary.append(objects[objects_ind])

        # print(objects)
        # print(numbers)

        for v in range(len(varProto)-int(isquery)):
            if varProto[v].isupper():
                if len(objects) == 0: 
                    return None
                varList.append(objects.pop(0))
            else:
                if len(numbers) == 0:
                    return None
                tmp = re.split(r"(\/|\.)",numbers.pop(0))
                if len(tmp) == 1:
                    varList.append(Fraction(tmp[0]))
                elif tmp[1] == '/':
                    varList.append(Fraction(tmp[0], tmp[2]))
                else:
                    varList.append(Fraction(tmp[0]) + Fraction(tmp[2]))
        if isquery:
            varList.append(None)

        new_fact = {"name": rela, "var": varList}

        # print(new_fact)
        # print('dictonary',self.dictonary)
        return new_fact
    
    def getStrictRule(self, i, j):
        F = self.facts
        varMap = dict()
        curobj = ord('A')
        curnum = ord('a')
        f1 = []
        for v in F[i]["var"]:
            if v is None:
                f1.append('_')
            elif type(v) is str:
                f1.append(chr(curobj))
                varMap[chr(curobj)] = v
                curobj += 1
            else:
                f1.append(chr(curnum))
                varMap[chr(curnum)] = v
                curnum += 1
        f2 = []
        if i == j:
            f2 = f1
        else:
            for v in F[j]["var"]:
                if v not in F[i]["var"]:
                    if v is None:
                        f2.append('_')
                    elif type(v) is str:
                        f2.append(chr(curobj))
                        varMap[chr(curobj)] = v
                        curobj += 1
                    else:
                        f2.append(chr(curnum))
                        varMap[chr(curnum)] = v
                        curnum += 1
                else:
                    tmp = f1[F[i]["var"].index(v)]
                    f2.append(tmp)
                    varMap[tmp] = v
        return varMap, "%s(%s)&%s(%s)" % (F[i]["name"], ';'.join(f1), F[j]["name"], ';'.join(f2))
    
    def getUnstrictRule(self, i, j):
        F = self.facts
        varMap = dict()
        curobj = ord('A')
        curnum = ord('a')
        f1 = []
        for v in F[i]["var"]:
            if v is None:
                f1.append('_')
            elif type(v) is str:
                f1.append(chr(curobj))
                varMap[chr(curobj)] = v
                curobj += 1
            else:
                f1.append(chr(curnum))
                varMap[chr(curnum)] = v
                curnum += 1
        f2 = []
        for v in F[j]["var"]:
            if v is None:
                f2.append('_')
            elif type(v) is str:
                if v not in F[i]["var"]:
                    f2.append(chr(curobj))
                    varMap[chr(curobj)] = v
                    curobj += 1
                else:
                    tmp = f1[F[i]["var"].index(v)]
                    f2.append(tmp)
                    varMap[tmp] = v
            else:
                f2.append(chr(curnum))
                varMap[chr(curnum)] = v
                curnum += 1
            
        return varMap, "%s(%s)&%s(%s)" % (F[i]["name"], ';'.join(f1), F[j]["name"], ';'.join(f2))
        
    def infer(self):
        Q = self.queries
        F = self.facts
        R = self.rules
        ER = set() # Explored Rules
        EF = set(map(str, F)) # Explored Facts
        F.extend(Q)
        nquery = len(Q)
        if nquery == 0:
            self.answer += "\n\nKhông tìm thấy câu hỏi trong đề bài!\n\nBài toán không có yêu cầu gì để giải quyết!"
            return
        while nquery:
            match = False
            rule = None
            # print("F::", F)
            for i in range(len(F)):
                for j in range(len(F)):
                    if str(F[i])+ "&" + str(F[j]) in ER:
                        continue
                    ER.add(str(F[i])+ "&" + str(F[j]))
                    Rules = [self.getStrictRule(i,j), self.getUnstrictRule(i,j)]
                    for varMap, rule in Rules:
                        # print("ExploredRule::", rule)
                        # print("ExploredFact::",str(F[i])+ "&" + str(F[j]))
                        if rule in R:
                            match = True
                            if None in F[i]["var"] + F[j]["var"] and F[i]["name"] == F[j]["name"]:
                                nquery -= 1
                            # print("Rule match::", rule)
                            # Delete old facts:
                            # if i < j:
                            #     i, j = j, i
                            # F.pop(i)
                            # if len(F): F.pop(j)
                            tmp = R[rule]
                            # Create new fact
                            if len(tmp) > 1:
                                new_fact = {
                                    "name": tmp[1][: tmp[1].index("(")],
                                    "var": tmp[1][tmp[1].index("(")+1: -1].split(';')
                                }
                                for ind in range(len(new_fact["var"])):
                                    v = new_fact["var"][ind]
                                    if v in varMap:
                                        new_fact["var"][ind] = varMap[v]
                                    else:
                                        func = self.opmap[v[:v.index('(')]]
                                        new_fact["var"][ind] = func([Fraction(varMap[item]) for item in v[v.index('(')+1:-1].split(',')])
                                if str(new_fact) not in EF:
                                    EF.add(str(new_fact))
                                    F.append(new_fact)
                            # Add to answer
                            desc = tmp[0]
                            for v in varMap:
                                if v.isupper():
                                    desc = desc.replace('$'+v, varMap[v])
                                else:
                                    tmp = str(Fraction(varMap[v]))
                                    desc = desc.replace('$'+v, tmp)
                            
                            for opans in [self.opmap[o[1:o.index('(')]](Fraction(t) for t in o[o.index('(')+1:-2].split(',')) for o in re.findall('\[.*\]', desc)]:
                                tmp = str(Fraction(opans))
                                desc = re.sub('\[.*\]', tmp, desc)
                            self.answer += desc
                            break
                    if match: break
                if match: break
            if not match:
                self.answer += "\n\nKhông thể tiếp tục quá trình suy luận!"
                return


if __name__ == "__main__":
    while True:
        engine = InferenceEngine()
        print(engine.fit(input()))
