import streamlit as st
import numpy as np
import wave
import io
from streamlit_extras.stylable_container import stylable_container
import time

# ---- UTILITY FUNCTIONS ---- #

def message_to_bits(message):
    return ''.join(f'{ord(c):08b}' for c in message)

def bits_to_message(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message = ''.join(chr(int(c, 2)) for c in chars)
    return message

def embed_message(audio_data, message, sample_width):
    bits = message_to_bits(message) + '1111111111111110'  # EOF marker
    audio_flat = np.copy(audio_data).flatten()

    if len(bits) > len(audio_flat):
        raise ValueError("Message too long to encode in audio")

    for i, bit in enumerate(bits):
        audio_flat[i] = (audio_flat[i] & ~1) | int(bit)  # LSB replace

    return audio_flat.reshape(audio_data.shape)

def extract_message(audio_data):
    audio_flat = audio_data.flatten()
    bits = [str(audio_flat[i] & 1) for i in range(len(audio_flat))]
    bitstring = ''.join(bits)

    # Look for EOF marker
    end_marker = '1111111111111110'
    end_index = bitstring.find(end_marker)
    if end_index == -1:
        return "No hidden message found."

    message_bits = bitstring[:end_index]
    return bits_to_message(message_bits)

# ---- FUTURISTIC CSS (Copied from DTMF Decoder) ---- #
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    :root {
        --primary: #00f0ff;
        --secondary: #ff00ff;
        --dark: #0a0a12;
        --light: #f0f0ff;
        --accent: #7b2dff;
    }

    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
        background-color: var(--dark);
        color: var(--light);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        color: var(--primary) !important;
        text-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
        letter-spacing: 2px;
    }

    .stApp {
        background-color: var(--dark);
        background-image: radial-gradient(circle at 20% 30%, rgba(123, 45, 255, 0.08) 0%, transparent 30%),
                          radial-gradient(circle at 80% 70%, rgba(0, 240, 255, 0.08) 0%, transparent 30%);
        overflow: hidden;
    }

    /* 🔥 REMOVE all glow effects on hover */
    button, .stButton>button, .stFileUploader>div>div, .stCheckbox>div>div, input, textarea, select {
        outline: none !important;
        box-shadow: none !important;
        transition: none !important;
    }

    /* Button styling */
    .stButton>button {
        border: 2px solid var(--primary) !important;
        background: rgba(10, 10, 20, 0.5) !important;
        color: var(--primary) !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }

    /* File uploader */
    .stFileUploader>div>div {
        border: 2px dashed var(--primary) !important;
        background: rgba(10, 10, 20, 0.5) !important;
        color: var(--primary) !important;
        border-radius: 8px !important;
    }

    /* Checkbox and others */
    .stCheckbox>div>div {
        border: 2px solid var(--primary) !important;
        background: rgba(10, 10, 20, 0.5) !important;
    }

    /* Error/success blocks */
    .stSuccess {
        background: rgba(0, 240, 255, 0.08) !important;
        border-left: 4px solid var(--primary) !important;
        border-radius: 0 8px 8px 0 !important;
    }

    .stError {
        background: rgba(255, 0, 100, 0.08) !important;
        border-left: 4px solid #ff0064 !important;
        border-radius: 0 8px 8px 0 !important;
    }

    /* Cyber-terminal block */
    .cyber-terminal {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid var(--primary);
        border-radius: 8px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        color: var(--primary);
    }

    .ascii-art {
        font-family: 'Courier New', monospace;
        color: var(--primary);
        white-space: pre;
        line-height: 1.2;
    }
    
    *:focus, *:active {
        outline: none !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ---- ASCII ART HEADER ---- #
ascii_art = r"""
   ________  ______  __________ _    ____________  _____ ______
  / ____/\ \/ / __ )/ ____/ __ \ |  / / ____/ __ \/ ___// ____/
 / /      \  / __  / __/ / /_/ / | / / __/ / /_/ /\__ \/ __/   
/ /___    / / /_/ / /___/ _, _/| |/ / /___/ _, _/___/ / /___   
\____/   /_/_____/_____/_/ |_| |___/_____/_/ |_|/____/_____/   

"""

# ---- MAIN UI ---- #
st.markdown(f"""
<div style="text-align: center; margin-bottom: 30px;">
    <div class="ascii-art" style="color: var(--primary); font-size: 10px; opacity: 0.8;">{ascii_art}</div>
    <h1 class="glow" style="margin-top: -10px; font-size: 3em;">AUDIO STEGANOGRAPHY TOOL</h1>
    <p style="color: var(--light); letter-spacing: 2px;">LSB ENCODING/DECODING SYSTEM</p>
    <div style="height: 2px; background: linear-gradient(90deg, transparent, var(--primary), transparent); margin: 10px auto; width: 50%;"></div>
</div>
""", unsafe_allow_html=True)

# ---- MODE SELECTION ---- #
with stylable_container(
    key="mode_selector",
    css_styles="""
        {
            border: 2px solid var(--primary);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            background: rgba(10, 10, 20, 0.5);
            margin-bottom: 30px;
        }
    """,
):
    mode = st.radio(
        "OPERATION MODE",
        ["Hide Message", "Extract Message"],
        horizontal=True,
        label_visibility="collapsed"
    )

# ---- MAIN FUNCTIONALITY ---- #
if mode == "Hide Message":
    with stylable_container(
        key="uploader",
        css_styles="""
            {
                border: 2px dashed var(--primary);
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                background: rgba(10, 10, 20, 0.5);
                margin-bottom: 30px;
            }
        """,
    ):
        uploaded_audio = st.file_uploader("UPLOAD CARRIER WAV FILE", type=["wav"], label_visibility="collapsed")
        # Add this line after uploading audio in both modes
        st.audio(uploaded_audio, format='audio/wav')

    with stylable_container(
        key="message_input",
        css_styles="""
            {
                border: 2px solid var(--primary);
                border-radius: 8px;
                padding: 20px;
                background: rgba(10, 10, 20, 0.5);
                margin-bottom: 30px;
            }
        """,
    ):
        # ---- Inside "Hide Message" mode ----

    # Your existing text area
        secret_msg = st.text_area("ENTER SECRET MESSAGE", height=150, label_visibility="collapsed")

    # Add the styled encode button
    with stylable_container(
        key="encode_button",
        css_styles="""
            button {
                border: 1px solid var(--primary) !important;
                background: rgba(10, 10, 30, 0.7) !important;
                color: var(--primary) !important;
                font-family: 'Orbitron' !important;
                font-size: 1.1em !important;
                padding: 12px 28px !important;
                margin: 20px 0 !important;
                border-radius: 4px !important;
                letter-spacing: 1px;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            button:hover {
                background: rgba(20, 20, 40, 0.9) !important;
                border-color: var(--secondary) !important;
                color: var(--secondary) !important;
                box-shadow: 0 2px 8px rgba(0, 240, 255, 0.15) !important;
                transform: none !important;
            }
            button:active {
                transform: scale(0.98) !important;
            }
        """
    ):
        encode_button = st.button(
            "⚡ ENCODE MESSAGE",
            key="encode_button",
            help="Securely hide your message in the audio file"
        )

    # Modified processing block (now requires button click)
    if uploaded_audio and secret_msg and encode_button:
        with st.spinner('ENCODING MESSAGE...'):
            time.sleep(1)  # For dramatic effect
            
            with wave.open(uploaded_audio, 'rb') as wav_file:
                params = wav_file.getparams()
                n_channels, sampwidth, framerate, n_frames = params[:4]
                audio_bytes = wav_file.readframes(n_frames)

            audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_np = audio_np.reshape(-1, n_channels)

            try:
                stego_np = embed_message(audio_np, secret_msg, sampwidth)
                stego_bytes = stego_np.astype(np.int16).tobytes()

                # Write to buffer
                buffer = io.BytesIO()
                with wave.open(buffer, 'wb') as out_wav:
                    out_wav.setparams(params)
                    out_wav.writeframes(stego_bytes)
                buffer.seek(0)

                with stylable_container(
                    key="success_box",
                    css_styles="""
                        {
                            border-left: 4px solid var(--primary);
                            padding: 15px 20px;
                            background: rgba(0, 0, 0, 0.5);
                            margin-bottom: 20px;
                            border-radius: 0 8px 8px 0;
                        }
                    """,
                ):
                    st.success("✅ ENCODING SUCCESSFUL")
                
                st.audio(buffer, format='audio/wav')    
                st.download_button(
                    "DOWNLOAD STEGO AUDIO",
                    buffer,
                    file_name="stego_audio.wav",
                    mime="audio/wav"
                )

            except ValueError as e:
                with stylable_container(
                    key="error_box",
                    css_styles="""
                        {
                            border-left: 4px solid #ff0064;
                            padding: 15px 20px;
                            background: rgba(255, 0, 100, 0.08);
                            margin-bottom: 20px;
                            border-radius: 0 8px 8px 0;
                        }
                    """,
                ):
                    st.error(f"❌ {e}")

elif mode == "Extract Message":
    with stylable_container(
        key="uploader",
        css_styles="""
            {
                border: 2px dashed var(--primary);
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                background: rgba(10, 10, 20, 0.5);
                margin-bottom: 30px;
            }
        """,
    ):
        uploaded_audio = st.file_uploader("UPLOAD STEGO WAV FILE", type=["wav"], label_visibility="collapsed")
        # Add this line after uploading audio in both modes
        st.audio(uploaded_audio, format='audio/wav')
    if uploaded_audio:
        with st.spinner('DECODING MESSAGE...'):
            time.sleep(1.5)  # For dramatic effect
            
            with wave.open(uploaded_audio, 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                n_frames = wav_file.getnframes()
                audio_bytes = wav_file.readframes(n_frames)

            audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_np = audio_np.reshape(-1, n_channels)

            secret = extract_message(audio_np)
            
            st.markdown("""
            <div style="margin: 30px 0;">
                <h3 style="color: var(--secondary); text-align: center;">DECODED MESSAGE</h3>
                <div class="cyber-terminal" style="font-size: 18px; padding: 30px; text-align: left;">
                    <span style="color: var(--secondary);">>> </span>
                    <span style="color: var(--primary); font-weight: bold;">{0}</span>
                </div>
            </div>
            """.format(secret), unsafe_allow_html=True)

# ---- FOOTER ---- #
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: var(--light); font-size: 0.8em; opacity: 0.7;">
    <div style="height: 1px; background: linear-gradient(90deg, transparent, var(--primary), transparent); margin: 20px auto; width: 30%;"></div>
    COVERT CHANNEL v1.0 | [SYSTEM: ONLINE] | [CPU: 62%] | [MEM: 45%]
</div>
""", unsafe_allow_html=True)