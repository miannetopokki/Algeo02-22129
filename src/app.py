from flask import Flask, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename
import os
import math
import time
import glob
import cv2
from color import color_based_image_retrieval

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['DATASETS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'datasets')
app.config['FILTER_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static')
app.secret_key = 'keyjangandigantiplisdarihugo'  #buat save gambar kalo ganti page

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
    # Menampilkan maksimum 6 gambar per halaman
    page_size = 6
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
    if action == "Unggah":
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file:
                # Periksa ekstensi file yang diunggah
                allowed_extensions = {'jpg', 'jpeg', 'png'}
                if '.' in uploaded_file.filename and uploaded_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                    uploaded_file.save(file_path)
                    messageunggah = "Berhasil diunggah!"
                    image_url = "static/uploads/" + uploaded_file.filename
                    namafile = uploaded_file.filename

                    # Simpan image_url dan namafile di sesi
                    session['image_url'] = image_url
                    session['namafile'] = namafile
                else:
                    messageunggah = "File yang diunggah tidak valid. Harap unggah file dengan ekstensi .jpg, .jpeg, atau .png."
            else:
                messageunggah = "Gagal mengunggah file."
        messageunggah = session.get('messageunggah')
        image_url = session.get('image_url')
        namafile = session.get('namafile')
        return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, image_list=current_images, num_pages=num_pages, current_page=page)
            
    # Menghitung jumlah halaman total
    if action == 'Search':
        database_images = []
        image_url = session.get('image_url')
        query_image = cv2.imread(image_url)
        for img in glob.glob("./static/datasets/*.jpg"):
            n = cv2.imread(img)
            database_images.append(n)
        start = time.time()
        result = color_based_image_retrieval(query_image, database_images)
        end =time.time()
        duration = end-start
        # # display matches
        # cv2.imshow("Query image", query_image)
        # for i, (image, similarity) in enumerate(result):
        #     cv2.imshow(f"Match {i + 1} - Similarity: {similarity:.2f}%", image)
        page_size = 6
        page = int(request.args.get('page', 1))  # Halaman saat ini, defaultnya adalah halaman 1
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        # Path ke direktori datasets di dalam folder static
        # Mengambil daftar file gambar dalam direktori datasets
        image_list = result
        # Mengambil daftar gambar untuk halaman saat ini
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
        image_list = [os.path.join('static', 'filter', os.path.basename(image_path)) for image_path, similarity in filteredImages]
        current_images = image_list[start_index:end_index]
        return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, result =filteredImages ,image_list=current_images, num_pages=num_pages, current_page=page, durasi=duration)



    image_url = session.get('image_url')
    messageunggah = session.get('messageunggah')
    namafile = session.get('namafile')
    return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, image_list=current_images, num_pages=num_pages, current_page=page)

if __name__ == '__main__':
    app.run()
