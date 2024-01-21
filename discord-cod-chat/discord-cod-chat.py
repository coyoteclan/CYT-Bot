import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

def process_message(message):
    # Replace this with your custom function to process the message
    print("Processing message:", message)

class LogFileHandler(PatternMatchingEventHandler):
    def on_modified(self, event):
        with open(event.src_path, "r") as log_file:
            for line in log_file.readlines():
                if line.startswith("say: ") or line.startswith("something: "):
                    message = line.split(":", 1)[1].strip()
                    process_message(message)

if __name__ == "__main__":
    log_file_path = "path/to/your/game.log"
    patterns = ["*.log"]
    
    event_handler = LogFileHandler(patterns=patterns)
    observer = Observer()
    observer.schedule(event_handler, path=log_file_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
