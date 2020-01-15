"""
Module for handling HTTP requests.
This wraps whatever library we decide to use, so if we change library we can just change it here.
"""
import requests
import os


class VerdictServerConnection(object):
    """Class to wrap HTTP requests to the verdict server."""

    def __init__(self, verdict_server):
        self._verdict_server = verdict_server

    def request(self, end_point):
        """Given an end-point on the verdict server, get the response."""
        try:
            response = requests.get(os.path.join(self._verdict_server, end_point))
            return response.text
        except:
            raise Exception("Failed to connect to the verdict server at '%s'." % self._verdict_server)

    def handshake(self):
        """Try to connect to the verdict server.  We might include more information in the response at some point."""
        # request the index page
        self.request(end_point="")
