import queue
import sys
import threading


class MessageQueueProcessor:

    def __init__(self, num_workers=4):
        self.q = queue.Queue()
        self.workers = []
        self.coordinator = None
        self.create_workers(num_workers)
        self.create_coordinator()

    def create_workers(self, num_workers):
        for _ in range(num_workers):
            worker = threading.Thread(target=self.worker_thread)
            worker.daemon = True
            self.workers.append(worker)
            worker.start()

    def worker_thread(self):
        while True:
            message = self.q.get()
            message = self.action1(message)
            message = self.action2(message)
            message = self.action3(message)
            print(f"Processed message: {message}")
            self.q.task_done()

    def action1(self, message):
        # Perform the first action on the message
        return f'{message} + "_action1"'

    def action2(self, message):
        return f'{message} + "_action2"'

    def action3(self, message):
        # Perform the third action on the message
        return f'{message} + "_action3"'

    def create_coordinator(self):
        self.coordinator = threading.Thread(target=self.coordinator_thread)
        self.coordinator.daemon = True
        self.coordinator.start()

    def coordinator_thread(self):
        while True:
            self.q.join()

    def add_message(self, message):
        self.q.put(message)


def main():
    processor = MessageQueueProcessor(num_workers=4)

    # Add new messages to the queue
    processor.add_message("Message 1")
    processor.add_message("Message 2")
    processor.add_message("Message 3")

    print("Press Enter to close the program...")
    input()
    processor.coordinator.join()
    print("Program closed.")
    sys.exit(0)


if __name__ == '__main__':
    main()
