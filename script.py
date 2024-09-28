import yaml
import datetime
import pytz

import crawler

import json

def read_json(path):
    with open(path) as f:
        return json.load(f)

settings = read_json("application.json")

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


def get_current_calendar_week():
    return datetime.date.today().isocalendar()[1]


from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader("templates"))

def generate_eink_html(rooms=[], 
                       building_name="Unbenanntes Gebäude", 
                       current_time=datetime.datetime.now().strftime("%Y-%m-%d")):
    
    # convert current_time string to datetime object
    current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d")
    print("Looking for events on the date: " + str(current_time))

    # replace domain with production domain
    production_domain = settings["production_domain"]
    url = production_domain + "test.html"
    # generate_qr_svg(url)

    building = {"name": building_name, "id": "2882", "qrcode" : ""}

    events = crawler.get_events(rooms, current_time.date())

    # get current time in berlin timezone
    current_time = datetime.datetime.now()
    current_time = current_time.astimezone(pytz.timezone('Europe/Berlin'))
    current_time_str = current_time.strftime("%d.%m.%Y %H:%M")

    html_files = {}

    # Load the template
    template = env.get_template("online.html")
    # Render the template with the desired variables
    html_files["online"] = template.render(building=building, events=events, last_update=current_time_str)

    # Load the template
    template = env.get_template("eink.html")
    # Render the template with the desired variables
    html_files["eink"] = template.render(building=building, events=events, last_update=current_time_str)

    # Load the template
    template = env.get_template("eink-black.html")
    # Render the template with the desired variables
    html_files["eink_dark"] = template.render(building=building, events=events, last_update=current_time_str)

    return html_files


# read all groups from the yaml file
def read_groups():
    with open("groups.yaml") as f:
        return yaml.safe_load(f)

# go through all groups and generate the html files in the output folder
for group in read_groups():
    filename = group["filename"]
    for room in group["rooms"]:
        room["id"] = str(room["id"])
    htmls = generate_eink_html(rooms=group["rooms"], building_name=group["group_name"], current_time="2024-10-14")

    output_folder = settings["html_output_folder"]

    # write the html to a file
    with open(f"{output_folder}/{filename}_eink.html", "w") as f:
        f.write(htmls["eink"])
    with open(f"{output_folder}/{filename}_eink_dark.html", "w") as f:
        f.write(htmls["eink_dark"])
    with open(f"{output_folder}/{filename}.html", "w") as f:
        f.write(htmls["online"])
