import scipy.io
import numpy as np
import matplotlib.pyplot as plt

def idw(x,y,z,xx,yy):

    x_flat = xx.ravel()#z czata komenda do spłaszczenia macierzy
    y_flat = yy.ravel()

    dist=np.sqrt((x_flat[:,np.newaxis]-x[np.newaxis,:])**2+(y_flat[:,np.newaxis]-y[np.newaxis,:])**2)

    weights=1/(dist**4)

    num=np.sum(weights*z,axis=1)
    den=np.sum(weights,axis=1)

    z_result=num/den
    return z_result.reshape(xx.shape)

load=scipy.io.loadmat('data_map.mat')
print(load.keys())
dane=load['data_map']
x=dane[:,0]
y=dane[:,1]
z=dane[:,2]

size=100
xi=np.linspace(min(x),max(x),size)
yi=np.linspace(min(y),max(y),size)
xx,yy=np.meshgrid(xi,yi)

z_final=idw(x,y,z,xx,yy)

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
surf=ax.plot_surface(xx, yy, z_final)
ax.scatter(x, y, z, marker='x', c='r')

plt.show()
