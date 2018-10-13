class DaemonException(Exception):
    """Exception that deamons are raising"""

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val):
        self._parent = val

    def __init__(self, msg=None, parent=None):
        """Creates a new DaemonException.
        :param msg: Exception message
        :param parent: Optionals: parent={parent exception}
        """
        if parent:
            if not msg:
                msg = ""
            else:
                msg = msg + ":"
            msg = "{} {}".format(msg, parent)
        super(DaemonException, self).__init__(msg)
        self.parent = parent

    def has_parent(self):
        return self.parent is not None


class DaemonTimeoutException(DaemonException):
    """Special :class:`DaemonException` that is raised when a timeout was detected."""
    pass
