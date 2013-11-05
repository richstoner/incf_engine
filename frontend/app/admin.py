__author__ = 'stonerri'


# from stackexchange: http://stackoverflow.com/questions/16448913/tornado-and-wtforms
class TornadoFormMultiDict(object):
    """Wrapper class to provide form values to wtforms.Form

    This class is tightly coupled to a request handler, and more importantly one of our BaseHandlers
    which has a 'context'. At least if you want to use the save/load functionality.

    Some of this more difficult that it otherwise seems like it should be because of nature
    of how tornado handles it's form input.
    """
    def __init__(self, handler):
        # We keep a weakref to prevent circular references
        # This object is tightly coupled to the handler... which certainly isn't nice, but it's the
        # way it's gonna have to be for now.
        self.handler = weakref.ref(handler)

    @property
    def _arguments(self):
        return self.handler().request.arguments

    def __iter__(self):
        return iter(self._arguments)

    def __len__(self):
        return len(self._arguments)

    def __contains__(self, name):
        # We use request.arguments because get_arguments always returns a
        # value regardless of the existence of the key.
        return (name in self._arguments)

    def getlist(self, name):
        # get_arguments by default strips whitespace from the input data,
        # so we pass strip=False to stop that in case we need to validate
        # on whitespace.
        return self.handler().get_arguments(name, strip=False)

    def __getitem__(self, name):
        return self.handler().get_argument(name)

