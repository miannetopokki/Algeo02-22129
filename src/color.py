import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
#np.set_printoptions(threshold=np.inf)

def convert_rgb_to_hsv(image):
    image=image[:, :, ::-1]
    image_mat = image/255
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
    return hsv

#ini rumus dari referensi, diquantify dulu -> pakai euclidean distance bukan cosine similarity
def quantify(hsv):
    h=hsv[:,:,0]
    s=hsv[:,:,1]
    v=hsv[:,:,2]
    width=len(h)
    height=len(h[0])
    for i in range(width):
        for j in range(height):
            if (h[i][j]>=316):
                h[i][j]=0
            elif (h[i][j]>=1 and h[i][j] <=25):
                h[i][j]=1
            elif (h[i][j]<=40):
                h[i][j]=2
            elif (h[i][j]<=120):
                h[i][j]=3
            elif (h[i][j]<=190):
                h[i][j]=4
            elif (h[i][j]<=270):
                h[i][j]=5
            elif (h[i][j]<=295):
                h[i][j]=6
            elif (h[i][j]<=315):
                h[i][j]=7
            if (s[i][j]<0.2):
                s[i][j]=0
            elif (s[i][j]<0.7):
                s[i][j]=1
            else:
                s[i][j]=2
            if (v[i][j]<0.2):
                v[i][j]=0
            elif (v[i][j]<0.7):
                v[i][j]=1
            else:
                v[i][j]=2
    quantified_hsv = np.transpose([h, s, v], (1, 2, 0))
    return quantified_hsv

#euclidean distance untuk rumus dari referensi
def euclid_distance(vector1,vector2):
    distance = np.sum((vector1-vector2)**2)
    return distance

#ini metode yang ada di spesifikasi
def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    len_vector1 = np.sqrt(np.sum((vector1)**2))
    len_vector2 = np.sqrt(np.sum((vector2)**2))
    similarity = dot_product / (len_vector1 * len_vector2)
    return similarity

def pencarian_blok(query,database):
    height_q, width_q, _ = query.shape
    height_db, width_db, _ = database.shape
    # with open('query.txt', 'w') as f:
    #     print(query, file=f)
    block_size = 3
    similarities = []
    for i in range(0, height_q, block_size):
        for j in range(0, width_q, block_size):
            block_query = query[i:i+block_size, j:j+block_size]
            block_database = database[i:i+block_size, j:j+block_size]
            vector_query=block_query.flatten()
            vector_db=block_database.flatten()
            #Reference method
            #similarity=euclid_distance(vector_db,vector_query)
            #metode ori
            similarity=cosine_similarity(vector_db,vector_query)
            similarities.append(similarity)
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
        #if (similarity>=60):
        matches.append((image, similarity))

    # Mengurutkan citra berdasarkan tingkat kesamaan
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches

if __name__ == "__main__":
    # Query image
    query_image = cv2.imread("7.jpg")

    # Database
    database_images = [
        cv2.imread("7.jpg"),
        cv2.imread("8.jpg"),
        cv2.imread("9.jpg"),
        cv2.imread("tes.jpg"),
        cv2.imread("3549.jpg")
    ]

    result = color_based_image_retrieval(query_image, database_images)
    

    # display matches
    cv2.imshow("Query image", query_image)
    for i, (image, similarity) in enumerate(result):
        cv2.imshow(f"Match {i + 1} - Similarity: {similarity:.2f}%", image)


    cv2.waitKey(0)
    cv2.destroyAllWindows()