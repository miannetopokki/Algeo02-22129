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

def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    len_vector1 = math.sqrt(np.sum((vector1)**2))
    len_vector2 = math.sqrt(np.sum((vector2)**2))
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
            similarity=cosine_similarity(vector_db,vector_query)
            similarities.append(similarity)
    similarities=np.array(similarities)

    average_similarity = np.mean(similarities)
    similarity_percentage = (average_similarity)*100
    return similarity_percentage



def color_based_image_retrieval(query_image, database_images):
    query_image = convert_rgb_to_hsv(query_image)

    matches = []

    for image in database_images:
        db_image = convert_rgb_to_hsv(image)

        similarity = pencarian_blok(query_image,db_image)
        if (similarity>=60):
            matches.append((image, similarity))

    # Mengurutkan citra berdasarkan tingkat kesamaan
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches

if __name__ == "__main__":
    # Query image
    query_image = cv2.imread("7.jpg")

    # Database
    database_images = [
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
        hsv=convert_rgb_to_hsv(image)
        cv2.imshow(f"Match {i + 1} - Similarity: {similarity:.2f}%", hsv)


    cv2.waitKey(0)
    cv2.destroyAllWindows()