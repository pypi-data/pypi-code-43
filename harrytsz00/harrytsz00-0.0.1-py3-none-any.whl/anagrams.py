def anagrams(w):
    w = list(set(w))
    d = dict()
    for i in range(len(w)):
        s = ''.join(sorted(w[i]))
        if s in d:
            d[s].append(i)
        else:
            d[s] = [i]
    ans = []
    for s in d:
        ans.append([w[i] for i in d[s]])
    return ans