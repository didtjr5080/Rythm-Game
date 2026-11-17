"""Bounded application jobs; Qt consumers poll futures without cross-thread widgets."""
from concurrent.futures import ThreadPoolExecutor

jobs = ThreadPoolExecutor(max_workers=2, thread_name_prefix='exhibition-job')
