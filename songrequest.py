class SongRequest:
    """A wrapper for information about the songs requested by users."""

    def __init__(self, url, title, requester = None, uploader = None, creator = None, duration = None, like_count = None, dislike_count = None, thumbnail = None):
        self.uploader = uploader
        self.requester = requester
        self.title = title
        self.duration = duration
        self.like_count = like_count
        self.dislike_count = dislike_count
        self.url = url
        self.thumbnail = thumbnail

#        self._output = ""
#        self.format_output()

    @property
    def output(self):
        return self._output
