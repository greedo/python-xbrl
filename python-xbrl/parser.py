
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


