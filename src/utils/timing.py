import time
from contextlib import contextmanager

@contextmanager
def timer(name: str = "Operation"):
    start = time.time()
    yield
    end = time.time()
    print(f"{name} took {(end - start)*1000:.2f}ms")
