import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import time
import glob
from multiprocessing import process

def convert_rgb_to_hsv(image):

    # original method
    image = image[:,:,::-1]
    image_mat = image/255

    # pisah channel rgb
    r=image_mat[:,:,0]
    g=image_mat[:,:,1]
    b=image_mat[:,:,2]

    # hitung cmax, cmin, dan delta
    cmax=np.max(image_mat, axis=2)
    cmin=np.min(image_mat, axis=2)
    delta=(cmax-cmin)
    h = np.zeros_like(r)
    s = np.zeros_like(r)

    mask_r = np.logical_and(delta!=0, cmax==r)
    mask_g = np.logical_and(delta!=0, cmax==g)
    mask_b = np.logical_and(delta!=0, cmax==b)

    # hitung nilai H
    h[delta==0] = 0
    h[mask_r] = 60*(((g[mask_r]-b[mask_r])/(delta[mask_r]))%6)
    h[mask_g] = 60*(((b[mask_g]-r[mask_g])/(delta[mask_g]))+2)
    h[mask_b] = 60*(((r[mask_b]-g[mask_b])/(delta[mask_b]))+4)

    # hitung nilai S
    nonzero_mask = cmax != 0
    s[nonzero_mask] = delta[nonzero_mask] / cmax[nonzero_mask]
    v = cmax

    h,s,v = quantify(h,s,v)

    quantified_hsv = np.transpose([h, s, v], (1, 2, 0))
    quantified_hsv = quantified_hsv.astype(int)
    return quantified_hsv

def quantify(h,s,v):

    #numpy method
    
    h[np.logical_and(h>=0, h<=25)] = 1
    h[h>=316] = 0
    h[np.logical_and(h>25, h<=40)] = 2
    h[np.logical_and(h>40, h<=120)] = 3
    h[np.logical_and(h>120, h<=190)] = 4
    h[np.logical_and(h>190, h<=270)] = 5
    h[np.logical_and(h>270, h<=295)] = 6
    h[np.logical_and(h>295, h<=315)] = 7
    s[s>=0.7] = 2
    s[np.logical_and(s>=0.2, s<0.7)] = 1
    s[s<0.2] = 0
    v[v>=0.7] = 2
    v[np.logical_and(v>=0.2, v<0.7)] = 1
    v[v<0.2] = 0

    return h,s,v
            


#ini metode yang ada di spesifikasi
def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm_vector1 * norm_vector2)
    return similarity

def histogram(hsv):
    #numpy method
    
    # Define the H, S, and V thresholds
    h_thresholds = [0, 1, 2, 3, 4, 5, 6, 7]
    s_thresholds = [0, 1, 2]
    v_thresholds = [0, 1, 2]

    # Initialize histograms for H, S, and V
    h_histogram = np.zeros(len(h_thresholds), dtype=object)
    s_histogram = np.zeros(len(s_thresholds), dtype=object)
    v_histogram = np.zeros(len(v_thresholds), dtype=object)

    # Apply thresholds and compute histograms
    for i in range(len(h_thresholds)):
        h_mask = (hsv[:, :, 0] == h_thresholds[i])
        h_histogram[i] = np.count_nonzero(h_mask)

    for i in range(len(s_thresholds)):
        s_mask = (hsv[:, :, 1] == s_thresholds[i])
        s_histogram[i] = np.count_nonzero(s_mask)
        v_mask = (hsv[:, :, 2] == v_thresholds[i])
        v_histogram[i] = np.count_nonzero(v_mask)
    hist = np.concatenate((h_histogram,s_histogram,v_histogram))

    return hist



def pencarian_blok(query,database):
    height_q, width_q, _ = query.shape
    height_db, width_db, _ = database.shape
    if (height_q%3==0):
        block_height_q = [int(height_q/3), int(height_q/3), int(height_q/3)]
    elif (height_q%3==1):
        block_height_q = [int((height_q//3)+1), int(height_q//3), int(height_q//3)]
    else:
        block_height_q = [int((height_q//3)+1), int(height_q//3), int((height_q//3)+1)]

    if (height_db%3==0):
        block_height_db = [int(height_db/3), int(height_db/3), int(height_db/3)]
    elif (height_db%3==1):
        block_height_db = [int((height_db//3)+1), int(height_db//3), int(height_db//3)]
    else:
        block_height_db = [int((height_db//3)+1), int(height_db//3), int((height_db//3)+1)]
    
    if (width_q%3==0):
        block_width_q = [int(width_q/3), int(width_q/3), int(width_q/3)]
    elif (width_q%3==1):
        block_width_q = [int((width_q//3)+1), int(width_q//3), int(width_q//3)]
    else:
        block_width_q = [int((width_q//3)+1), int(width_q//3), int((width_q//3)+1)]

    if (width_db%3==0):
        block_width_db = [int(width_db/3), int(width_db/3), int(width_db/3)]
    elif (width_db%3==1):
        block_width_db = [int((width_db//3)+1), int(width_db//3), int(width_db//3)]
    else:
        block_width_db = [int((width_db//3)+1), int(width_db//3), int((width_db//3)+1)]

    similarities = []
    p=0
    r=0
    for i in range(0, height_q, block_height_q[p]):
        q=0
        s=0
        for j in range(0, width_q, block_width_q[q]):
            block_query = query[i:i+block_height_q[p], j:j+block_width_q[q]]
            block_database = database[r:r+block_height_db[p], s:s+block_width_db[q]]
            hist_query = histogram(block_query)
            hist_db = histogram(block_database)
            similarity = cosine_similarity(hist_query, hist_db)
            similarities.append(similarity)
            s+=block_width_db[q]
            q+=1
        r+=block_height_db[p]
        p+=1
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
            matches.append((image, round(similarity,2)))

    # Mengurutkan citra berdasarkan tingkat kesamaan
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches

# test case

if __name__ == "__main__":
    # Query image
    query_image = cv2.imread("./static/datasets/bg.png")

    # load database
    imdir = './static/datasets/' #folder file
    ext = ['jpg', 'jpeg', 'png'] #format gambar
    files = []
    [files.extend(glob.glob(imdir + '*.' + e)) for e in ext]
    database_images = [cv2.imread(file) for file in files]

    start = time.time()
    result = color_based_image_retrieval(query_image, database_images)
    end =time.time()
    duration = end-start
    print(f'Time taken: {duration}')
    #display matches
    cv2.imshow("Query image", query_image)
    for i, (image, similarity) in enumerate(result):
        cv2.imshow(f"Match {i + 1} - Similarity: {similarity:.2f}%", image)


    cv2.waitKey(0)
    cv2.destroyAllWindows()