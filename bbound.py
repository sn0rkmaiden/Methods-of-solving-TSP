import numpy as np
import math
import copy
import time
from get_files import read_atsplib, get_distance_matrix


start_time = time.time()
n, c = read_atsplib('ftv33.atsp.gz')
dist = get_distance_matrix(n, c)
NB_TOWNS = n

starting_town = [None] * NB_TOWNS
ending_town = [None] * NB_TOWNS

best_solution = [None] * NB_TOWNS
best_eval = -1


count = 0


def evaluation_solution(sol):
    eval = 0

    for i in range(NB_TOWNS - 1):   # - 1, т. к. между n городами n - 1 дорог при незамкнутом маршруте
        eval += dist[sol[i]][sol[i + 1]]    # sol[i] - i-й город в маршруте sol

    eval += dist[sol[NB_TOWNS - 1]][sol[0]]    # вернулись домой

    return eval


def build_next_neighbor():
    global best_eval
    sol = [None] * NB_TOWNS
    matr_for_eval = copy.deepcopy(dist)

    sol[0] = 0
    ind = 0
    next_ind = 0
    nbCity = 1
    matr_for_eval[:, 0] = math.inf
    while sol[NB_TOWNS - 2] is None:
        minim = matr_for_eval[ind][0]
        for i in range(1, NB_TOWNS):
            t = matr_for_eval[ind][i]
            if minim > t:
                minim = t
                next_ind = i
        matr_for_eval[ind, :] = math.inf
        matr_for_eval[:, next_ind] = math.inf
        sol[nbCity] = next_ind
        ind = next_ind
        nbCity += 1
    sol[NB_TOWNS - 1] = sum([i for i in range(1, NB_TOWNS)]) - sum(sol[:-1])

    del matr_for_eval
    eval = evaluation_solution(sol)
    print("Next neighbor ", (sol, eval))

    for i in range(NB_TOWNS):
        best_solution[i] = sol[i]

    best_eval = eval
    print("best_solution & best_val: ", best_solution, best_eval)
    return eval


def build_solution(starting_town, ending_town, adding=False):
    print("build_solution is called")
    global best_eval

    if adding:
        starting_town[NB_TOWNS - 1] = sum(i for i in range(1, NB_TOWNS)) - sum(starting_town[:NB_TOWNS - 1])
        ending_town[NB_TOWNS - 1] = sum(i for i in range(1, NB_TOWNS)) - sum(ending_town[:NB_TOWNS - 1])
 #       print("Вот такой состав рёбер получился", get_current_route(starting_town, ending_town))
    solution = [-1] * NB_TOWNS
    currentNode = 0

    #начиная с нулевого города, выстраиваем по starting_town и ending_town цепочку (маршрут)
    for i in range(NB_TOWNS):
        solution[i] = currentNode
        currentNode = ending_town[get_index(currentNode, starting_town)]

    eval = evaluation_solution(solution)

    if eval < best_eval:
        best_eval = eval
        for i in range(NB_TOWNS):
            best_solution[i] = solution[i]
        print("New best solution : ")
        print(best_eval)

    return


def get_index(el, arr):
    try:
        res = arr.index(el)
    except ValueError:
        return -1
    return res



def check_for_cycle(head_1, tail_1, starting_town, ending_town):
    '''
    Эта функция очень полезна в отсеивании множеств маршрутов (см. branch_and_bound) -- я про неё говорила на сдаче
  На вход она принимает ребро, по которому хотим провести разбиение, и уже набранные рёбра
 Далее проходит проверка, создаст ли новое ребро цикл с уже набранными. Если да, возвращается [True, 0]
 Если нет, возвращается [False, [**]], где [**] - ребро, которое содаст цикл в массиве из набранных рёбер
 и проверяемого ребра
    '''
    for_deleting = [tail_1, head_1] # Это если наше ребро, которое собираемся добавить,
    # ни с кем не связано
    # new_head_value - откуда пришли в начало ребра
    # new_tail_value - куда пойдём из конца ребра
    non_ind = get_index(None, starting_town)
    starting_town_cutted = starting_town[:non_ind]
    ending_town_cutted = ending_town[:non_ind]
    cou = 1
    tail = get_index(head_1, ending_town_cutted)
    head = get_index(tail_1, starting_town_cutted)

    if tail == -1 or head == -1:
        if tail == -1 and head == -1:
#            print("for_del", for_deleting)
            pass
        elif tail == -1: #проверяемое ребро соединяется только своим концом с добавленными, идём по
            # добавленным до разрыва
            y = ending_town_cutted[head]
            x = get_index(y, starting_town_cutted)
            while x != -1:
                y = ending_town_cutted[x]
                x = get_index(y, starting_town_cutted)
            for_deleting = [y, head_1]
 #           print("for_del", for_deleting)
        else:
            #проверяемое ребро соединяется только своим началом с добавленным
            y = starting_town_cutted[tail]
            x = get_index(y, ending_town_cutted)
            while x != -1:
                y = starting_town_cutted[x]
                x = get_index(y, ending_town_cutted)
            for_deleting = [tail_1, y]
#            print("for_del", for_deleting)
        return [False, for_deleting]

    new_head_value = starting_town_cutted[tail]
    new_tail_value = ending_town_cutted[head]
#    print(f"checking {new_head_value}, {new_tail_value}")
    while new_head_value != new_tail_value:
        tail = get_index(new_head_value, ending_town_cutted)
        if tail == -1:
            for_deleting = [new_tail_value, new_head_value]
#            print("for_del", for_deleting)
            return [False, for_deleting]

        new_head_value = starting_town_cutted[tail]

#        print(f"checking {new_head_value}, {new_tail_value}")
        if new_head_value == new_tail_value:
            return [True, 0]

        head = get_index(new_tail_value, starting_town_cutted)
        if head == -1:
            for_deleting = [new_tail_value, new_head_value]
#            print("for_del", for_deleting)
            return [False, for_deleting]

        new_tail_value = ending_town_cutted[head]
#        print(f"checking {new_head_value}, {new_tail_value}")
        if cou == NB_TOWNS:
            print("Miracle")
            return [True, 0]
    return [True, 0]


# Это просто для симпатичного вывода рёбер, которые уже набрали
def get_current_route(st_t, end_t):
    current_route = []
    for i in range(len(st_t)):
        if st_t[i] is None:
            return current_route
        else:
            current_route.append([st_t[i], end_t[i]])
    return current_route


def check_for_zeros(m1): # if in return [0] == -1 -- there are no zeros in matrix
    maxZero = [-1, 0, 0]
    nbZerosC = NB_TOWNS - np.count_nonzero(m1, 0)
    nbZerosR = NB_TOWNS - np.count_nonzero(m1, 1)
#    print("Здесь должна быть матрица, в которой считаем нули", m1)
#    print("здесь должны быть количества нулей", nbZerosR, nbZerosC)
    for i in range(NB_TOWNS):
        for j in range(NB_TOWNS):
            if m1[i][j] == 0:
                minR = 0 if nbZerosR[i] > 1 else min([value for value in m1[i] if value != 0])
                minC = 0 if nbZerosC[j] > 1 else min([value for value in m1[:, j] if value != 0])
                if minR == math.inf:
                    minR = 0
                if minC == math.inf:
                    minC = 0
                penalty = minR + minC
                if penalty > maxZero[0]:
                    maxZero = [penalty, i, j]

    return maxZero


def branch_and_bound(dist, iteration, evalParentNode, starting_town, ending_town):
    # Важно! iteration отражает глубину продвижения по дереву или то, сколько рёбер уже было отобрано для маршрута
    # Число итераций - в переменной count
    global count
    count += 1
    if count % 80000 == 0:
        print(count, get_current_route(starting_town, ending_town))
#    print("iteration", iteration)
#    print("dist", dist)
#    print(get_current_route(starting_town, ending_town))

    m = copy.deepcopy(dist)
    evalChildNode = evalParentNode
    minValueRow = np.amin(m, 1)

    for i in range(NB_TOWNS):
        if 0 not in m[i, :] and minValueRow[i] != math.inf:
            m[i] -= minValueRow[i]

            evalChildNode += minValueRow[i]

    minValueColumn = np.amin(m, 0)

    for i in range(NB_TOWNS):
        if 0 not in m[:, i] and minValueColumn[i] != math.inf:
            m[:, i] -= minValueColumn[i]
            evalChildNode += minValueColumn[i]

#    print("evaluation:", evalChildNode)
#    print("redused matrix", m)
    if evalChildNode >= best_eval:
        return

    nbZerosC = NB_TOWNS - np.count_nonzero(m, 0)
    nbZerosR = NB_TOWNS - np.count_nonzero(m, 1)

    maxZero = (-1, 0, 0)

    for i in range(NB_TOWNS):
        for j in range(NB_TOWNS):
            if m[i, j] == 0:

                minR = 0 if nbZerosR[i] > 1 else min([value for value in m[i] if value != 0])
                minC = 0 if nbZerosC[j] > 1 else min([value for value in m[:, j] if value != 0])

                if minR == math.inf:
                    minR = 0

                if minC == math.inf:
                    minC = 0

                v = minR + minC

                if (maxZero[0] < v):
                    maxZero = (v, i, j)

    if maxZero[0] == -1: # Больше нет выбора (если в матрице нет нулей, значит, она вся заполнена бесконечностями)
#        print("\n\nУпёрся в отсутствие нулей", np.amin(m))
        return

#    print(f"for_chose [{maxZero[1]}, {maxZero[2]}]")
    isCycle, reversedEdge = check_for_cycle(maxZero[1], maxZero[2], starting_town, ending_town)

    if isCycle:
        if iteration == NB_TOWNS - 1:
            # Всё ок, замкнём цикл, содержащий все города, добавив ребро maxZero[1:]
            starting_town[iteration] = maxZero[1]
            ending_town[iteration] = maxZero[2]
            print("--Number of iterations:", count)
            build_solution(starting_town, ending_town, True)
            return
        else:
            # Всё плохо, если это ребро добавить, будет цикл, причём не тот, который хочется (не все города содержит).
            # Можем вызвать бб только от варианта "не выбрать ребро"
            m3 = copy.deepcopy(m)
            m3[maxZero[1], maxZero[2]] = math.inf
            branch_and_bound(m3, iteration, evalChildNode, starting_town, ending_town)
            return

    # Но если осталось два ребра до маршрута и замыкающее ещё не отброшено,
    # можем уже на этом уровне дерева собрать маршрут
    # Условие (*):
    if iteration == NB_TOWNS - 2 and m[reversedEdge[0], reversedEdge[1]] != math.inf:
        starting_town[iteration] = maxZero[1]
        ending_town[iteration] = maxZero[2]
        starting_town[iteration + 1] = reversedEdge[0]
        ending_town[iteration + 1] = reversedEdge[1]
        print("Number of iterations:", count)
        build_solution(starting_town, ending_town)


    starting_town_new = copy.deepcopy(starting_town)
    ending_town_new = copy.deepcopy(ending_town)

    starting_town_new[iteration] = maxZero[1]
    ending_town_new[iteration] = maxZero[2]

    m2 = copy.deepcopy(m)
    m2[maxZero[1], :] = math.inf
    m2[:, maxZero[2]] = math.inf
    m2[reversedEdge[0], reversedEdge[1]] = math.inf
    branch_and_bound(m2, iteration + 1, evalChildNode, starting_town_new, ending_town_new)

    m3 = copy.deepcopy(m)
    m3[maxZero[1], maxZero[2]] = math.inf
    branch_and_bound(m3, iteration, evalChildNode, starting_town, ending_town)
    return



'''
dist = np.array([[0.0, 20, 18, 12, 8],
                 [5, 0, 14, 7, 11],
                 [12, 18, 0, 6, 11],
                 [11, 17, 11, 0, 12],
                 [5, 5, 5, 5, 0]])
'''

iteration = 0
lowerbound = 0

dist = dist.astype(float)
np.fill_diagonal(dist, math.inf)

print(dist)
next_neighbor = build_next_neighbor()
branch_and_bound(dist, iteration, lowerbound, starting_town, ending_town)

print("Total number of iterations :", count)
print("Best solution:", best_solution)
print("Best evaluation :", best_eval)
print("Next neighbor heuristic :", next_neighbor)
print("Runtime : %s seconds " % (time.time() - start_time))


'''
Dimension: 17 (with zeroes)
Best evaluation : 39.0
Runtime : 706.89350938797 seconds
Number of iterations: 7796
Total number of iterations : 2986017

Dimension: 33
Best evaluation : 1286.0
Runtime : 20.084980249404907 seconds 
Number of iterations: 21501
Total number of iterations : 30709

Dimension: 35
Best evaluation : 1473.0
Runtime : 8.665074348449707 seconds 
Number of iterations: 2483
Total number of iterations : 10743

Dimension: 38
Best evaluation : 1530.0
Runtime : 27.121103525161743 seconds 
Number of iterations: 33975
Total number of iterations : 40728

Dimension: 44
Best evaluation : 1613.0
Runtime : 128.31369972229004 seconds 
Number of iterations: 77631
Total number of iterations : 180614

Dimension: 47
Best evaluation : 1776.0
Runtime : 2430.343325853348 seconds 
Number of iterations: 2769154
Total number of iterations : 3225488
'''