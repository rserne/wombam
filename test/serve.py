# Start een webserver voor de map van de app, draai een testscript en stop de server weer.
import subprocess, sys, time, os
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
srv=subprocess.Popen([sys.executable,'-m','http.server','8765'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
try: sys.exit(subprocess.call([sys.executable]+sys.argv[1:],cwd=root))
finally: srv.terminate()
