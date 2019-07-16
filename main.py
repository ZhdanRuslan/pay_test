import hashlib

from flask import Flask, render_template, request
from werkzeug.utils import redirect
import requests

from forms.pay_forms import PayForm
from settings import SEKRET_KEY

app = Flask(__name__)


def generate_sign(amount=None, currency=None, requested_json=None):
    # generate for pay in EUR
    if requested_json is None:
        result_hash = (amount + ':' + currency + ':5:101' + SEKRET_KEY).encode()
        sign = hashlib.sha256(result_hash).hexdigest()
        return sign
    else:
        # generate sign for another cases
        sorted_json_keys = sorted(requested_json.keys())
        res_str = ''
        for key in sorted_json_keys:
            res_str += ':'
            res_str += str(requested_json[key])

        res_str += SEKRET_KEY
        sign = hashlib.sha256(res_str[1:].encode()).hexdigest()
        return sign


@app.route('/', methods=['GET', 'POST'])
def main():
    form = PayForm()
    currency = request.form.get('currency')
    amount = request.form.get('amount')

    if request.method == 'GET':
        return render_template('index.html', form=form)
    if request.method == 'POST':
        # EUR
        if currency == '978':
            sign = generate_sign(amount, currency)
            return render_template('pay_eur.html', currency=currency, amount=amount, sign=sign)
        # USD
        if currency == '840':
            requested_json = {"payer_currency": currency,
                              "shop_amount": "{}".format(amount),
                              "shop_currency": currency,
                              "shop_id": "5",
                              "shop_order_id": 123456,
                              }

            sign = generate_sign(amount, currency, requested_json)
            res = requests.post('https://core.piastrix.com/bill/create', json={"payer_currency": currency,
                                                                               "shop_amount": "{}".format(amount),
                                                                               "shop_currency": currency,
                                                                               "shop_id": "5",
                                                                               "shop_order_id": 123456,
                                                                               "sign": "{}".format(sign)
                                                                               })
            if res.ok:
                url = res.json()['data']['url']
                return redirect(url)

        if currency == '643':
            requested_json = {
                "amount": "{}".format(amount),
                "currency": currency,
                "payway": "payeer_rub",
                "shop_id": "5",
                "shop_order_id": "123456",
            }

            sign = generate_sign(amount, currency, requested_json)
            res = requests.post('https://core.piastrix.com/invoice/create', json={
                "amount": "{}".format(amount),
                "currency": currency,
                "payway": "payeer_rub",
                "shop_id": "5",
                "shop_order_id": "123456",
                "sign": sign
            })
            if res.ok:
                url = res.json()
                lang = url['data']['data']['lang']
                m_curorderid = url['data']['data']['m_curorderid']
                m_historyid = url['data']['data']['m_historyid']
                m_historytm = url['data']['data']['m_historytm']
                referer = url['data']['data']['referer']
                method = url['data']['method']

                return render_template('pay_rub.html', lang=lang, m_curorderid=m_curorderid,
                                       m_historyid=m_historyid, m_historytm=m_historytm, referer=referer, method=method)


if __name__ == '__main__':
    app.run(debug=True)
