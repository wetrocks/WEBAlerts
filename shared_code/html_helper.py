from lxml import html
import logging
import unicodedata
import re

WHITESPACE_REGEX = re.compile(r"\s+")

def extract_maintenance_links(htmlstr: str) -> list:
    page_tree = html.document_fromstring(htmlstr)

    maintenance_section = page_tree.xpath("body/main//h4[text() = 'Maintenance']/../../..")

    links = maintenance_section[0].xpath(".//@href")
    
    # card title is a link as well as the "read more" link, so dedup
    return list(dict.fromkeys(links))


def extract_interruption_info(htmlstr: str) -> dict:
  
    page_tree = html.document_fromstring(htmlstr)

    main_element = page_tree.xpath("body//main[1]")
    if len(main_element) != 1:
        logging.warning("No main element found")
        return None

    main_element = main_element[0]
    # pull out the title
    title = "".join(main_element.xpath("header[1]/h1[1]/text()"))

    content =  "<html><body>{}</body></html>".format(WHITESPACE_REGEX.sub(" ", html.tostring(main_element, encoding=str) ))

    interruption_info = { 
        "title": title,
        "content": content
    }

    return interruption_info