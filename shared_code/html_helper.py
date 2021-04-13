from lxml import etree, html
import logging

def extract_interruption_info(htmlstr: str) -> dict:
    page_tree = html.fromstring(htmlstr)
    main_element = page_tree.xpath("body//main[1]")
    if len(main_element) != 1:
        logging.warning("No main element found")
        return ""

    main_element = main_element[0]
    # pull out the title
    title = "".join(main_element.xpath("h1[1]/text()"))
    
    # remove paragraphs that have a child img
    for pimg in main_element.xpath("//p/img"):
        pimg.getparent().remove(pimg)
    
    content =  "<html><body>{}</body></html>".format(str(etree.tostring(main_element, encoding=str)))

    interruption_info = { 
        "title": title,
        "content": content
    }

    return interruption_info