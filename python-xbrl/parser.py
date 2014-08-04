
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def soup_maker(fh):
    skip_headers(fh)
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(fh, "xml")
        for tag in soup.findAll():
            tag.name = tag.name.lower()
    except ImportError:
        from BeautifulSoup import BeautifulStoneSoup
        soup = BeautifulStoneSoup(fh)
    return soup


class XBRLParserException(Exception):
    pass

class XBRLParser(object):
    @classmethod
    def parse(file_handle):
        '''
        parse is the main entry point for an XBRLParser. It takes a file
        handle.

        '''

        xbrl_obj = XBRL()

        # Store the headers
        xbrl_file = OfxPreprocessedFile(file_handle)
        xbrl_obj.headers = ofx_file.headers
        xbrl_obj.accounts = []
        xbrl_obj.signon = None

        skip_headers(ofx_file.fh)
        ofx = soup_maker(ofx_file.fh)
        if ofx.find('ofx') is None:
            raise OfxParserException('The ofx file is empty!')


