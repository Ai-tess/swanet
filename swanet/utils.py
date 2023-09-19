import re
import requests
from bs4 import BeautifulSoup

html_char = ['"<<s>>"', '\t"<s>" { <s> }', '"<<p>>"', '\t"<p>" { <p> }',\
              '"<<s>>"', '\t"<s>" { <s> } ']

def get_soup_object(url, parser="html.parser"):
    """
        get soup object
    """
    return BeautifulSoup(requests.get(url, timeout=200).text, parser)


def get_tag_object(word):
    """
        gets tag object
    """
    try:
        data = get_soup_object(f"http://77.240.23.241/tagger/basic/{word}")
        section = data.find('textarea', {'id': "tagger_outputText"})
        return section.string
    except RuntimeError:
        return None


def tag(word):
    """
        get tag from the json response and append into a new list

    """
    tags = []
    tag_s = get_tag_object(word).split('\n')
    ntag = [value for value in tag_s if value not in html_char]
    for i in range(0, len(ntag), 2):
        tag_list = ntag[i+1].split()
        tags.append((re.sub(r'[$*"":,]+', '', tag_list[0]), tag_list[1].replace('{', '.')))
    return tags
