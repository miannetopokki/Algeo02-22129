import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
#np.set_printoptions(threshold=np.inf)

def convert_rgb_to_hsv(image):
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
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm_vector1 * norm_vector2)
    return similarity

def color_based_image_retrieval(query_image, database_images):
    query_image = convert_rgb_to_hsv(query_image)
    vector_query = query_image.flatten()

    matches = []

    for image in database_images:
        db_image = convert_rgb_to_hsv(image)
        vector_db = db_image.flatten()

        similarity = cosine_similarity(vector_query,vector_db)*100
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
        cv2.imread("9.jpg")
    ]

    result = color_based_image_retrieval(query_image, database_images)
    

    # display matches
    for i, (image, similarity) in enumerate(result):
        cv2.imshow(f"Match {i + 1} - Similarity: {similarity:.2f}%", image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()