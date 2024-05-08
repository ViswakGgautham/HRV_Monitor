class Piotimer:
    def __init__(self, period=None, freq=None, mode=Piotimer.ONE_SHOT, callback=None):
        if period is None and freq is None:
            raise ValueError("Must specify 'freq' or 'period'")
        self.period = period
        self.freq = freq
        self.mode = mode
        self.callback = callback