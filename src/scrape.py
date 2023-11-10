'''
Fungsi Scraping gambar dari website untuk Fitur Bonus
Akan menampilkan error apabila tidak bisa meng-scrap img dari web yang diinginkan
Semua image yang terscrap fixed tersimpan di directory static/datasetscrap ,terpisah dari dataset upload
'''
from PIL import Image
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import os

def scrape_images(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    images = soup.find_all('img')

    directory = 'static/datasetscrap'  # Direktori baru

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Mencari jumlah file yang sudah ada di dalam folder
    existing_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    file_count = len(existing_files)

    # Iterasi dari nomor file terakhir ditambah satu
    for i, image in enumerate(images, start=file_count + 1):
        link = image['src']
        if link.startswith('http'):  # Pastikan URL lengkap
            try:
                im = requests.get(link)
                if im.status_code != 200:  # Cek kode status HTTP
                    raise requests.RequestException(f"Failed to download image {link}: HTTP status code {im.status_code}")

                # Menggunakan try-except untuk menangani 'NoneType' saat membuka gambar
                try:
                    img = Image.open(BytesIO(im.content))
                except:
                    print(f"Failed to open image {link}")
                    continue  # Melanjutkan iterasi jika gambar tidak dapat dibuka
                
                img.verify()  # Verifikasi gambar
                image_path = os.path.join(directory, f"result_{i}.jpg")  # Path gambar di dalam direktori baru
                with open(image_path, 'wb') as f:
                    f.write(im.content)
            except requests.RequestException as e:
                print(e)  # Tampilkan pesan kesalahan
                with open("error_log.txt", 'a') as error_file:
                    error_file.write(f"Failed to download image {link}: {e}\n")
                # Kembalikan pesan yang sesuai
                with open("error_image.txt", 'a') as error_img_file:
                    error_img_file.write(f"Tidak bisa mengunduh gambar: {link}\n")

# Memanggil fungsi dengan URL yang diinginkan
# scrape_images('https://journeythrough.org/courses/john/lessons/day-3-6/')
