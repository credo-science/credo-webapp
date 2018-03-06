class InputHeader:
    def __init__(self, application=None, frame_type=None, protocol=None, time_stamp=None):
        self.application = application
        self.frame_type = frame_type
        self.protocol = protocol
        self.time_stamp = time_stamp


class Body:
    def __init__(self, detection, device_info, user_info):
        self.detection = detection
        self.device_info = device_info
        self.user_info = user_info


class DetectionRequest:
    def __init__(self, header, body):
        self.header = header
        self.body = body
