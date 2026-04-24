import logging, contextlib, time

@contextlib.contextmanager
def section(title: str):
    logging.info("=== %s ===", title)
    t0 = time.time()
    try:
        yield
    finally:
        dt = (time.time()-t0)*1000.0
        logging.info("--- %s done in %.2f ms", title, dt)
