from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
def main():
    message = "Hello from Flask!"
    return render_template('main.html', message=message)

@app.route('/about')
def about():
    message = "About!"
    return render_template('about.html',message=message)

if __name__ == '__main__':
    app.run()
