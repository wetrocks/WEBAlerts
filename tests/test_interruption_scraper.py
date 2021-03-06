from shared_code import html_helper
from lxml import etree, html

class TestInterruptionScraper:

    int_html = \
    '''<html lang="en-US">
        <head></head>
        <body>
            <nav>...</nav>
            <div class="wrapper wrapper--page mm-page mm-slideout" id="mm-0">
            <header class="header">...</header>
            <div class="default centered">
            <main role="main">
                {title_element}
                <p>Usually summary with location:</p>
                <p><strong>Date:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Saturday&nbsp; march 27<sup>th&nbsp;</sup> to Friday April 23<sup>rd</sup></strong><strong>, 2021</strong></p>
                <p><strong>Time:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 06:00 </strong><strong>in the morning </strong><strong>– 19:00 </strong><strong>o’clock in the evening</strong></p>
                <p>Details about interruption</p>
                <p>More details...</p>
                <p>Maybe even more...</p>
                <p><img loading="lazy" class="alignnone size-medium wp-image-11389" src="https://www.weirdwordpressimgtag.com/pic.jpg" alt="" width="207" height="300" sizes="(max-width: 207px) 100vw, 207px"></p>
                <p>&nbsp;</p>
            </main>
            </div>
            <footer>...</footer>
        </html>'''

    def test_date_formatting(self):
        html_str = self.int_html.format(title_element="<h1>Title Text</h1>")

        info = html_helper.extract_interruption_info(html_str)

        html_tree = html.fromstring(info["content"])
        date_element = html_tree.xpath("//main/p[contains(string(), 'Date:')]")
        date_str = etree.tostring(date_element[0], encoding=str).strip()

        expectedDate = "<p><strong>Date: Saturday march 27<sup>th </sup> to Friday April 23<sup>rd</sup></strong><strong>, 2021</strong></p>"

        assert expectedDate == date_str

    def test_time_formatting(self):
        html_str = self.int_html.format(title_element="<h1>Title Text</h1>")

        info = html_helper.extract_interruption_info(html_str)

        html_tree = html.fromstring(info["content"])        
        time_element = html_tree.xpath("//main/p[contains(string(), 'Time:')]")
        time_str = etree.tostring(time_element[0], encoding=str).strip()

        expectedTime = "<p><strong>Time: 06:00 </strong><strong>in the morning </strong><strong>– 19:00 </strong><strong>o’clock in the evening</strong></p>"

        assert expectedTime == time_str

    def test_extract_title(self):
        html_str = self.int_html.format(title_element="<h1>Title Text</h1>")

        info = html_helper.extract_interruption_info(html_str)
        
        assert "Title Text" == info["title"]

    def test_missing_title(self):
        html_str = self.int_html.format(title_element="")

        info = html_helper.extract_interruption_info(html_str)
        
        assert "" == info["title"]

    def test_html_structure(self):
        html_str = self.int_html.format(title_element="<h1>Title Text</h1>")

        info = html_helper.extract_interruption_info(html_str)

        html_tree = html.fromstring(info["content"])
        assert "html" == html_tree.tag
        assert "body" == html_tree[0].tag
        assert "main" == html_tree[0][0].tag

    def test_img_removed(self):
        html_str = self.int_html.format(title_element="<h1>Title Text</h1>")

        xpathq = "//p/img"

        #make sure its there in the first place
        assert 1 == len(html.fromstring(html_str).xpath(xpathq))

        info = html_helper.extract_interruption_info(html_str)
        
        assert 0 == len(html.fromstring(info["content"]).xpath(xpathq))


