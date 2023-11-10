from flask import Flask, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename
import os
import math
import time
import glob
import cv2
from color import color_based_image_retrieval
from CBIRtexture import imgToVector,cosSimilarity

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['DATASETS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'datasets')
app.config['FILTER_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static')
app.secret_key = 'keyjangandigantiplisdarihugo'  #buat save session kalo ganti page

# Konfigurasi lokasi direktori 'uploads'

@app.route('/')
def main():
    message = "Hello from Flask!"
    return render_template('main.html', message=message)

@app.route('/about')
def about():
    message = "About!"
    return render_template('about.html', message=message)



@app.route('/use', methods=['GET', 'POST'])
def use():
    if 'image' in request.files:
        imageKamera = request.files['image']
        if imageKamera:
            # Simpan gambar yang diterima di server (opsional)
            file_path = os.path.join(app.config['DATASETS_FOLDER'], imageKamera.filename)
            imageKamera.save(file_path)
            messageunggah = "Berhasil diunggah!"
            image_url = "static/datasets/" + imageKamera.filename
            namafile = imageKamera.filename
            # Simpan image_url dan namafile di sesi
            session['image_url'] = image_url
            session['namafile'] = namafile
            # Lakukan pemrosesan gambar di sini (sesuaikan dengan kebutuhan Anda)

    #Fungsi Hapus Gambar
    if request.method == 'POST':
    # Mendapatkan path gambar yang akan dihapus dari form
        image_to_delete = request.form.get('image_path')

        # Periksa apakah tombol delete ditekan
        if 'delete_image' in request.form:
            # Path lengkap ke file gambar yang akan dihapus
            full_path = os.path.join(app.root_path, image_to_delete)

            # Memastikan path file berada dalam folder 'datasets' dan merupakan file gambar
            if os.path.exists(full_path) and full_path.startswith(os.path.join(app.root_path, 'static', 'datasets')) and \
            (full_path.lower().endswith('.jpg') or full_path.lower().endswith('.png')):
                try:
                    # Hapus file gambar
                    os.remove(full_path)
                    print(f"File gambar {image_to_delete} berhasil dihapus.")
                    session['image_url'] = None
                    session['namafile'] = None
                    session['messageunggah'] = "Berhasil Hapus foto!"
                except Exception as e:
                    print(f"Gagal menghapus file gambar: {str(e)}")







    #DEKLARASI AWAL==============
    # Menampilkan maksimum 6 gambar per halaman
    page_size = 12
    page = int(request.args.get('page', 1))  # Halaman saat ini, defaultnya adalah halaman 1
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    # Path ke direktori datasets di dalam folder static

    dataset_dir = app.config['DATASETS_FOLDER']
    # Mengambil daftar file gambar dalam direktori datasets
    image_list = [os.path.join('static', 'datasets', filename) for filename in os.listdir(dataset_dir) if filename.endswith(('.jpg', '.png', '.jpeg'))]
    # Mengambil daftar gambar untuk halaman saat ini

    current_images = image_list[start_index:end_index]
    num_pages = math.ceil(len(image_list) / page_size)
    image_list = []
    messageunggah = ""
    image_url = None  # Tetapkan dengan nilai default
    namafile = None
    action = request.form.get('action')

    if action == "Reset":
        folder_path = os.path.join(os.path.dirname(__file__), 'static', 'filter')
        try :
            session['image_url'] = None
            session['namafile'] = None
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path,filename)
                if os.path.isfile(file_path) and (filename.lower().endswith('.jpg') or filename.lower().endswith('.png')):
                    os.remove(file_path)
            print("Semua file gambar (.jpg dan .png) dalam folder berhasil dihapus.")
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")





    if action == "Unggah":
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file:
                # Periksa ekstensi file yang diunggah
                allowed_extensions = {'jpg', 'jpeg', 'png'}
                if '.' in uploaded_file.filename and uploaded_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    file_path = os.path.join(app.config['DATASETS_FOLDER'], uploaded_file.filename)
                    uploaded_file.save(file_path)
                    messageunggah = "Berhasil diunggah!"
                    image_url = "static/datasets/" + uploaded_file.filename
                    namafile = uploaded_file.filename

                    # Simpan image_url dan namafile di sesi
                    session['image_url'] = image_url
                    session['namafile'] = namafile
                else:
                    messageunggah = "File yang diunggah tidak valid. Harap unggah file dengan ekstensi .jpg, .jpeg, atau .png."
            else:
                messageunggah = "Gagal mengunggah file."
        session['messageunggah'] = "Berhasil upload file!"
        messageunggah = session.get('messageunggah')
        image_url = session.get('image_url')
        namafile = session.get('namafile')
        return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, image_list=current_images, num_pages=num_pages, current_page=page)
            



    # Menghitung jumlah halaman total
    if action == 'Search':
        database_images = []
        image_url = session.get('image_url')
        if (image_url != None):
            query_image = cv2.imread(image_url)
            for img in glob.glob("./static/datasets/*.jpg"):
                n = cv2.imread(img)
                database_images.append(n)
            start = time.time()
            result = color_based_image_retrieval(query_image, database_images)
            end =time.time()
            duration = end-start
            page_size = len(result)
            page = int(request.args.get('page', 1))  # Halaman saat ini, defaultnya adalah halaman 1
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            image_list = result
            messageunggah = session.get('messageunggah')
            namafile = session.get('namafile')
            output_folder = os.path.join(app.config['FILTER_FOLDER'], 'filter')
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            filteredImages = []
            # Simpan gambar-gambar hasil filter
            for i, (image, similarity) in enumerate(image_list):
                output_filename = f'result{i + 1}.jpg'
                output_path = os.path.join(output_folder, output_filename)
                cv2.imwrite(output_path, image)
                filteredImages.append((output_path,similarity))
            # Sekarang, baca daftar gambar hasil filter dari direktori 'filter'
            countFiltered = len(filteredImages)
        
            image_list = [os.path.join('static', 'filter', os.path.basename(image_path)) for image_path, similarity in filteredImages]
            current_images = image_list[start_index:end_index]
            session['messageunggah'] = "Search Berhasil!"
            messageunggah = session.get('messageunggah')
            session['jenissearch'] = "Color"
            jenissearch = session.get('jenissearch')
            duration = round(duration,2)
            return render_template('use.html',searchType = jenissearch, countfilter = countFiltered,unggah=messageunggah, image_url=image_url, namafile=namafile, result =filteredImages ,image_list=current_images, num_pages=1, current_page=1, durasi=duration)
        

        else:
            session['messageunggah'] = "Error! Anda mau search apa wkwkwk"
            messageunggah = session.get('messageunggah')



    if action == 'SearchTexture':
        database_images = []
        result = []
        image_url = session.get('image_url')
        if (image_url != None): #ada fotonya
            vec_ref = imgToVector(image_url)
            start = time.time()
            for img in glob.glob("./static/datasets/*.jpg"):
                vec_set = imgToVector(img)
                similarity = 100 * cosSimilarity(vec_ref,vec_set)
                n = cv2.imread(img)
                result.append((n,similarity))
            end =time.time()

            duration = end-start
            page_size = len(result)
            page = int(request.args.get('page', 1))  # Halaman saat ini, defaultnya adalah halaman 1
            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            output_folder = os.path.join(app.config['FILTER_FOLDER'], 'filter')

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            filteredImages = []
            result.sort(key=lambda x: x[1], reverse=True)

            namafile = session.get('namafile')
            for i, (image, similarity) in enumerate(result):
                output_filename = f'result{i + 1}.jpg'
                output_path = os.path.join(output_folder, output_filename)
                cv2.imwrite(output_path, image)
                filteredImages.append((output_path,similarity))
            countFiltered = len(filteredImages)
            image_list = [os.path.join('static', 'filter', os.path.basename(image_path)) for image_path, similarity in filteredImages]
            current_images = image_list[start_index:end_index]
            session['messageunggah'] = "Search Berhasil!"
            session['jenissearch'] = "Texture"
            jenissearch = session.get('jenissearch')
            messageunggah = session.get('messageunggah')
            duration = round(duration,2)
            return render_template('use.html', searchType = jenissearch ,countfilter = countFiltered,unggah=messageunggah, image_url=image_url, namafile=namafile, result =filteredImages ,image_list=current_images, num_pages=1, current_page=1, durasi=duration)


        else:
            session['messageunggah'] = "Error! Anda mau search apa wkwkwk"
            messageunggah = session.get('messageunggah')
            




    image_url = session.get('image_url')
    messageunggah = session.get('messageunggah')
    namafile = session.get('namafile')
    enablePages = "True"
    return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, image_list=current_images, num_pages=num_pages, current_page=page,enablepage = enablePages)

if __name__ == '__main__':
    app.run()
