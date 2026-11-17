"""Bounded, thread-safe timings; flush off the GUI thread at segment completion."""
import json
import threading
import time
from collections import defaultdict, deque
from pathlib import Path
from uuid import uuid4

class Timings:
    def __init__(self):
        self.values=defaultdict(lambda: deque(maxlen=20000))
        self.lock=threading.Lock()

    def add(self,name,milliseconds):
        with self.lock: self.values[name].append(float(milliseconds))

    def summary(self):
        with self.lock: snapshot={k:sorted(v) for k,v in self.values.items()}
        return {k:dict(n=len(v),p50=v[int((len(v)-1)*.5)],p95=v[int((len(v)-1)*.95)],
                       p99=v[int((len(v)-1)*.99)],max=v[-1]) for k,v in snapshot.items() if v}

    def flush(self):
        from app.background import jobs
        payload=self.summary()
        def write():
            folder=Path(__file__).resolve().parent/'data'/'logs'
            folder.mkdir(parents=True,exist_ok=True)
            path=folder/f'performance-{time.strftime("%Y%m%d-%H%M%S")}-{uuid4().hex[:8]}.json'
            path.write_text(json.dumps(payload,indent=2),encoding='utf-8')
        return jobs.submit(write)

timings=Timings()
