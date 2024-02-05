from datetime import datetime
from src.util.StringCleanUtil import clean_text_name

'''
This function is used to parse a date string into a datetime object.
'''
def parseisodate(date_str, _ ):
    return datetime.fromisoformat(date_str)

date_formats = [
    { "format": "", "function": parseisodate },
    { "format": "%m/%d/%y", "function": datetime.strptime },
    { "format": "%Y-%m-%dT%H:%M:%S%z", "function": datetime.strptime },
    { "format": "%Y-%m-%dT%H:%M:%S.%fZ", "function":  datetime.strptime },
    { "format": "%d-%b-%y", "function": datetime.strptime },
    { "format": "%B %d, %Y At %I:%M %p", "function": datetime.strptime },
    { "format": "%m/%d/%y %H:%M", "function": datetime.strptime },
    { "format": "'%b %d, %Y at %I:%M%p %Z", "function": datetime.strptime },
    { "format": "%Y-%m-%dT%H:%M:%S.%fZ", "function": datetime.strptime },
    { "format": "%Y-%m-%dT%H:%M:%S.%f", "function": datetime.strptime },
    { "format": "%Y-%m-%dT%H:%M:%S", "function": datetime.strptime },
    { "format": "%Y-%m-%dT%H:%M:%S.%f%z", "function": datetime.strptime },
    { "format": "%b. %d %Y", "function": datetime.strptime },
    { "format": "Publicación %d de %B %Y", "function": datetime.strptime },
    { "format": "%d Publicación %d de %B de %Y", "function": datetime.strptime },
    { "format": "visited %b. %d %Y", "function": datetime.strptime },
    { "format": "%d %b. %d %Y (archived)", "function": datetime.strptime },
    { "format": "Publicación %d de %B de %Y", "function": datetime.strptime },
    { "format": "%d %b. %d %Y.", "function": datetime.strptime },
    { "format": "%b. %d %Y.", "function": datetime.strptime },
    { "format": "Publicación %d de %B", "function": datetime.strptime },
    { "format": "%b %d %Y", "function": datetime.strptime },
    { "format": "%b %d %Y (archived)", "function": datetime.strptime },
    { "format": "%B %d, %Y", "function": datetime.strptime },
]

def try_parse_multi_date(date_str):
    if date_str == "": return None
    date_str_clean = clean_text_name(date_str).strip()
    for date_format in date_formats:
        try:
            return date_format["function"](date_str, date_format["format"])
        except Exception as e:
            pass
        try:
            return date_format["function"](date_str_clean, date_format["format"])
        except Exception as e:
            pass

    return None