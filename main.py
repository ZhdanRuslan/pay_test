import hashlib
import logging
import datetime

from flask import Flask, render_template, request, redirect
import requests

from settings import SEKRET_KEY, currency_code, ref_for_rub, ref_for_eur

app = Flask(__name__)


def generate_sign(amount=None, currency=None, requested_json=None):
    # generate for pay in EUR
    if requested_json is None:
        result_hash = (amount + ':' + currency + ':5:101' + SEKRET_KEY).encode()
        sign = hashlib.sha256(result_hash).hexdigest()
        app.logger.info('Generate sign for base case with EUR')
        return sign
    else:
        # generate sign for another cases USD/RUB
        sorted_json_keys = sorted(requested_json.keys())
        res_str = ''
        for key in sorted_json_keys:
            res_str += ':'
            res_str += str(requested_json[key])

        res_str += SEKRET_KEY
        sign = hashlib.sha256(res_str[1:].encode()).hexdigest()
        app.logger.info('Generate sign for other cases USD/RUB')
        return sign


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        currency = request.form.get('currency')
        amount = request.form.get('amount')
        description = request.form.get('description')
        decimal_currency = str(currency_code.get(currency))

        # EUR
        if currency == 'EUR':
            sign = generate_sign(amount, decimal_currency)
            logging.info('Currency: {}, Amount: {}, Time: {}, Description: {}, ID: {}'.format(currency, amount,
                                                                                              datetime.datetime.now(),
                                                                                              description, None))
            return render_template('pay_eur.html', currency=decimal_currency, amount=amount, sign=sign,
                                   ref_for_eur=ref_for_eur)
        # USD
        if currency == 'USD':

            requested_json = {"payer_currency": decimal_currency,
                              "shop_amount": "{}".format(amount),
                              "shop_currency": decimal_currency,
                              "shop_id": "5",
                              "shop_order_id": 123456,
                              }

            sign = generate_sign(amount, decimal_currency, requested_json)
            res = requests.post('https://core.piastrix.com/bill/create', json={"payer_currency": decimal_currency,
                                                                               "shop_amount": "{}".format(amount),
                                                                               "shop_currency": decimal_currency,
                                                                               "shop_id": "5",
                                                                               "shop_order_id": 123456,
                                                                               "sign": "{}".format(sign)
                                                                               })
            if res.ok:
                url = res.json()['data']['url']

                logging.info('Currency: {}, Amount: {}, Time: {}, Description: {}, ID: {}'.format(currency, amount,
                                                                                                  res.json()['data'][
                                                                                                      'created'],
                                                                                                  description,
                                                                                                  res.json()['data'][
                                                                                                      'id']))
                return redirect(url)

        # RUB
        if currency == 'RUB':
            requested_json = {
                "amount": "{}".format(amount),
                "currency": decimal_currency,
                "payway": "payeer_rub",
                "shop_id": "5",
                "shop_order_id": "123456",
            }

            sign = generate_sign(amount, decimal_currency, requested_json)
            res = requests.post('https://core.piastrix.com/invoice/create', json={
                "amount": "{}".format(amount),
                "currency": decimal_currency,
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

                logging.info('Currency: {}, Amount: {}, Time: {}, Description: {}, ID: {}'.format(currency, amount,
                                                                                                  datetime.datetime
                                                                                                  .now(),
                                                                                                  description,
                                                                                                  res.json()['data'][
                                                                                                      'id']))

                return render_template('pay_rub.html', lang=lang, m_curorderid=m_curorderid,
                                       m_historyid=m_historyid, m_historytm=m_historytm, referer=referer, method=method,
                                       ref_for_rub=ref_for_rub)


if __name__ == '__main__':
    logging.basicConfig(filename='logfile.log', level=logging.INFO)
    app.run(debug=True)
