# 🔊 AUDIO STEGANOGRAPHY TOOL 🔐  
A futuristic web tool to hide and extract secret messages in WAV audio files using **LSB (Least Significant Bit) encoding**

## Features

- 🎙️ Upload and preview `.wav` audio files
- ✏️ Hide any secret text message inside audio
- 🕵️ Extract hidden messages from stego audio
- 💾 Download the steganographically modified audio
- 🧠 Built using Python + Streamlit with **zero setup for users**

---

## How It Works

This tool uses a basic form of **audio steganography**:  
> It modifies audio samples' **Least Significant Bit (LSB)** to embed binary data from the secret message.  
> These slight changes are **imperceptible to the human ear**, but can be decoded to retrieve the message.

---

## 📦 Installation (For Developers)

1. Clone the repo
```bash
git clone https://github.com/ArshSharan/Audio-Steganography-Tool.git
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app
```bash
python -m streamlit run streamlit_app.py
```

---

## Limitations

- [ ] Only supports uncompressed .wav audio files
- [ ] Message length must be short enough to fit in audio sample space
- [ ] No support for other formats like MP3/OGG (yet)

## 🧑‍💻 Author
Developed with ❤️ by Arsh Sharan
