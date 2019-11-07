# -*- coding: utf-8 -*-

from .utilities import *
from functools import reduce
import os
import re
from decimal import Decimal


class InferenceEngine:
    def __init__(self, kbmodel_dir_path=""):
        if kbmodel_dir_path == "":
            kbmodel_dir_path = os.path.dirname(
                os.path.abspath(__file__)) + "/KBModel/"

        self.relations = read_json(kbmodel_dir_path + 'relations.json')
        self.rules = read_json(kbmodel_dir_path + 'rules.json')
        self.patterns = read_json(kbmodel_dir_path + 'patterns.json')
        self.facts = []
        self.queries = []
        self.opmap = {
            '+': lambda a: numericZeroStrip(reduce(lambda x, y: x+y, a)),
            '-': lambda a: numericZeroStrip(reduce(lambda x, y: x-y, a)),
            '*': lambda a: numericZeroStrip(reduce(lambda x, y: x*y, a)),
            '//': lambda a: numericZeroStrip(reduce(lambda x, y: x//y, a)),
            '/': lambda a: numericZeroStrip(reduce(lambda x,y: x/y, a))
        }
        self.answer = ''

    def fit(self, input_str):
        clauses = input_str.replace(',', '.').split('.')
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
                        return "Có lỗi trong biểu diễn tri thức."
                    if isquery:
                        self.queries.append(fact)
                    else:
                        self.facts.append(fact)
                    break
            if not found:
                return "Không thể nhận dạng câu hỏi \"%s\"." % (clause) if isquery else "Không thể nhận dạng giả thiết \"%s\"." % (clause)
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

        num_regex = r"[-+]?\d*\.\d+|\d+"
        numbers = re.findall(num_regex, clause)
        clause = re.sub(num_regex, "", clause)

        if isquery:
            clause = re.sub("(Hỏi|mấy|bao nhiêu|\?)", "", clause)
        
        objects = [re.sub("\\s+", " ",w.strip()).lower() for w in re.split("(%s)" % ("|".join(varSep)), clause) if re.match("\\s*$", w) is None and w not in varSep]
        varList = []

        # print(objects)
        # print(numbers)
        
        for v in range(len(varProto)-int(isquery)):
            if varProto[v].isupper():
                varList.append(objects.pop(0))
            else:
                varList.append(Decimal(numbers.pop(0)))
        if isquery:
            varList.append(None)
        return {"name": rela, "var": varList}
    
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
        E = set() # Explored Rules
        F.extend(Q)
        nquery = len(Q)
        while nquery:
            match = False
            rule = None
            # print("F::", F)
            for i in range(len(F)):
                for j in range(len(F)):
                    if str(F[i])+ "&" + str(F[j]) in E:
                        continue
                    E.add(str(F[i])+ "&" + str(F[j]))
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
                                        new_fact["var"][ind] = func([Decimal(varMap[item]) for item in v[v.index('(')+1:-1].split(',')])
                                F.append(new_fact)
                            # Add to answer
                            desc = tmp[0]
                            for v in varMap:
                                if v.isupper():
                                    desc = desc.replace('$'+v, varMap[v])
                                else:
                                    desc = desc.replace('$'+v, str(varMap[v]))

                            for opans in [self.opmap[o[1:o.index('(')]](Decimal(t) for t in o[o.index('(')+1:-2].split(',')) for o in re.findall('\[.*\]', desc)]:
                                desc = re.sub('\[.*\]', str(opans), desc)
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
