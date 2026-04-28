#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from app.window import ModernSalahApp

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Salah Times")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Islamic Apps")
    app.setQuitOnLastWindowClosed(False)

    lock_file = os.path.join(os.path.expanduser('~'), '.salah_times', 'app.lock')
    try:
        os.makedirs(os.path.dirname(lock_file), exist_ok=True)
        if os.path.exists(lock_file):
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                print("Another instance is already running")
                sys.exit(0)
            except OSError:
                os.remove(lock_file)
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
    except Exception as e:
        print(f"Could not create lock file: {e}")

    window = ModernSalahApp()
    window.show()

    def cleanup():
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except:
            pass

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
