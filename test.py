import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']

N = 5
menMeans = (20, 35, 30, 35, 27)
womenMeans = (25, 32, 34, 20, 25)
menStd = (2, 3, 4, 1, 2)
womenStd = (3, 5, 2, 3, 3)
ind = np.arange(N)  # the x locations for the groups
width = 0.35  # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, menMeans, width, yerr=menStd)
p2 = plt.bar(ind, womenMeans, width, bottom=menMeans, yerr=womenStd)

plt.title('2020年央视《新闻联播》出现频次最高的职业')
plt.ylabel('Scores')
plt.xticks(ind, ('G1', 'G2', 'G3', 'G4', 'G5'))
plt.yticks(np.arange(0, 81, 10))
plt.legend((p1[0], p2[0]), ('Men', 'Women'))

plt.show()

data = {
    '医护人员': 437,
    '警察': 420,
    '工人': 321,
    '医生': 254,
    '毕业生': 210,
    '海军': 180,
    '农民工': 150,
    '企业家': 115,
    '职工': 114,
    '解放军': 100,
    '空军': 91,
    '院士': 77,
    '务工人员': 76,
    '大学生': 72,
    '人民警察': 63,
    '武警': 62,
    '医师': 42,
    '陆军': 40,
    '法官': 34,
    '扶贫干部': 33,
}
