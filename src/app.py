from flask import Flask, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename
import os
import math
import time
import glob
import cv2
import shutil
from color import color_based_image_retrieval
from CBIRtexture import imgToVector,cosSimilarity
from scrape import scrape_images

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['DATASETS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'datasets')
app.config['DATASETSCRAP_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'datasetscrap')
app.config['FILTER_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static','filter')
app.secret_key = 'keyjangandigantiplisdarihugo'  #buat save session kalo ganti page

# Konfigurasi lokasi direktori 'uploads'

def resetFilter():
    folder_path = os.path.join(os.path.dirname(__file__), 'static', 'filter')
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path,filename)
        if os.path.isfile(file_path) and (filename.lower().endswith('.jpg') or filename.lower().endswith('.png')):
            os.remove(file_path)
    

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
    
    if 'isScrape' not in session:  # Periksa apakah 'var' sudah ada di sesi
        session['isScrape'] = False
    if 'isSearch' not in session:  # Periksa apakah 'var' sudah ada di sesi
        session['isSearch'] = False

        
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
        
        

        # Periksa apakah tombol delete ditekan
        if 'delete_image' in request.form:
            image_to_delete = request.form.get('image_path')
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

        elif 'select_image' in request.form:
            image_to_select = request.form.get('image_path')
            file_name = os.path.basename(image_to_select)
            full_path = os.path.join(app.root_path, image_to_select)
            if os.path.exists(full_path) and full_path.startswith(os.path.join(app.root_path, 'static', 'datasets')) and \
            (full_path.lower().endswith('.jpg') or full_path.lower().endswith('.png')):
                try:
                    # Hapus file gambar
                   
                    print(f"File gambar {image_to_select} berhasil diselect.")
                    session['image_url'] = image_to_select
                    session['namafile'] = file_name
                    session['messageunggah'] = "Berhasil select foto!"
                except Exception as e:
                    print(f"Gagal select file gambar : {str(e)}")

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

    # image_list = []
    messageunggah = ""
    image_url = None  # Tetapkan dengan nilai default
    namafile = None
    action = request.form.get('action')
    if action == "SubmitLink":
        inputLink = request.form['inputLinkScrap']
        scrape_images(inputLink)


    #Status Scrap
    if action == 'Scrap':
        session['isScrape'] = True
    elif action == 'stopScrape':
        session['isScrape'] = False



    if(session['isScrape'] == True):
        datasetscrap_dir = app.config['DATASETSCRAP_FOLDER']
        image_list_scrap = [os.path.join('static', 'datasetscrap', filename) for filename in os.listdir(datasetscrap_dir) if filename.endswith(('.jpg', '.png', '.jpeg'))]
        combinedListImage = image_list + image_list_scrap
        current_images = combinedListImage[start_index:end_index]
        num_pages = math.ceil(len(combinedListImage) / page_size)


    if action == "Reset":
        
        try :
            session['image_url'] = None
            session['namafile'] = None
            session['isSearch'] = False
            resetFilter()
            
            print("Semua file gambar (.jpg dan .png) dalam folder berhasil dihapus.")
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")


        
    if action == "deleteScrap":
        folder_path = os.path.join(os.path.dirname(__file__), 'static', 'datasetscrap')
        try :
            session['image_url'] = None
            session['namafile'] = None
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path,filename)
                if os.path.isfile(file_path) and (filename.lower().endswith('.jpg') or filename.lower().endswith('.png') or filename.lower().endswith('.jpeg')):
                    os.remove(file_path)
            print("Semua file gambar (.jpg dan .png) dalam folder berhasil dihapus.")
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")



    if action =="deletedatabase":
        folder_path = os.path.join(os.path.dirname(__file__), 'static', 'datasets')
        try :
            session['image_url'] = None
            session['namafile'] = None
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path,filename)
                if os.path.isfile(file_path) and (filename.lower().endswith('.jpg') or filename.lower().endswith('.png') or filename.lower().endswith('.jpeg')):
                    os.remove(file_path)
            print("Semua file gambar (.jpg dan .png) dalam folder berhasil dihapus.")
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")
        




    if action == "uploadfile":
        uploaded_files = request.files.getlist('file')

        if uploaded_files:
            # Dapatkan path folder tempat file-file tersebut disimpan
            folder_path = os.path.join(app.config['DATASETS_FOLDER'])  # Ganti dengan path yang sesuai
            os.makedirs(folder_path, exist_ok=True)  # Pastikan folder tempat file disimpan ada

            # Simpan file-file yang diunggah ke dalam folder tempat file disimpan
            for uploaded_file in uploaded_files:
                file_path = os.path.join(folder_path, secure_filename(uploaded_file.filename))
                uploaded_file.save(file_path)

            # List semua file di folder dengan ekstensi .jpg atau .png
            image_files = [file for file in os.listdir(folder_path) if file.lower().endswith(('.jpg', '.png'))]

            # Proses file-file gambar
            array_of_images = []
            for image_file in image_files:
                full_path = os.path.join(folder_path, image_file)
                # Add your logic to handle each image file
                # Misalnya, simpan path ke array_of_images
                array_of_images.append(full_path)
                print('Processing image file:', full_path)

            # Sekarang array_of_images berisi path dari semua file gambar yang diunggah


    
    if action == "Unggah":
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file:
                # Periksa ekstensi file yang diunggah
                allowed_extensions = {'jpg', 'jpeg', 'png'}
                if '.' in uploaded_file.filename and uploaded_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    file_path = os.path.join(app.config['DATASETS_FOLDER'], uploaded_file.filename)
                    current_path = os.path.abspath(__file__)
                    test_path = os.path.join(os.path.dirname(os.path.dirname(current_path)), 'test')
                  
                    uploaded_file.save(file_path)
                  
                    messageunggah = "Berhasil diunggah!"
                    image_url = "static/datasets/" + uploaded_file.filename
                    namafile = uploaded_file.filename
                    shutil.copy(image_url,test_path)

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
        return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, image_list=current_images, num_pages=num_pages, current_page=page, isScrape = session['isScrape'])
            



    # Menghitung jumlah halaman total
    if action == 'Search':
        output_folder = os.path.join(app.config['FILTER_FOLDER'])
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        #refresh
        resetFilter()
        session['filteredImages'] = []
        session['countfiltered'] = 0
   

        
        database_images = []
        image_url = session.get('image_url')
        if (image_url != None):
            query_image = cv2.imread(image_url)
            if (session['isScrape'] == True):
                for img in glob.glob("./static/datasets/*.jpg") + glob.glob("./static/datasetscrap/*.jpg"):
                    n = cv2.imread(img)
                    database_images.append(n)
            else:
                dataset_path = os.path.join(app.config['DATASETS_FOLDER'])
                for img in glob.glob(os.path.join(dataset_path, "*.jpg")):
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
            
            filteredImages = session.get('filteredImages', [])
            # Simpan gambar-gambar hasil filter
            for i, (image, similarity) in enumerate(image_list):
                output_filename = f'result{i + 1}.jpg'
                output_path = os.path.join(output_folder, output_filename)
                cv2.imwrite(output_path, image)
                filteredImages.append((output_path,similarity))
            # Sekarang, baca daftar gambar hasil filter dari direktori 'filter'
            session['filteredImages'] = filteredImages
            countFiltered = len(filteredImages)
            session['countfiltered'] = (countFiltered)
            session['duration'] = float(duration)
            image_list = [os.path.join('static', 'filter', os.path.basename(image_path)) for image_path, similarity in filteredImages]
            current_images = image_list[start_index:end_index]
            session['messageunggah'] = "Search Berhasil!"
            messageunggah = session.get('messageunggah')
            session['jenissearch'] = "Color"
            session['duration'] = round(duration,2)
            session['isSearch'] = True
        else:
            session['messageunggah'] = "Error! Anda mau search apa wkwkwk"
            messageunggah = session.get('messageunggah')


    if action == 'SearchTexture':
        #deklarasi awal / refresh
        resetFilter()
        result = []
        session['filteredImages'] = []
        session['countfiltered'] = 0
        output_folder = os.path.join(app.config['FILTER_FOLDER'])
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        image_url = session.get('image_url')
        if (image_url != None): #ada fotonya
            vec_ref = imgToVector(image_url)
            start = time.time()
            if (session['isScrape'] == True):
                for img in glob.glob("./static/datasets/*.jpg") + glob.glob(".static/datasetscrap/*.jpg"):
                    vec_set = imgToVector(img)
                    similarity = 100 * cosSimilarity(vec_ref,vec_set)
                    n = cv2.imread(img)
                    result.append((n,similarity))
            else:

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



            filteredImages = []
            result.sort(key=lambda x: x[1], reverse=True)
            filteredImages = session.get('filteredImages', [])
            namafile = session.get('namafile')
            for i, (image, similarity) in enumerate(result):
                output_filename = f'result{i + 1}.jpg'
                output_path = os.path.join(output_folder, output_filename)
                cv2.imwrite(output_path, image)
                filteredImages.append((output_path,similarity))
            countFiltered = len(filteredImages)
            image_list = [os.path.join('static', 'filter', os.path.basename(image_path)) for image_path, similarity in filteredImages]
            current_images = image_list[start_index:end_index]
            session['filteredImages'] = filteredImages
            session['messageunggah'] = "Search Berhasil!"
            session['jenissearch'] = "Texture"
            session['countfiltered'] = (countFiltered)
            jenissearch = session.get('jenissearch')
            messageunggah = session.get('messageunggah')
            session['duration'] = round(duration,2)
            session['isSearch'] = True
        else:
            session['messageunggah'] = "Error! Anda mau search apa wkwkwk"
            messageunggah = session.get('messageunggah')


    if (session['isSearch'] == True):
        filteredImages = session.get('filteredImages', [])
        page_size = 12
        page = int(request.args.get('page', 1))  # Halaman saat ini, defaultnya adalah halaman 1
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        # Path ke direktori datasets di dalam folder static
        dataset_dir = app.config['FILTER_FOLDER']
        # Mengambil daftar file gambar dalam direktori datasets
        image_list = [os.path.join('static', 'filter', filename) for filename in os.listdir(dataset_dir) if filename.endswith(('.jpg', '.png', '.jpeg'))]
        # Mengambil daftar gambar untuk halaman saat ini
        current_images = image_list[start_index:end_index]
        num_pages = math.ceil(len(image_list) / page_size)
        # image_list = []
        messageunggah = ""
        image_url = None  # Tetapkan dengan nilai default
        namafile = None
        return render_template('use.html',searchType = session['jenissearch'], countfilter = session['countfiltered'],unggah=messageunggah,num_pages = num_pages,current_page = page, image_url=session['image_url'], namafile=session['namafile'], result =filteredImages ,image_list=current_images, durasi=session['duration'], isScrape = session['isScrape'])

    image_url = session.get('image_url')
    messageunggah = session.get('messageunggah')
    namafile = session.get('namafile')
    enablePages = "True"
    return render_template('use.html', unggah=messageunggah, image_url=image_url, namafile=namafile, image_list=current_images, num_pages=num_pages, current_page=page ,enablepage = enablePages, isScrape = session['isScrape'])

if __name__ == '__main__':
    app.run()
