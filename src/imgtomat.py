import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
#np.set_printoptions(threshold=np.inf)

image = cv2.imread("7.jpg")
image_rgb=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image_mat = image_rgb/255
r=image_mat[:,:,0]
g=image_mat[:,:,1]
b=image_mat[:,:,2]
row=len(r)
col=len(r[0])
cmax=([[0 for i in range(col)] for j in range(row)])
cmin=([[0 for i in range(col)] for j in range(row)])
delta=([[0 for i in range(col)] for j in range(row)])
h=([[0 for i in range(col)] for j in range(row)])
s=([[0 for i in range(col)] for j in range(row)])
v=cmax


for i in range(row):
    for j in range(col):
        cmax[i][j]=max(r[i][j],g[i][j],b[i][j])
        cmin[i][j]=min(r[i][j],g[i][j],b[i][j])
        delta[i][j]=cmax[i][j]-cmin[i][j]
for i in range(row):
    for j in range(col):
        if (delta[i][j]==0):
            h[i][j]=0
        elif (cmax[i][j]==r[i][j]):
            h[i][j]=60*(((g[i][j]-b[i][j])/delta[i][j])%6)
        elif (cmax[i][j]==g[i][j]):
            h[i][j]=60*(((b[i][j]-r[i][j])/delta[i][j])+2)
        else:
            h[i][j]=60*(((r[i][j]-g[i][j])/delta[i][j])+4)
        if (cmax[i][j]!=0):
            s[i][j]=delta[i][j]/cmax[i][j]

hsv=np.transpose([h, s, v], (1, 2, 0))
        


image_hsv=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
cv2.imshow("bgr?", image)
cv2.imshow("hsvmatrix", hsv)
cv2.imshow("hsvcv2", image_hsv)
cv2.waitKey(0)
cv2.destroyAllWindows()