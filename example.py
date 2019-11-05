def ex(s):
    # s = 'Trên bàn có 7 đĩa cam, mỗi đĩa có 8 quả. Hỏi trên bàn có bao nhiêu quả cam?'
    s = s.lower()
    print(s)
    d = dict()
    if s.find(',') != -1:
        s1 = s.strip().split('.')
        q = s1[0].split(',')
        q.append(s1[1])
        tmp = ''
        tmp1 = ''
        n = 0
        for i in range(len(q)):
            k = 'mỗi'
            if k in q[i]:
                tmp = q[i]
                n = i
        # print(tmp)
        if n == 0:
            tmp1 = q[1]
        else:
            tmp1 = q[0]
        a = [int(s) for s in tmp.split() if s.isdigit()]
        q.append(a[0])
        k = tmp[tmp.find(str(a[0]))+len(str(a[0])):]
        q.append(k)
        a = [int(s) for s in tmp1.split() if s.isdigit()]
        q.append(a[0])
        k = tmp[tmp.find(str(a[0])) + len(str(a[0])):]
        q.append(k)
        d[1] = q

        for i in d[1]:
            print(i)
    else:
        q = s.split('.')
        a = [int(s) for s in q[0].split() if s.isdigit()]
        q.append(a[0])
        k = q[0][q[0].find(str(a[0])) + len(str(a[0])):]
        q.append(k)
        a = [int(s) for s in q[1].split() if s.isdigit()]
        q.append(a[0])
        k = q[1][q[1].find(str(a[0])) + len(str(a[0])):]
        q.append(k)
        for i in q:
            print(i)

ex('TRÊN bàn có 8 chồng sách, mỗi chồng sách có 2 quyển sách. Hỏi trên bàn có mấy quyển sách?')