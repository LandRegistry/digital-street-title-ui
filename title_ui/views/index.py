from datetime import datetime

import requests
from flask import Blueprint, current_app, render_template, request

# This is the blueprint object that gets registered into the app in blueprints.py.
index = Blueprint('index', __name__)


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

    return render_template('app/index.html', titles=titles, title_number=title_number, error=None)


def process(titles):
    placeholders = [
        {"str": "*CD*", "field": "charge/date"},
        {"str": "*CP*", "field": "charge/lender/organisation"}
    ]

    for title_idx, title in enumerate(titles):
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
