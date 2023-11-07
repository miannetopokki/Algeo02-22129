import cv2
import numpy as np
from PIL import Image
import math
import time
import glob
#np.set_printoptions(threshold=np.inf)

def convert_rgb_to_hsv(image):
    row, col = image.size
    h=np.zeros((row,col))
    s=np.zeros((row,col))
    v=np.zeros((row,col))
    for i in range(row):
        for j in range(col):
            r,g,b = image.getpixel((j,i))
            r,g,b = r/255, g/255, b/255
            cmax = max(r,g,b)
            cmin = min(r,g,b)
            delta = cmax-cmin
            v[i][j]=cmax
            if (delta==0):
                h[i][j]=0
            elif (cmax==r):
                h[i][j]=60*(((g-b)/delta)%6)
            elif (cmax==g):
                h[i][j]=60*(((b-r)/delta)+2)
            else:
                h[i][j]=60*(((r-g)/delta)+4)
            if (cmax!=0):
                s[i][j]=delta/cmax
            h[i][j], s[i][j], v[i][j] = quantify(h[i][j],s[i][j],v[i][j])

    # image_mat = image/255
    # r=image_mat[:,:,0]
    # g=image_mat[:,:,1]
    # b=image_mat[:,:,2]
    # cmax=np.max(image_mat, axis=2)
    # cmin=np.min(image_mat, axis=2)
    # delta=(cmax-cmin)
    

    # for i in range(row):
    #     for j in range(col):
    #         cmax[i][j]=max(r[i][j],g[i][j],b[i][j])
    #         cmin[i][j]=min(r[i][j],g[i][j],b[i][j])
    #         delta[i][j]=cmax[i][j]-cmin[i][j]
    # for i in range(row):
    #     for j in range(col):
    #         if (delta[i][j]==0):
    #             h[i][j]=0
    #         elif (cmax[i][j]==r[i][j]):
    #             h[i][j]=60*(((g[i][j]-b[i][j])/delta[i][j])%6)
    #         elif (cmax[i][j]==g[i][j]):
    #             h[i][j]=60*(((b[i][j]-r[i][j])/delta[i][j])+2)
    #         else:
    #             h[i][j]=60*(((r[i][j]-g[i][j])/delta[i][j])+4)
    #         if (cmax[i][j]!=0):
    #             s[i][j]=delta[i][j]/cmax[i][j]
    #         h[i][j], s[i][j], v[i][j] = quantify(h[i][j],s[i][j],v[i][j])

    quantified_hsv = np.transpose([h, s, v], (1, 2, 0))
    quantified_hsv = quantified_hsv.astype(int)
    return quantified_hsv

def quantify(h,s,v):
    if (h>=316):
        h=0
    elif (h <=25):
        h=1
    elif (h<=40):
        h=2
    elif (h<=120):
        h=3
    elif (h<=190):
        h=4
    elif (h<=270):
        h=5
    elif (h<=295):
        h=6
    elif (h<=315):
        h=7
    if (s<0.2):
        s=0
    elif (s<0.7):
        s=1
    else:
        s=2
    if (v<0.2):
        v=0
    elif (v<0.7):
        v=1
    else:
        v=2
    return h,s,v
            


#ini metode yang ada di spesifikasi
def cosine_similarity(vector1, vector2):
    dot_product = 0
    panjang1 = 0
    panjang2 = 0
    for i in range(len(vector1)):
        dot_product+=(vector1[i]*vector2[i])
        panjang1 += (vector1[i]**2)
        panjang2 += (vector2[i]**2)
    panjang1 = math.sqrt(panjang1)
    panjang2 = math.sqrt(panjang2)
    similarity = dot_product / (panjang1 *panjang2)
    return similarity

def histogram(hsv):
    hist = np.zeros(14, dtype=object)
    h=hsv[:,:,0]
    s=hsv[:,:,1]
    v=hsv[:,:,2]
    width=len(h)
    height=len(h[0])
    for i in range(width):
        for j in range(height):
            hist[h[i][j]]+=1
            hist[s[i][j]+8]+=1
            hist[v[i][j]+11]+=1
    return hist



def pencarian_blok(query,database):
    height_q, width_q, _ = query.shape
    height_db, width_db, _ = database.shape
    if (height_q%3==0):
        block_height = [int(height_q/3), int(height_q/3), int(height_q/3)]
    elif (height_q%3==1):
        block_height = [int((height_q//3)+1), int(height_q//3), int(height_q//3)]
    else:
        block_height = [int((height_q//3)+1), int(height_q//3), int((height_q//3)+1)]
    
    if (width_q%3==0):
        block_width = [int(width_q/3), int(width_q/3), int(width_q/3)]
    elif (width_q%3==1):
        block_width = [int((width_q//3)+1), int(width_q//3), int(width_q//3)]
    else:
        block_width = [int((width_q//3)+1), int(width_q//3), int((width_q//3)+1)]

    similarities = []
    p=0
    # k=1
    for i in range(0, height_q, block_height[p]):
        q=0
        for j in range(0, width_q, block_width[q]):
            block_query = query[i:i+block_height[p], j:j+block_width[q]]
            block_database = database[i:i+block_height[p], j:j+block_width[q]]
            # print(k)
            # k+=1
            hist_query = histogram(block_query)
            hist_db = histogram(block_database)
            similarity = cosine_similarity(hist_query, hist_db)
            similarities.append(similarity)
            q+=1
        p+=1
    similarities=np.array(similarities)

    average_similarity = np.mean(similarities)
    
    #Kalau metode ori perlu diconvert ke persen
    similarity_percentage = (average_similarity)*100
    
    #Metode referensi langsung aja
    #similarity_percentage = 100-average_similarity

    return similarity_percentage



def color_based_image_retrieval(query_image, database_images):
    query_image = convert_rgb_to_hsv(query_image)
    #query_image = quantify(query_image)

    matches = []
    for image in database_images:
        db_image = convert_rgb_to_hsv(image)
        #db_image = quantify(db_image)
        similarity = pencarian_blok(query_image,db_image)
        if (similarity>=60):
            matches.append((image, similarity))

    # Mengurutkan citra berdasarkan tingkat kesamaan
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches

if __name__ == "__main__":
    # Query image
    query_image = Image.open("./static/datasets/2.jpg")

    # Database
    database_images = [
        Image.open("7.jpg")
    ]
    # database_images = []
    # for img in glob.glob("./static/datasets/*.jpg"):
    #     n = cv2.imread(img)
    #     database_images.append(n)
    start = time.time()
    result = color_based_image_retrieval(query_image, database_images)
    end =time.time()
    duration = end-start
    print(f'Time taken: {duration}')
    # display matches
    # cv2.imshow("Query image", query_image)
    # for i, (image, similarity) in enumerate(result):
    #     cv2.imshow(f"Match {i + 1} - Similarity: {similarity:.2f}%", image)


    # cv2.waitKey(0)
    # cv2.destroyAllWindows()