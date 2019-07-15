from flask import Flask, render_template, request
import hashlib

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():

    currency_dict = {
        'EUR': 978,
        'USD': 840,
        'RUB': 643,
    }


    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        currency = request.form.get('currency')
        sum = request.form.get('sum')
        result_hash = (sum + ':' + str(currency_dict.get(currency)) + ':5:101SecretKey01').encode()
        sign = hashlib.sha256(result_hash).hexdigest()
        if currency:
            return render_template('tst.html', currency=currency, sum = sum, sign = sign)
