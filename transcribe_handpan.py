#!/usr/bin/env python3
"""
Lotus Handpan — Acoustic Note Extractor & Score Generator
Analyzes handpan audio/video programmatically via librosa and outputs
synchronized time-stamped note scores for live play-along.
"""

import sys, os, json, subprocess
import numpy as np
import scipy.io.wavfile as wavfile
import librosa

def format_time(sec):
    sec = max(0, int(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def extract_audio(video_id_or_url, start_sec=0, duration=90):
    """Downloads a targeted audio window via yt-dlp and converts to mono 22050Hz WAV."""
    if video_id_or_url.startswith("http"):
        url = video_id_or_url
        vid = video_id_or_url.split("v=")[-1].split("&")[0].split("/")[-1]
    else:
        vid = video_id_or_url
        url = f"https://www.youtube.com/watch?v={vid}"

    out_dir = "/data/data/com.termux/files/home/handpan/scores/audio"
    os.makedirs(out_dir, exist_ok=True)

    start_sec = max(0, int(start_sec))
    duration = max(30, int(duration))
    end_sec = start_sec + duration

    wav_filename = f"{vid}_{start_sec}_{duration}.wav" if start_sec > 0 else f"{vid}.wav"
    wav_path = os.path.join(out_dir, wav_filename)

    if os.path.exists(wav_path):
        return vid, wav_path

    raw_path = os.path.join(out_dir, f"raw_{vid}_{start_sec}_{duration}.wav")
    sec_str = f"*{format_time(start_sec)}-{format_time(end_sec)}"
    print(f"[*] Downloading audio slice for {vid} ({sec_str})...")
    cmd = [
        "yt-dlp", "-f", "ba",
        "--download-sections", sec_str,
        "-x", "--audio-format", "wav",
        "-o", raw_path,
        url
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Convert to standard 22050Hz mono
    subprocess.run(["ffmpeg", "-y", "-i", raw_path, "-ac", "1", "-ar", "22050", wav_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if os.path.exists(raw_path):
        try: os.remove(raw_path)
        except Exception: pass

    return vid, wav_path

def transcribe_audio(wav_path, min_clarity=0.45):
    """Detects strike onsets and extracts fundamental pitch frequencies via fast wav loading."""
    print(f"[*] Loading {wav_path} via fast wavfile...")
    sr, data = wavfile.read(wav_path)
    if data.dtype == np.int16:
        y = (data / 32768.0).astype(np.float32)
    elif data.dtype == np.int32:
        y = (data / 2147483648.0).astype(np.float32)
    else:
        y = data.astype(np.float32)

    if len(y.shape) > 1:
        y = np.mean(y, axis=1)

    dur = len(y) / sr
    print(f"[*] Loaded {dur:.1f}s of audio in ms. Detecting transients...")

    # Onset detection optimized for percussive handpan strikes
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
    onsets = librosa.onset.onset_detect(y=y, sr=sr, onset_envelope=onset_env,
                                           backtrack=True, units="time")

    print(f"[*] Found {len(onsets)} potential onsets. Extracting fundamental frequencies...")

    notes = []
    # Handpan note range: C3 (~130Hz) to C6 (~1050Hz)
    fmin = librosa.note_to_hz("C3")
    fmax = librosa.note_to_hz("C6")

    detected_midis = {}

    for t in onsets:
        start_samp = int(t * sr)
        window_samp = int(0.14 * sr) # 140ms analysis window
        seg = y[start_samp:start_samp + window_samp]
        if len(seg) < 512:
            continue

        # Extract pitch using probabilistic YIN
        f0, voiced_flag, voiced_probs = librosa.pyin(seg, fmin=fmin, fmax=fmax, sr=sr)
        valid = f0[voiced_flag & (voiced_probs > min_clarity)]
        if len(valid):
            med_f0 = float(np.median(valid))
            midi = int(round(librosa.hz_to_midi(med_f0)))
            note_name = librosa.midi_to_note(midi)

            # Avoid duplicate onsets within 90ms of same note
            if notes and abs(notes[-1]["t"] - t) < 0.09 and notes[-1]["midi"] == midi:
                continue

            notes.append({
                "t": round(float(t), 3),
                "midi": midi,
                "note": note_name,
                "f0": round(med_f0, 1),
                "dur": 0.4
            })
            detected_midis[midi] = detected_midis.get(midi, 0) + 1

    # Filter out spurious one-off ghost notes if we have plenty of notes
    if len(notes) > 20:
        common_midis = sorted([m for m, count in detected_midis.items() if count >= 2])
        if len(common_midis) >= 7:
            notes = [n for n in notes if n["midi"] in common_midis]
            layout = common_midis
        else:
            layout = sorted(list(detected_midis.keys()))
    else:
        layout = sorted(list(detected_midis.keys()))

    print(f"[+] Transcribed {len(notes)} notes across {len(layout)} unique handpan pads: {layout}")
    return notes, layout

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe_handpan.py <video_id_or_url> [title] [artist]")
        sys.exit(1)

    target = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "Transcribed Performance"
    artist = sys.argv[3] if len(sys.argv) > 3 else "Handpan Artist"

    vid, wav_path = extract_audio(target)
    notes, layout = transcribe_audio(wav_path)

    score_data = {
        "videoId": vid,
        "title": title,
        "artist": artist,
        "layout": layout,
        "notes": notes,
        "totalNotes": len(notes),
        "generatedAt": int(os.path.getmtime(wav_path))
    }

    scores_dir = "/data/data/com.termux/files/home/handpan/scores"
    os.makedirs(scores_dir, exist_ok=True)
    out_json = os.path.join(scores_dir, f"{vid}.json")
    with open(out_json, "w") as f:
        json.dump(score_data, f, indent=2)

    print(f"[SUCCESS] Saved synchronized score to {out_json}")

if __name__ == "__main__":
    main()
