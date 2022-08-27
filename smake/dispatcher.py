import subprocess, os, time

class Dispatcher:
    PROCESSES = []
    LIMIT = os.cpu_count() if os.cpu_count() is not None else 4

    @staticmethod
    def run(command: list):
        if len(Dispatcher.PROCESSES) >= Dispatcher.LIMIT:
            Dispatcher._wait_one()
        
        print(" ".join(command))
        Dispatcher.PROCESSES.append(subprocess.Popen(command))
    
    @staticmethod
    def _wait_one():
        while True:
            for i, proc in enumerate(Dispatcher.PROCESSES):
                result = proc.poll()
                if result is not None:
                    Dispatcher.PROCESSES.pop(i)
                    return
                elif result != 0:
                    exit(1)
            
            time.sleep(0.001)
    
    @staticmethod
    def wait():
        for proc in Dispatcher.PROCESSES:
            if proc.wait() != 0:
                exit(1)
