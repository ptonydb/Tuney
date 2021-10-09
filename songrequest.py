class SongRequest:
    """A wrapper for information about the songs requested by users."""

    def __init__(self, url, title, requester = None, uploader = None, views = None, creator = None, duration = None, like_count = None, dislike_count = None, thumbnail = None):
        
        self.url = url
        self.title = title
        self.duration = duration
        self.views = views
        self.like_count = like_count
        self.dislike_count = dislike_count
        self.creator = creator
        self.thumbnail = thumbnail
        self.requester = requester

#        self._output = ""
#        self.format_output()

    @property
    def output(self):
        return self._output

