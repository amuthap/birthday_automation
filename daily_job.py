import subprocess, os
PY = r"C:\Python313\python.exe"
BASE = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print("-> " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=BASE)
    if r.returncode != 0:
        raise SystemExit(r.returncode)

if __name__ == "__main__":
    run([PY, "scrape_names.py"])      # 1) scrape -> writes CSV
    run([PY, "birthday_script.py"])   # 2) generate image + send WhatsApp
