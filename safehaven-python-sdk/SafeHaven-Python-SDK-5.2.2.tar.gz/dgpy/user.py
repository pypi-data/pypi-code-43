class User(object):
    """
    User represents a single CMS user.
    @username:   login name
    @lock_count: how many failed login attempts (causes user lock-out)
    @role:       currently 'ADMIN' is the only accepted role
    @level:      currently 'CLUSTER' is the only accepted level
    @resources:  also set to 'CLUSTER', otherwise has no meaning
    """
    _LOCK_COUNT = 3 # Maximum failed attempts; same as UI: USER_LOCK_COUNT

    def __init__(self, username, lock_count, role, level="CLUSTER", resources="CLUSTER"):
        self.username   = username
        self.lock_count = int(lock_count)
        self.role       = role
        self.level      = level
        self.resources  = resources

    def is_locked(self):
        """Returns True if the user is currently locked, using same rule as the GUI"""
        return self.lock_count >= User._LOCK_COUNT

    def __repr__(self):
        return "User(%s, %s: %s)" % (self.username, self.role,
                                     "locked" if self.is_locked() else "ok")
