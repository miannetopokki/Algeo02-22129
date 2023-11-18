from PIL import Image
import math
import time

# CARA MENGGUNAKAN (PENTING UNTUK DIBACA)
#   1.  Siapkan nama file image yang ingin dicari similaritas teksturnya (.jpg, .jpeg, .png, dll.)
#   2.  Ubah gambar ke vektor dengan komponen <contrast, homogeneity, entropy> dengan fungsi imgToVector(Nama_File_Gambar)
#   3.  Untuk mencari similaritas tekstur 2 gambar, gunakan fungsi cosSimilarity(Vektor_Gambar_Referensi, Vektor_Gambar_Dataset)
#       (Perhatikan bahwa cosSimilarity akan mengembalikan nilai dalam range hasil fungsi cosinus, yaitu 0 <= cos(x) <= 1,
#       sehingga untuk mengubahnya ke dalam persen, perlu dikali 100)
#   Tambahan: imgToVector dan cosSimilarity merupakan FUNCTION, bukan procedure, sehingga dibutuhkan variabel untuk menampung return value-nya

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
                coOcc[gScaleMtx[i][j]][gScaleMtx[i][j + 1]] += 1
    
    # Kasus sudut 45 derajat
    elif (Angle == 45):
        for i in range (1, height):
            for j in range (width - 1):
                coOcc[gScaleMtx[i][j]][gScaleMtx[i - 1][j + 1]] += 1
    
    # Kasus sudut 90 derajat
    elif (Angle == 90):
        for i in range (1, height):
            for j in range (width):
                coOcc[gScaleMtx[i][j]][gScaleMtx[i - 1][j]] += 1
    
    # Kasus sudut 135 derajat
    elif (Angle == 135):
        for i in range (1, height):
            for j in range (1, width):
                coOcc[gScaleMtx[i][j]][gScaleMtx[i - 1][j - 1]] += 1
    
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

def imgToVector(img_name):
    # Buka file dengan nama img_name
    img = Image.open(img_name)

    # Ubah ke grayscale
    gscale_img = rgbToGrayscale(img)

    # Pembuatan Co-Occurrence Matrix
    coOcc_img = coOccMtx(gscale_img, 0)

    # Normalisasi Co-Occurrence Matrix
    coOcc_img = normalize(coOcc_img)

    # Ambil nilai contrast, homogeneity, dan entropy
    cont = contrast(coOcc_img)
    hom = homogeneity(coOcc_img)
    ent = entropy(coOcc_img)

    # Tutup file gambar
    img.close()

    # Mengembalikan vektor [cont, hom, ent]
    return [cont, hom, ent]

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

# ------------------------------------------------------------------ TEST CASE ------------------------------------------------------------------

# vec_ref = imgToVector('albert.jpg')
# vec_set = imgToVector('jokowi.jpeg')
# start = time.time()

# similarity = 100 * cosSimilarity(vec_ref, vec_set)
# print(f'similarity: {similarity}')
# vec_ref = imgToVector(r'C:\Users\User\Downloads\Algeo02-22129\src\static\datasets\19.jpg')
# vec_set = imgToVector(r'C:\Users\User\Downloads\Algeo02-22129\src\static\datasets\104.jpg')

# similarity = 100 * cosSimilarity(vec_ref, vec_set)
# end = time.time()
# duration = end-start
