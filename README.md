# 🪷 Lotus Handpan & Lotus Jam

> **A real-time, polyphonic virtual handpan & collaborative audio synthesizer for the Web, Android Termux, and PRoot.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Web Audio](https://img.shields.io/badge/audio-WebAudio_API-brightgreen.svg)
![Zero Dependencies](https://img.shields.io/badge/dependencies-none-orange.svg)

---

## ✨ Features

- **🌸 Polyphonic Multi-Touch Engine:** Full two-handed chords, Ding holds, melodic rolls, dynamic pressure sensitivity, and glissando slides with zero touch-event locking (`touch-action: none`).
- **🎵 20 Authentic Classic Songs Library:** Complete sheet-music transcriptions with exact rhythms, genuine musical keys, and natural rests:
  - *Brahms' Lullaby (Wiegenlied)*
  - *Hallelujah (Leonard Cohen)*
  - *Imagine (John Lennon)*
  - *Twinkle, Twinkle, Little Star*
  - *Amazing Grace*
  - *The Sound of Silence (Simon & Garfunkel)*
  - *Scarborough Fair*
  - *Greensleeves (What Child Is This)*
  - *Ode to Joy (Beethoven)*
  - *Canon in D (Pachelbel)*
  - *Morning Has Broken*
  - *Stand by Me (Ben E. King)*
  - *Let It Be (The Beatles)*
  - *Over the Rainbow*
  - *What a Wonderful World (Louis Armstrong)*
  - *House of the Rising Sun (The Animals)*
  - *Silent Night (Franz Gruber)*
  - *Bella Ciao*
  - *Clocks (Coldplay)*
  - *First Light (demo meditation)*
- **🎓 Interactive Teach & Free Play Modes:** Real-time note anticipation rings, hit/miss scoring, streak tracking, and instant seamless transition directly into Free Play when a song finishes.
- **🎹 13 Physical Synthesis Engines:** High-fidelity algorithmic synthesis models for Handpan, Acoustic Grand Piano, Marimba, Kalimba, Vibraphone, Celesta, Rhodes, Tubular Bells, Hang Drum, and more.
- **🎙️ Microtonal Pitch & Resonance Detection:** YIN pitch detection combined with Harmonic Product Spectrum (HPS) and subharmonic validation to sample physical acoustic instruments in real time.
- **✨ Complete Handpan Preset Scales:** Includes classic tunings: D Kurd 9, D Kurd 10, F Pygmy, E Pygmy, D Celtic Minor, B Celtic Minor, D Integral, D Hijaz, D Amara, E Equinox, B Ursa Minor, C Akebono, and D Mystic.

---

## 🚀 Quick Start

Run the zero-dependency Python server:

```bash
# Start server directly
python3 serve.py 8765

# Or use the Lotus daemon controller
./lotus start
./lotus status
```

Open in your browser:
- **Lotus Handpan:** `http://localhost:8765/index.html`
- **Lotus Jam:** `http://localhost:8765/lotusjam.html`

---

## 🛠️ Architecture

- `index.html`: Core single-file Lotus Handpan application with integrated Web Audio synthesis, interactive SVG pad geometry, and pitch tracking.
- `lotusjam.html`: Lotus Jam companion app featuring multi-touch sequencing, recording, and jamming tools.
- `serve.py`: High-performance HTTP server with zero-cache headers optimized for local development and real-time audio sample streaming.
- `lotus`: Daemon manager (`start`, `stop`, `status`, `restart`) designed for Android Termux and PRoot sandboxes.

---

## 📜 License

MIT License. Designed and crafted with digital intelligence for [ChloeOS](https://github.com/acadiemedia).
