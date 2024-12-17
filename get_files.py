import numpy as np
import re
import gzip

np.set_printoptions(formatter={'float': lambda x: "{0:0.1f}".format(x)})

def get_distance_matrix(n, c):
    '''
    Transform output of function read_atsplib in a square matrix that is used in bbound.py

    n - dimension
    c - dictionary with tuples representing edges as keys and distance between them as values
        (edge1, edge2) : distance between edge1 and edge2
    '''
    adj = np.zeros((n, n))
    for pair, distance in c.items():
      adj[pair[0] - 1][pair[1] - 1] = int(distance)
    adj = adj.astype(int)
    return adj

def read_atsplib(filename):
     "basic function for reading a ATSP problem on the TSPLIB format"
     "NOTE: only works for explicit matrices"

     if filename[-3:] == ".gz":
         f = gzip.open(filename, 'rb')
         data_f = f.readlines()
         data = []
         for line in data_f:
             data.append(line.decode())
     else:
         f = open(filename, 'r')
         data = f.readlines()

     for line in data:
         if line.find("DIMENSION") >= 0:
             n = int(line.split()[1])
             break
     else:
         raise IOError("'DIMENSION' keyword not found in file '%s'" % filename)

     for line in data:
         if line.find("EDGE_WEIGHT_TYPE") >= 0:
             if line.split()[1] == "EXPLICIT":
                 break
     else:
         raise IOError("'EDGE_WEIGHT_TYPE' is not 'EXPLICIT' in file '%s'" % filename)

     for k, line in enumerate(data):
         if line.find("EDGE_WEIGHT_SECTION") >= 0:
             break
     else:
         raise IOError("'EDGE_WEIGHT_SECTION' not found in file '%s'" % filename)

     c = {}
     # flatten list of distances
     dist = []
     for line in data[k + 1:]:
         if line.find("EOF") >= 0:
             break
         for val in line.split():
             dist.append(int(val))

     k = 0
     for i in range(n):
         for j in range(n):
             c[i + 1, j + 1] = dist[k]
             k += 1

     return n, c

def get_dist(file_name):
    str_sum = [[]]
    f = open(file_name)
    c = 0
    j = 0
    for line in f.readlines():
        c += 1
        if c == 4:
            NB_TOWNS = int(line.split(" ")[1][:-1])
            dist = np.zeros((NB_TOWNS, NB_TOWNS))
        elif c > 7:
            s = line.replace('\n', '')
            s = line.replace(' ', '  ')
            regex = r"\s((\s)(\s+)?)?"
            subst = "\\2"
            s = re.sub(regex, subst, s)
            s = s.split(' ')
            for i in range(1, len(s)):
                str_sum[j].append(int(s[i]))
                if len(str_sum[j]) == NB_TOWNS:
                    j += 1
                    if j < NB_TOWNS:
                        str_sum.append([])

    for i in range(NB_TOWNS):
        for j in range(NB_TOWNS):
            dist[i][j] = str_sum[i][j]

    return dist
