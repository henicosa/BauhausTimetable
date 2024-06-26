from flask import Flask, Response, render_template, jsonify, request, abort

import schedule
import time

import subprocess

import datetime
import pytz

import crawler

import json

def read_json(path):
    with open(path) as f:
        return json.load(f)

app = Flask(__name__)

settings = read_json("application.json")


program_status = "not running"

'''
-----------------------------------------------------

Section for App-specific functions

-----------------------------------------------------
'''
import qrcode
import qrcode.image.svg

def generate_qr_svg(url):

    factory = qrcode.image.svg.SvgImage
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white", image_factory=qrcode.image.svg.SvgPathImage,attrib={'class': 'qrcode'})
    # return svg
    return img.to_string(encoding='unicode')

import requests
from bs4 import BeautifulSoup


def get_current_calendar_week():
    return datetime.date.today().isocalendar()[1]

@app.route('/qrtest')
def qrtest():
    return generate_qr_svg("https://bison.uni-weimar.de/qisserver/rds?state=wplan&act=Raum&pool=Raum&show=plan&P.vx=kurz&raum.rgid=2882")

# route for the eink display, with query parameters for the room ids
@app.route('/raum', methods=['GET'])
@app.route('/', methods=['GET'])
def web():
    room_ids = request.args.get('room_ids', default="2882,2883,2881,2884", type=str).split(",")
    building_name = request.args.get('building_name', default="Unbenanntes Gebäude", type=str)
    display_type = request.args.get('display_type', default="online", type=str)
    current_time = request.args.get('current_time', default=datetime.datetime.now().strftime("%Y-%m-%d"), type=str)
    current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d")
    
    print("Looking for events on the date: " + str(current_time))

    template_path = "online.html"
    if display_type == "online":
        template_path = "online.html"
    elif display_type == "eink":
        template_path = "eink.html"
    elif display_type == "dark_eink":
        template_path = "eink-black.html"

    # get full url with query parameters
    url = request.url

    # replace domain with production domain
    production_domain = settings["production_domain"]
    url = url.split("://")[1]
    url = url.split("/", 1)[1]
    url = production_domain + url
    # generate_qr_svg(url)
    building = {"name": building_name, "id": "2882", "qrcode" : ""}

    events = crawler.get_events(room_ids, current_time.date())

    # get current time in berlin timezone
    current_time = datetime.datetime.now()
    current_time = current_time.astimezone(pytz.timezone('Europe/Berlin'))
    current_time_str = current_time.strftime("%d.%m.%Y %H:%M")
    return render_template(template_path, building=building, events=events, last_update=current_time_str)


'''
-----------------------------------------------------

Section for template functions

-----------------------------------------------------
'''

@app.errorhandler(404)
def page_unavailable_for_legal_reasons(error):
    errorinfo = {"code": 404,
                 "explanation_de": "Sorry. Diese Seite gibt es nicht. Oder sie gab es mal und jetzt fehlt sie.",
                 "explanation_en": "Sorry. This site does not exist. Or it existet and is gone now."}
    return render_template('error.html', appinfo=settings, error=errorinfo), 404

@app.route('/about')
def about():
    return render_template('appinfo.html', appinfo=settings)


@app.route('/status')
def status():
    global program_status
    return jsonify(status=program_status)


@app.route('/activate', methods=['POST'])
def activate():
    global program_status
    if program_status == "success":
        return jsonify(status='already running')
    program_running = True
    if start():
        program_status = "success"
    else:
        program_status = "failed"
    return jsonify(status=program_status)

def start():
    time.sleep(5)
    # code for your function goes here
    subprocess.Popen(["python", "app/main.py"]) 
    print("Calendar initialized")
    return True

if __name__ == '__main__':
    app.run()