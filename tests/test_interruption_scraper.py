from shared_code import html_helper
from lxml import etree, html

class TestInterruptionScraper:

    int_html = \
    '''
    <html lang="en-US">
        <head></head>
        <body>
            <main role="main">
                <header class="page-header">{title_element}</header>
                <div class="page-content">
                    <p>Usually summary with location:</p>
                    <p>
                      <strong><br>Date:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Saturday&nbsp; march 27<sup>th&nbsp;</sup> to Friday April 23<sup>rd</sup>, 2021<br></strong>
                      <strong>Time:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 06:00 - 19:00 o’clock in the evening</strong>
                    </p>
                    <p>Details about interruption</p>
                    <p>More details...</p>
                    <p>Maybe even more...</p>
                    <p><img loading="lazy" class="alignnone size-medium wp-image-11389" src="https://www.weirdwordpressimgtag.com/pic.jpg" alt="" width="207" height="300" sizes="(max-width: 207px) 100vw, 207px"></p>
                    <p>&nbsp;</p>
                </div>
            </main>
        </body>
    </html>'''

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



