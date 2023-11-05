from flask import Flask, render_template, request
from tes import findnumber
app = Flask(__name__)
@app.route('/')
def main():
    message = "Hello from Flask!"
    return render_template('main.html', message=message)

@app.route('/about')
def about():
    message = "About!"
    angka = findnumber(31233)
    return render_template('about.html',message=message ,angka=angka) 

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file:
            file_path = f"uploads/{uploaded_file.filename}"
            uploaded_file.save(file_path)
            messageunggah = "Berhasil diunggah!"
            return render_template('main.html',unggah=messageunggah) 

    return render_template('main.html')

    
@app.route('/use')
def use():
    return render_template('use.html')


if __name__ == '__main__':
    app.run()


