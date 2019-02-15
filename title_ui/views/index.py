from datetime import datetime
from babel import numbers
import requests
import json
import os.path
from flask import Blueprint, current_app, render_template, request

# This is the blueprint object that gets registered into the app in blueprints.py.
index = Blueprint('index', __name__)

extras_filepath = 'extras.json'


@index.route("/")
def index_page():
    headers = {'Accept': 'application/json'}

    title_number = None
    titles = None

    if request.args.get('title_number'):
        title_number = request.args.get('title_number')

        r = requests.get(current_app.config['TITLE_API_URL'] + '/titles/' + title_number,
                         headers=headers)
        try:
            r.raise_for_status()
        except requests.exceptions.RequestException:
            return render_template('app/index.html', titles=None, title_number=None, error=r.text)

        titles = []
        titles.append(r.json())

        if not titles:
            return render_template('app/index.html', titles=None, title_number=None, error="Cannot find title")

        title = process(titles)[0]

        title['updated_at_date'] = datetime.strptime(title['updated_at'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%d %B %Y')
        title['updated_at_time'] = datetime.strptime(title['updated_at'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%H:%M:%S')

        extras = None
        if os.path.isfile(extras_filepath):
            with open(extras_filepath) as json_file:
                extras = json.load(json_file)

        return render_template('app/single-title.html', title=title, extras=extras, title_number=title_number)
    elif request.args.get('owner_email_address'):
        r = requests.get(current_app.config['TITLE_API_URL'] + '/titles',
                         params={"owner_email_address": request.args.get('owner_email_address')},
                         headers=headers)
        try:
            r.raise_for_status()
        except requests.exceptions.RequestException:
            return render_template('app/index.html', titles=None, title_number=None, error=r.text)

        titles = r.json()

        if titles:
            titles = process(titles)

        return render_template('app/multi-title.html', titles=titles, title_number=title_number, error=None)

    return render_template('app/index.html', titles=None, title_number=None, error=None)


def process(titles):
    placeholders = [
        {"str": "*CD*", "field": "charge/date"},
        {"str": "*CP*", "field": "charge/lender/organisation"}
    ]

    for title_idx, title in enumerate(titles):
        if not title['updated_at']:
            titles[title_idx]['updated_at'] = title['created_at']

        for price_idx, price in enumerate(title['price_history']):
            titles[title_idx]['price_history'][price_idx]['price_pretty'] = numbers.format_currency(
                price['amount'] / 100,
                price['currency_code']
            ).replace(".00", "")

            date_pretty = datetime.fromtimestamp(price['date']).strftime('%d %B %Y')
            titles[title_idx]['price_history'][price_idx]['date_pretty'] = date_pretty

            date_full_pretty = datetime.fromtimestamp(price['date']).strftime('%d %B %Y %H:%M:%S')
            titles[title_idx]['price_history'][price_idx]['date_full_pretty'] = date_full_pretty

        for restriction_idx, restriction in enumerate(title['restrictions']):
            if 'charge' in restriction:
                titles[title_idx]['charges'].append(restriction['charge'])
                charge_id = str(title_idx) + str(restriction_idx)
                titles[title_idx]['restrictions'][restriction_idx]['charge']['html_id'] = charge_id

            for placeholder in placeholders:
                fields = placeholder['field'].split('/')

                restriction_temp = restriction
                for field in fields:
                    if field in restriction_temp:
                        if field == 'date':
                            date_obj = datetime.strptime(restriction_temp[field], '%Y-%m-%dT%H:%M:%S.%f')
                            value = datetime.strftime(date_obj, '%d %B %Y')
                        else:
                            value = restriction_temp[field]

                        restriction_temp = value
                    else:
                        restriction_temp = None
                        break

                if restriction_temp:
                    text = restriction['restriction_text'].replace(placeholder['str'],
                                                                   str(restriction_temp))
                    titles[title_idx]['restrictions'][restriction_idx]['restriction_text'] = text
    return titles
