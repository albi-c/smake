import subprocess, os, time

class Dispatcher:
    PROCESSES = []

    @staticmethod
    def run(command: list):
        print(" ".join(command))
        Dispatcher.PROCESSES.append(subprocess.Popen(command))
    
    @staticmethod
    def wait():
        for proc in Dispatcher.PROCESSES:
            if proc.wait() != 0:
                exit(1)
