#!/usr/bin/env python3
import os
import shutil
import urllib.request
import concurrent.futures

BASE_URL = "https://www.yishama.com/virtual-pantam/assets/notes/"
TARGET_DIR = "/data/data/com.termux/files/home/handpan/samples"

NOTES = [
    'Db2', 'D2', 'Eb2', 'E2', 'F2', 'Gb2', 'G2', 'Ab2', 'A2', 'Bb2', 'B2',
    'C3', 'Db3', 'D3', 'Eb3', 'E3', 'F3', 'Gb3', 'G3', 'Ab3', 'A3', 'Bb3', 'B3',
    'C4', 'Db4', 'D4', 'Eb4', 'E4', 'F4', 'Gb4', 'G4', 'Ab4', 'A4', 'Bb4', 'B4',
    'C5', 'Db5', 'D5', 'Eb5', 'E5', 'F5', 'Gb5', 'G5', 'Ab5', 'A5', 'Bb5', 'B5',
    'C6', 'Db6', 'D6', 'Eb6', 'E6', 'SLAP'
]

os.makedirs(TARGET_DIR, exist_ok=True)

def download_sample(name):
    filename = f"{name}.mp3"
    dest_path = os.path.join(TARGET_DIR, filename)
    url = f"{BASE_URL}{filename}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) ChloeOS/Revo-Door"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
            return name, len(data), None
    except Exception as e:
        return name, 0, str(e)

def main():
    print(f"[*] Downloading {len(NOTES)} sound samples from Yishama to {TARGET_DIR}...")
    success = 0
    total_bytes = 0
    failed = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(download_sample, n): n for n in NOTES}
        for future in concurrent.futures.as_completed(futures):
            name, size, err = future.result()
            if err:
                print(f"[!] FAILED {name}: {err}")
                failed.append(name)
            else:
                success += 1
                total_bytes += size
                print(f"[+] Downloaded {name}.mp3 ({size:,} bytes)")

    # Also link D3.mp3 to ding.mp3 for classic handpan ding pad integration
    d3_path = os.path.join(TARGET_DIR, "D3.mp3")
    ding_path = os.path.join(TARGET_DIR, "ding.mp3")
    if os.path.exists(d3_path):
        shutil.copyfile(d3_path, ding_path)
        print(f"[+] Created ding.mp3 from D3.mp3 ({os.path.getsize(ding_path):,} bytes)")

    print(f"\n[*] Finished: {success}/{len(NOTES)} samples downloaded.")
    print(f"[*] Total downloaded size: {total_bytes / (1024*1024):.2f} MB")
    if failed:
        print(f"[!] Failed samples: {failed}")
    return len(failed)

if __name__ == "__main__":
    exit(main())
