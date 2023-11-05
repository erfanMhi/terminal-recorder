import platform

def _get_active_app_name():
    """Get the name of the current active application."""
    print('system name: ', platform.system())
    if platform.system() == 'Darwin':
        # macOS
        import Quartz
        app = Quartz.NSWorkspace.sharedWorkspace().activeApplication()
        return app['NSApplicationName']
    elif platform.system() == 'Windows':
        # Windows
        import win32gui
        import win32process
        import psutil
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid[-1])
        process_name = process.name()
        return process_name
    elif platform.system() == 'Linux':
        # Linux
        import subprocess
        try:
            output = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowname'])
            return output.decode('utf-8').strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ''
    else:
        # Unsupported platform
        return ''