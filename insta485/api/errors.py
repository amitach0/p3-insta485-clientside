"""Error response code handling."""
import flask
import insta485


class InvalidUsage(Exception):
    """Class for error handling."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Initialize invalid usage."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert to dict."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle invalid usage."""
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
