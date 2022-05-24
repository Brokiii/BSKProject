class Storage:
    password: str
    mode: str
    actual_session_key: str
    other_public_key: str
    buffer_size: int
    filename: str

    def __init__(self, password, mode, buffer_size):
        self.password = password
        self.mode = mode
        self.buffer_size = buffer_size
        self.actual_session_key = ""
        self.other_public_key = ""
        self.filename = "filename"
