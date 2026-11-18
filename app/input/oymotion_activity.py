"""All 8 raw channels contribute equally; DC offsets never become muscle activity."""
import math
import struct
from collections import deque


class OYMotionActivity:
    CHANNELS = 8
    SAMPLE_RATE = 500
    WINDOW = 50  # 100ms, containing every received sample of every channel.
    HOP = 10     # Publish activity at 50Hz; acquisition remains 500Hz.

    def __init__(self):
        self.frames = deque(maxlen=self.WINDOW)
        self.sample_count = 0
        self.channel_rms = (0.,) * self.CHANNELS
        self.activity = 0.
        self._since_publish = 0

    @staticmethod
    def decode(payload):
        if not payload or len(payload) % 16 or len(payload) > 4096:
            raise ValueError('Expected complete 8-channel 12-bit frames.')
        values = struct.unpack('<' + 'H' * (len(payload)//2), payload)
        if any(v > 4095 for v in values):
            raise ValueError('OYMotion ADC value exceeds 12 bits.')
        return [values[i:i+8] for i in range(0, len(values), 8)]

    def feed(self, payload):
        output = []
        for frame in self.decode(payload):
            self.frames.append(frame)
            self.sample_count += 1
            self._since_publish += 1
            if len(self.frames) < self.WINDOW or self._since_publish < self.HOP:
                continue
            self._since_publish = 0
            variances = []
            for channel in range(self.CHANNELS):
                values = [row[channel] for row in self.frames]
                mean = math.fsum(values)/len(values)
                variances.append(math.fsum((value-mean)**2 for value in values)/len(values))
            self.channel_rms = tuple(math.sqrt(v) for v in variances)
            self.activity = math.sqrt(math.fsum(variances)/self.CHANNELS)
            output.append(self.activity)
        return output
