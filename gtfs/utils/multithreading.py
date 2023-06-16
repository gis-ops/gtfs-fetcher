import os
import pathlib
import threading

from ..feed_source import FeedSource
from ..utils.constants import LOG


def multi_fetch(sources: list, output_dir_path: pathlib.Path, concurrency: int) -> None:
    threads: list[threading.Thread] = []

    def thread_worker():
        while True:
            try:
                src = sources.pop(0)
            except IndexError:
                break

            LOG.debug(f"Going to start fetch for {src}...")
            try:
                if issubclass(src, FeedSource):
                    inst = src()
                    inst.ddir = output_dir_path
                    inst.status_file = os.path.join(inst.ddir, src.__name__ + ".pkl")
                    inst.fetch()
                else:
                    LOG.warning(f"Skipping class {src.__name__}, which does not subclass FeedSource.")
            except AttributeError:
                LOG.error(f"Skipping feed {src}, which could not be found.")

    for _ in range(concurrency):
        thread = threading.Thread(target=thread_worker)
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
