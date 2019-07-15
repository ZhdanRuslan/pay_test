from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        print('GET')
        return render_template('index.html')
    if request.method == 'POST':
        print('POST')
        return render_template('tst.html')
