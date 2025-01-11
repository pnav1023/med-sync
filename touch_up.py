import re
from html.parser import HTMLParser

# Create a class to strip HTML tags
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = []

    def handle_data(self, data):
        self.data.append(data)

    def get_data(self):
        return ''.join(self.data)

def strip_html(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()



##other class
def case_insensitive_match(term, text):
    """Check if a term matches a text, case-insensitively."""
    if not term:
        return False  # Avoid matching empty inputs
    return bool(re.search(re.escape(term), text, flags=re.IGNORECASE))