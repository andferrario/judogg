class LoadError(Exception):
    pass


class CallFailed(Exception):
    """An IJF call that still fails after its retries: it is reported and the download goes on."""


class FetchError(Exception):
    pass
