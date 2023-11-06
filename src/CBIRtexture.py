from PIL import Image
import math
import time

def rgbToGrayscale(RGBImage):
    # Ekstrak ukuran
    width, height = RGBImage.size

    # Inisialisasi matrix grayscale
    matrix = [[0 for i in range (width)] for j in range (height)]
    
    # Loop untuk ekstrak rgb, convert ke grayscale, input ke image baru
    for i in range(height):
        for j in range(width):
            r, g, b = RGBImage.getpixel((j, i))
            gscalevalue = int(0.29 * r + 0.587 * g + 0.114 * b)
            matrix[i][j] = gscalevalue
    
    # Mengembalikan gambar yang sudah diubah ke grayscale
    return matrix

def coOccMtx(gScaleMtx, Angle):
    # Inisialisasi matrix co-occurrence
    coOcc = [[0 for i in range (256)] for j in range (256)]

    # Ambil dimensi gambar
    height = len(gScaleMtx)
    width = len(gScaleMtx[0])

    # Kasus sudut 0 derajat
    if (Angle == 0):
        for i in range (height):
            for j in range (width - 1):
                coOcc[gScaleMtx[i][j] - 1][gScaleMtx[i][j + 1] - 1] += 1
    
    # Kasus sudut 45 derajat
    elif (Angle == 45):
        for i in range (1, height):
            for j in range (width - 1):
                coOcc[gScaleMtx[i][j] - 1][gScaleMtx[i - 1][j + 1] - 1] += 1
    
    # Kasus sudut 90 derajat
    elif (Angle == 90):
        for i in range (1, height):
            for j in range (width):
                coOcc[gScaleMtx[i][j] - 1][gScaleMtx[i - 1][j] - 1] += 1
    
    # Kasus sudut 135 derajat
    elif (Angle == 135):
        for i in range (1, height):
            for j in range (1, width):
                coOcc[gScaleMtx[i][j] - 1][gScaleMtx[i - 1][j - 1] - 1] += 1
    
    # Mengembalikan cooccurance matrix sesuai sudut yang dimasukkan
    return coOcc

def transpose(Mtx):
    # Ambil dimensi matrix
    h = len(Mtx)
    w = len(Mtx[0])

    # Inisialisasi matrix transpose
    MtxT = [[0 for i in range (w)] for j in range (h)]

    # Buat matrix transpose
    for i in range (h):
        for j in range (w):
            MtxT[i][j] = Mtx[j][i]
    
    # Mengembalikan matrix yang sudah ditranspose
    return MtxT

def normalize(Mtx):
    # Ambil transpose matrix
    MtxT = transpose(Mtx)

    # Ambil dimensi matrix
    h = len(Mtx)
    w = len(Mtx[0])

    # Inisialisasi matrix symmetric
    MtxSym = [[0 for i in range (w)] for j in range (h)]

    # Variabel penyimpan jumlah elemen
    sum = 0

    # Jumlahkan matrix co-occurrence dengan transpose-nya sambil menambahkan ke sum
    for i in range (h):
        for j in range (w):
            MtxSym[i][j] = Mtx[i][j] + MtxT[i][j]
            sum += MtxSym[i][j]

    # Normalisasi dengan membagi MtxSym dengan sum
    for i in range (h):
        for j in range (w):
            MtxSym[i][j] = MtxSym[i][j] / sum

    # Mengembalikan matrix yang sudah dinormalisasi
    return MtxSym


def contrast(coOccMtx):
    # Variabel penyimpanan sum
    con = 0

    # Loop semua elemen matrix co-occurrence lalu kalkulasi menurut rumus contrast
    for i in range (256):
        for j in range (256):
            con += coOccMtx[i][j] * pow((i - j), 2)
    
    # Mengembalikan nilai contrast
    return con

def homogeneity(coOccMtx):
    # Variabel penyimpan sum
    hom = 0

    # Loop semua elemen matrix co-occurrence lalu kalkulasi menurut rumus homogeneity
    for i in range (256):
        for j in range (256):
            hom += coOccMtx[i][j] / (1 + pow((i - j), 2))
    
    # Mengembalikan nilai homogeneity
    return hom

def entropy(coOccMtx):
    # Variabel penyimpan sum
    ent = 0

    # Loop semua elemen matrix co-occurence lalu kalkulasi menurut rumus entropy
    for i in range (256):
        for j in range (256):
            # Jika elemen coOccMtx[i][j] = 0, diabaikan karena log(0) tidak ada dan kalaupun dihitung,
            # limit x * log(x) untuk x mendekati 0 adalah 0 sehingga nilai ent tidak berubah
            if (coOccMtx[i][j] != 0):
                ent += coOccMtx[i][j] * math.log10(coOccMtx[i][j])
    ent = ent * -1

    # Mengembalikan nilai entropy
    return ent

def normalizeVec(V):
    # Variabel panjang vektor
    length = 0

    # Loop untuk menjumlahkan kuadrat elemen
    for i in range (len(V)):
        length += pow(V[i], 2)
    
    # Mencari akar
    length = math.sqrt(length)

    # Normalisasi dengan membagi semua elemen dengan panjang
    for i in range (len(V)):
        V[i] = V[i] / length

    # Mengembalikan vektor yang sudah dinormalisasi
    return V

def cosSimilarity(v1, v2):
    # Pembilang
    numerator = 0
    for i in range (len(v1)):
        numerator += v1[i] * v2[i]

    # Penyebut
    denominatorv1 = 0
    for i in range (len(v1)):
        denominatorv1 += pow(v1[i], 2)
    denominatorv1 = math.sqrt(denominatorv1)

    denominatorv2 = 0
    for i in range (len(v2)):
        denominatorv2 += pow(v2[i], 2)
    denominatorv2 = math.sqrt(denominatorv2)

    denominator = denominatorv1 * denominatorv2

    # Mengembalikan nilai cosine similarity
    return numerator / denominator

start = time.time()

# Buka file foto
img_ref = Image.open('albert.jpg')
img_set = Image.open('white.jpg')

# Ubah ke grayscale
gscale_img_ref = rgbToGrayscale(img_ref)
gscale_img_set = rgbToGrayscale(img_set)

# Pembuatan Co-Occurence Matrix
coOcc_ref_0 = coOccMtx(gscale_img_ref, 0)
coOcc_set_0 = coOccMtx(gscale_img_set, 0)
coOcc_ref_45 = coOccMtx(gscale_img_ref, 45)
coOcc_set_45 = coOccMtx(gscale_img_set, 45)
coOcc_ref_90 = coOccMtx(gscale_img_ref, 90)
coOcc_set_90 = coOccMtx(gscale_img_set, 90)
coOcc_ref_135 = coOccMtx(gscale_img_ref, 135)
coOcc_set_135 = coOccMtx(gscale_img_set, 135)

# Normalisasi matrix Co-Occurence
coOcc_ref_0 = normalize(coOcc_ref_0)
coOcc_set_0 = normalize(coOcc_set_0)
coOcc_ref_45 = normalize(coOcc_ref_45)
coOcc_set_45 = normalize(coOcc_set_45)
coOcc_ref_90 = normalize(coOcc_ref_90)
coOcc_set_90 = normalize(coOcc_set_90)
coOcc_ref_135 = normalize(coOcc_ref_135)
coOcc_set_135 = normalize(coOcc_set_135)

# Ambil nilai contrast
contrast_ref_0 = contrast(coOcc_ref_0)
contrast_set_0 = contrast(coOcc_set_0)
contrast_ref_45 = contrast(coOcc_ref_45)
contrast_set_45 = contrast(coOcc_set_45)
contrast_ref_90 = contrast(coOcc_ref_90)
contrast_set_90 = contrast(coOcc_set_90)
contrast_ref_135 = contrast(coOcc_ref_135)
contrast_set_135 = contrast(coOcc_set_135)

# Ambil nilai homogeneity
homogeneity_ref_0 = homogeneity(coOcc_ref_0)
homogeneity_set_0 = homogeneity(coOcc_set_0)
homogeneity_ref_45 = homogeneity(coOcc_ref_45)
homogeneity_set_45 = homogeneity(coOcc_set_45)
homogeneity_ref_90 = homogeneity(coOcc_ref_90)
homogeneity_set_90 = homogeneity(coOcc_set_90)
homogeneity_ref_135 = homogeneity(coOcc_ref_135)
homogeneity_set_135 = homogeneity(coOcc_set_135)

# Ambil nilai entropy
entropy_ref_0 = entropy(coOcc_ref_0)
entropy_set_0 = entropy(coOcc_set_0)
entropy_ref_45 = entropy(coOcc_ref_45)
entropy_set_45 = entropy(coOcc_set_45)
entropy_ref_90 = entropy(coOcc_ref_90)
entropy_set_90 = entropy(coOcc_set_90)
entropy_ref_135 = entropy(coOcc_ref_135)
entropy_set_135 = entropy(coOcc_set_135)

# Buat vektor ref dan set
v_ref_0 = [contrast_ref_0, homogeneity_ref_0, entropy_ref_0]
v_set_0 = [contrast_set_0, homogeneity_set_0, entropy_set_0]
v_ref_45 = [contrast_ref_45, homogeneity_ref_45, entropy_ref_45]
v_set_45 = [contrast_set_45, homogeneity_set_45, entropy_set_45]
v_ref_90 = [contrast_ref_90, homogeneity_ref_90, entropy_ref_90]
v_set_90 = [contrast_set_90, homogeneity_set_90, entropy_set_90]
v_ref_135 = [contrast_ref_135, homogeneity_ref_135, entropy_ref_135]
v_set_135 = [contrast_set_135, homogeneity_set_135, entropy_set_135]
# v_ref = [contrast_ref_0, homogeneity_ref_0, entropy_ref_0, contrast_ref_45, homogeneity_ref_45, entropy_ref_45, contrast_ref_90, homogeneity_ref_90, entropy_ref_90, contrast_ref_135, homogeneity_ref_135, entropy_ref_135]
# v_set = [contrast_set_0, homogeneity_set_0, entropy_set_0, contrast_set_45, homogeneity_set_45, entropy_set_45, contrast_set_90, homogeneity_set_90, entropy_set_90, contrast_set_135, homogeneity_set_135, entropy_set_135]

# Normalisasi vektor ref dan set
# v_ref_0 = normalizeVec(v_ref_0)
# v_set_0 =  normalizeVec(v_set_0)
# v_ref_45 = normalizeVec(v_ref_45)
# v_set_45 = normalizeVec(v_set_45)
# v_ref_90 = normalizeVec(v_ref_90)
# v_set_90 = normalizeVec(v_set_90)
# v_ref_135 = normalizeVec(v_ref_135)
# v_set_135 = normalizeVec(v_set_135)
# v_ref = normalizeVec(v_ref)
# v_set = normalizeVec(v_set)

# Cari cosine similarity
cosSim_0 = cosSimilarity(v_ref_0, v_set_0)
cosSim_45 = cosSimilarity(v_ref_45, v_set_45)
cosSim_90 = cosSimilarity(v_ref_90, v_set_90)
cosSim_135 = cosSimilarity(v_ref_135, v_set_135)

# Cari nilai rata-rata
cosSimAvg = (cosSim_0 + cosSim_45 + cosSim_90 + cosSim_135) / 4
# cosSimAvg = cosSimilarity(v_ref, v_set)

end = time.time()
duration = end - start

# Tampilkan pada layar kemiripan dan waktu yang dibutuhkan untuk memproses gambar
print(f'Similarity: {cosSimAvg*100}')
print(f'Time taken: {duration}')

# Tutup file
img_ref.close()
img_set.close()