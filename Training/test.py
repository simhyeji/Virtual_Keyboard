import numpy as np

nparray = np.arange(16).reshape((4,4))
print(nparray)
print('---'*4)

v1 = nparray[[0, 1, 0, 3, 0, 2], :] # 0, 1, 0, 3, 0, 2번 행의 모든 요소 가져옴
v2 = nparray[[1, 2, 3, 0, 1, 2], :]

print(v1)
print('---'*4)
print(v2)
print('---'*4)
v=v2-v1
print(v)
print('---'*4)
print(v/np.linalg.norm(v,axis=1)[:,np.newaxis])


l = [1]
for i in len(l):
    print(i)