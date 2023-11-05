from flask import Flask, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename
import os
import math

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['DATASETS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'datasets')
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
    messageunggah = ""
    image_url = None  # Tetapkan dengan nilai default
    namafile = None

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

    # Menghitung jumlah halaman total
    num_pages = math.ceil(len(image_list) / page_size)
    messageunggah = session.get('messageunggah')
    image_url = session.get('image_url')
    namafile = session.get('namafile')
    return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, image_list=current_images, num_pages=num_pages, current_page=page)

if __name__ == '__main__':
    app.run()
