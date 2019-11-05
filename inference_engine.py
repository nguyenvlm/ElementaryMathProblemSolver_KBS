from utilities import *
from functools import reduce
import re

class inference_engine:
    def __init__(self, kbmodel_dir_path = 'KBModel/'):
        self.relations = read_json(kbmodel_dir_path + 'relations.json')
        self.rules = read_json(kbmodel_dir_path + 'rules.json')
        self.patterns = read_json(kbmodel_dir_path + 'patterns.json')
        self.facts = []
        self.queries = []
        self.opmap = {
            '+': lambda a: reduce(lambda x,y: x+y, a),
            '-': lambda a: reduce(lambda x,y: x-y, a),
            '*': lambda a: reduce(lambda x,y: x*y, a),
            '/': lambda a: reduce(lambda x,y: x/y, a),
        }
        self.answer = ''
    
    def fit (self, input_str):
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
        # print(self.facts)
        # print(self.queries)
        self.infer()
        return self.answer
    
    def getFact(self, rela, clause, isquery = False):
        if rela not in self.relations:
            return None
        varProto = self.relations[rela]["var"]
        varSep = self.relations[rela]["split"]
        varFilter = self.relations[rela]["filter"]

        clause = re.sub("(%s)"%("|".join(varFilter)), "", clause)

        numbers = re.findall("\d{1,}", clause)
        clause = re.sub("\d{1,}", "", clause)

        if isquery:
            clause = re.sub("(Hỏi|mấy|bao nhiêu|\?)","",clause)
        
        objects = [w for w in re.split("(%s)"%("|".join(varSep)), clause) if len(w) > 0 and w not in varSep]
        varList = []
        for v in range(len(varProto)-int(isquery)):
            if varProto[v].isupper():
                varList.append(objects.pop(0).strip().lower())
            else:
                varList.append(int(numbers.pop(0).strip()))
        if isquery:
            varList.append(None)
        return {"name": rela, "var": varList}
    
    def infer(self):
        while len(self.facts):
            match = False
            F = self.facts
            Q = self.queries
            R = self.rules
            rule = None
            if len(F) == 1:
                F.extend(Q)
                Q = []
            for i in range(len(F)):
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
                for j in range(len(F)):
                    if j == i:
                        continue
                    f2 = []
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
                    rule = "%s(%s)&%s(%s)" % (F[i]["name"], ';'.join(f1), F[j]["name"],';'.join(f2))
                    if rule in R:
                        match = True
                        if i < j: i,j = j,i
                        F.pop(i)
                        F.pop(j)
                        tmp = R[rule]

                        # Get new fact
                        if len(tmp) > 1:
                            new_fact = {
                                "name": tmp[1][ : tmp[1].index("(")],
                                "var": tmp[1][tmp[1].index("(")+1 : -1].split(';')
                            }
                            for ind in range(len(new_fact["var"])):
                                v = new_fact["var"][ind]
                                if v in varMap:
                                    new_fact["var"][ind] = varMap[v]
                                else:
                                    func = self.opmap[v[:v.index('(')]]
                                    new_fact["var"][ind] = func([varMap[item] for item in v[v.index('(')+1:-1].split(',')])
                            F.append(new_fact)
                        
                        # Add to answer
                        desc = tmp[0]
                        for v in varMap:
                            if v.isupper():
                                desc = desc.replace('$'+v, varMap[v])
                            else:
                                desc = desc.replace('$'+v, str(varMap[v]))
                        
                        for opans in [self.opmap[o[1]](int(t) for t in o[3:-2].split(',')) for o in re.findall('\[.*\]', desc)]:
                            desc = re.sub('\[.*\]', str(opans), desc)
                        self.answer += desc
                        break
                if match:
                    break
            if not match:
                self.answer = "Không thể tìm thấy suy luận thích hợp."
                return
                



if __name__ == "__main__":
    engine = inference_engine()
    print(engine.fit(input()))