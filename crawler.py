import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
import os

import logging

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logg(level="info", msg=""):
    if level == "info":
        logger.info(msg)
    elif level == "error":
        logger.error(msg)
    elif level == "warning":
        logger.warning(msg)
    print(level.upper() + ": " + msg)

from datetime import datetime, timedelta, date

# url = "http://bison-connector.bauhaus.uni-weimar.de/qisserver/rds?state=wplan&raum.rgid=[raumid]&week=[calendar_week]_[year]&act=Raum&pool=Raum&show=plan&P.vx=lang&fil=plu&P.subc=plan"
url = "https://bison.uni-weimar.de/qisserver/rds?state=wplan&raum.rgid=[raumid]&week=[calendar_week]_[year]&act=Raum&pool=Raum&show=plan&P.vx=lang&fil=plu&P.subc=plan"

days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

room_abbreviations = json.load(open("room_abbreviations.json"))

def is_cashed(course_id):
    cache_path = "cache/" + course_id + ".json"
    return os.path.exists(cache_path)


def get_html(url):
    print("Fetching " + url)
    return requests.get(url).text


def format_string(string):
    return string.replace("\t", "").replace("\n", "").replace(",", "").strip()


def get_course_details(event):
    link = event["link"]
    
    try:
        course_id = link.split("publishid=")[1]
        course_id = course_id.split("&")[0]
    except:
        print("No course ID found for " + link)
        course_id = None

    if not course_id:
        return event

    if is_cashed(course_id):
        return json.load(open("cache/" + course_id + ".json"))

    html_code = get_html(link)
    soup = BeautifulSoup(html_code, 'html.parser')
    name_de = format_string(soup.find("h1").get_text().replace("- Einzelansicht", ""))
    name_en = get_english_event_name(event["link"])

    title = {}

    if name_de != name_en:
        title["german"] = name_de
        title["english"] = name_en
    else: 
        title["multilingual"] = name_de

    event["title"] = title
    
    event["course_id"] = format_string(soup.find('td', class_='mod_n_basic', headers='basic_3').get_text())
    event["event_type"] = format_string(soup.find('td', class_='mod_n_basic', headers='basic_1').get_text())

    event["people"] = extract_persons_info(soup)

    # cache event
    json.dump(event, open("cache/" + course_id + ".json", "w"), indent=4)

    return event


def get_english_event_name(link):
    link += "&language=en"
    html_code = get_html(link)
    soup = BeautifulSoup(html_code, 'html.parser')
    name = soup.find("h1").get_text().replace("- Single View", "")
    return format_string(name)


def add_hours_to_day(current_date, time_to_add):
    # Combine current date with time_to_add
    combined_datetime = datetime.combine(current_date, datetime.strptime(time_to_add, "%H:%M").time())
    return combined_datetime

def weekday_to_german(weekday):
    translationtable = {
        "Mon": "Mo.",
        "Tue": "Di. / Tue.",
        "Wed": "Mi. / Wed.",
        "Thu": "Do. / Thu.",
        "Fri" : "Fr.",
        "Sat": "Sa.",
        "Sun": "So. / Sun."
    }

    if weekday in translationtable:
        return translationtable[weekday]
    else:
        return weekday
    
def get_full_datestring(dt):
    return weekday_to_german(dt.strftime("%a")) + " " + dt.strftime("%d.%m.%Y, %H:%M")

def format_datetime(dt, time_format="%Y-%m-%d %H:%M"):
    return {
        "dateformat1": dt.strftime(time_format),
        "dateformat2": dt.isoformat(),
        "unixtime": int(dt.timestamp()),
        "dateformat_readable": get_full_datestring(dt)
    }

def generate_timeformats(start_datetime, end_datetime):
    start = format_datetime(start_datetime)
    end = format_datetime(end_datetime, time_format="%Y-%m-%d %H:%M")

    # Check if end date is on the same day as start date
    same_day = start_datetime.date() == end_datetime.date()

    if same_day:
        end["dateformat_readable"] = end_datetime.strftime("%H:%M Uhr")
    else:
        # Customize the format_readable for different days if needed
        end["dateformat_readable"] = get_full_datestring(end_datetime)

    result = {
        "start": start,
        "end": end
    }

    return result


def extract_persons_info(soup):
    # Find the table with the specified summary attribute
    table = soup.find('table', summary='Verantwortliche Dozenten')

    # Initialize a list to store person information
    persons_list = []

    # Check if the table is found
    if table:
        # Find all rows in the table body
        rows = table.find_all('tr')

        # Iterate over rows to extract information
        for row in rows:
            # Find cells in the row
            cells = row.find_all('td')

            # Extract information from each cell
            if len(cells) == 2:
                name_cell, role_cell = cells
                name_link = name_cell.find('a')
                if name_link:
                    person_name = ' '.join(name_link.get_text().split()).split(", ")
                    if len(person_name) > 1:
                        if len(person_name) > 2:
                            formatted_person_name = ' '.join(person_name[2:]) + " " + format_string(person_name[1]) + " " + format_string(person_name[0])
                        else:
                            formatted_person_name = format_string(person_name[1]) + " " + format_string(person_name[0])
                        person_link = name_link['href']
                        person_role = ' '.join(role_cell.get_text().split())

                        # Append person information to the list
                        persons_list.append({
                            "name": formatted_person_name,
                            "link": person_link,
                            "role": person_role
                        })

    return persons_list


def extract_events(html_code, day):
    soup = BeautifulSoup(html_code, 'html.parser')

    # Get weekday (0-6, where Monday is 0)
    weekday = day.weekday()

    # get first day of the week
    first_day_of_week = day - timedelta(days=weekday)


    # 
    # Process Location
    #
    location = {}
    location_soup = soup.find_all("table")[3].find("a")
    location["link"] = location_soup["href"]
    location["building"] = format_string(location_soup.get_text()).split(" - ")[0]
    room = {}
    full_name = format_string(location_soup.get_text()).split(" - ")[1]
    room["full_name"] = full_name
    room["abbr_name"] = {}
    #abbr_name = full_name.replace("(Hörsaal ansteigend)", "")
    #abbr_name = abbr_name.replace("Hörsaal", "<abbr title='Hörsaal / Auditorium'>HS</abbr>")
    
    # TODO: make sure that the room_id is correct
    room_id = location["link"].split("raum.rgid=")[1]

    abbr_name = room_abbreviations[room_id]
    room["abbr_name"]["html"] = abbr_name
    location["room"] = room


    # get second table
    timetable = soup.find_all('table')[4]
    # get all td with class plan2
    event_tables = timetable.find_all('td', class_='plan2')
    event_tables = [event_table.find_all("td") for event_table in event_tables]
    events = []

    for event_table in event_tables:
        event = {}

        #
        # get time information
        #
        time_information = event_table[1].get_text().split(",")
        time_information = [info.strip() for info in time_information]

        # fetch additional course information
        event["link"] = event_table[0].find("a")["href"]
        event = get_course_details(event)

        

        try:
            time = {}
            time["day"] = time_information[0]
            current_base_date = first_day_of_week + timedelta(days=days.index(time["day"]))

            start_dt = add_hours_to_day(current_base_date, time_information[1].split(" - ")[0])
            end_dt = add_hours_to_day(current_base_date, time_information[1].split(" - ")[1])

            formatted_time = generate_timeformats(start_dt, end_dt)

            time["start"] = formatted_time["start"]

            time["end"] = formatted_time["end"]

            if len(time_information) > 2:
                time["repeat_type"] = time_information[2]
            else:
                time["repeat_type"] = None

            event["time"] = time
        except:
            logg("error","Error processing time information " + str(time_information))
            continue

        # unreliable event type extraction
        """
        if len(event_table) > 2:
            event["event_type"] = format_string(event_table[2].get_text())
        else:
            event["event_type"] = None
        """
        if len(event_table) > 3:
            for i in range(3, len(event_table)):
                current_info = event_table[i]
                # get host information from course website
                #if "Lehrperson" in event_table[i].get_text():
                #    hosts = []
                #    for link in current_info.find_all("a"):
                #        host = {}
                #        host["host"] = format_string(link.get_text().replace(",", "").strip())
                #       host["host_link"] = link["href"]
                #        hosts.append(host)
                #    event["hosts"] = hosts
                if "Einrichtung" in event_table[i].get_text():
                    institutions = []
                    for link in current_info.find_all("a"):
                        institution = {}
                        institution["institution"] = format_string(link.get_text())
                        institution["institution_link"] = link["href"]
                        if institution["institution"] != "":
                            institutions.append(institution)
                    event["institutions"] = institutions


        event["location"] = location

        events.append(event)

    return events


def get_events(rooms, day_of_interest):

    # Get weekday (0-6, where Monday is 0)
    year = day_of_interest.year

    # Get calendar week
    calendar_week = day_of_interest.isocalendar()[1]

    url_template = url.replace("[year]", str(year))
    url_template = url_template.replace("[calendar_week]", str(calendar_week))

    events = []

    for room in rooms:
        room_id = room["id"]
        
        # get html code
        url_to_fetch = url_template.replace("[raumid]", room_id)
        html_code = get_html(url_to_fetch)

        # check if room_id is cached:
        used_cached_version = False
        if os.path.exists("cache/room_" + room_id + ".json"):
            cached_room = json.load(open("cache/rooms/" + room_id + ".json"))
            if datetime.now() - datetime.strptime(cached_room["last_time_updated"], "%Y-%m-%d %H:%M:%S") < timedelta(hours=8):
                print("Using cached room " + room_id)
                events += cached_room["events"]
                used_cached_version = True

        
        if not used_cached_version:
            events += extract_events(html_code, day_of_interest)
            # update only if time is relevant
            if abs(datetime.now() - add_hours_to_day(day_of_interest, "00:00")) < timedelta(days=2):
                print("Cache room " + room_id + " for next query.")
                json.dump({"last_time_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                           , "events": events}, open("cache/rooms/" + room_id + ".json", "w"), indent=4)
        
        # convert date to unixtime timestamp at midnight
        day_of_interest_timestamp = add_hours_to_day(day_of_interest, "00:00").timestamp()
        events = [event for event in events if event["time"]["end"]["unixtime"] > day_of_interest_timestamp]
        print("Processed Raum " + room_id)

    # if current_date equals day_of_interest remove all events that end before the current time
    if day_of_interest == datetime.now().date():

        # get current_time
        current_time = datetime.now()
        # override current_time for testing with 2024-04-10 12:00
        # current_time = datetime(2024, 4, 10, 13, 0)

        # remove all events that end before the current time using unixtime
        events = [event for event in events if event["time"]["end"]["unixtime"] > current_time.timestamp()]
        
    # sort events by time
    events.sort(key=lambda x: x["time"]["start"]["unixtime"])

    return events

