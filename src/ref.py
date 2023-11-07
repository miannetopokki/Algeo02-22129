import cv2
import numpy as np
import time
import glob

def calculate_histogram(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    h_hist = np.histogram(h, bins=7, range=(0, 7))[0]
    s_hist = np.histogram(s, bins=3, range=(0, 1))[0]
    v_hist = np.histogram(v, bins=3, range=(0, 1))[0]
    return np.concatenate((h_hist, s_hist, v_hist))

def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    return dot_product / (norm_vector1 * norm_vector2)

def color_based_image_retrieval(query_image, database_images):
    query_histogram = calculate_histogram(query_image)

    matches = []
    for image in database_images:
        db_histogram = calculate_histogram(image)
        similarity = cosine_similarity(query_histogram, db_histogram)
        #if similarity >= 0.6:  # Threshold
        matches.append((image, similarity))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

if __name__ == "__main__":
    query_image = cv2.imread("7.jpg")
    database_images = [cv2.imread("./static/datasets/2.jpg")]

    start_time = time.time()
    result = color_based_image_retrieval(query_image, database_images)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Time taken: {duration} seconds")

    cv2.imshow("Query Image", query_image)
    for i, (image, similarity) in enumerate(result):
        cv2.imshow(f"Match {i + 1} - Similarity: {similarity:.2f}", image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
