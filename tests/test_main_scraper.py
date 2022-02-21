from shared_code import html_helper
from lxml import etree, html

class TestMainScraper:

    main_html = \
    '''
    <html lang="en-US">
        <head></head>
        <body>
            <main role="main">
            <div><div><div class="bunch-o-divs">
                <a href="https://shouldnot.be/included">Read Move</a>
                <div>
                    <div data-widget_type="heading.default">
                        <div>
                            <h4>Maintenance</h4>
                        </div>
                    </div>
                    <div>
                        <article>
                            <div class="more than 1 div here">
                                <div>
                                    <h3><a href="https://foo.com/bar">Card Title</a>
                                    <a href="https://foo.com/bar">Read Move</a>
                                </div>
                            </div>
                        </article>
                        <article>
                            <div class="more than 1 div here">
                                <div>
                                    <h3><a href="https://foo.com/another">Card Title</a>
                                    <a href="https://foo.com/another">Read Move</a>
                                </div>
                            </div>
                        </article>
                    </div>
                </div>
            </div></div></div>
            </main>
        </body>
    </html>'''


    def test_extract_maintenance_links(self):
        html_str = self.main_html

        maint_urls = html_helper.extract_maintenance_links(html_str)
        
        assert len(maint_urls) == 2
        assert "https://foo.com/bar" in maint_urls
        assert "https://foo.com/another" in maint_urls


