
class NoTextBox(Exception):
    """Raised when attempt to push txt to a textentry box that 
    hasn't been registered."""

class TextGrab(object):
    """Global object to handle grabbing of text and passing to
    a function that accepts text."""
    _shared_state = {}
    _textobject = None
    def __init__(self):
        self.__dict__ = self._shared_state

    def register(self, text_accept):
        self._textobject = text_accept

    def deregister(self):
        self._textobject = None

    def push(self, txt):
        if self._textobject:
            self._textobject(txt)
        else:
            raise NoTextBox("No text box set!")

