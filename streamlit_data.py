import streamlit as st
import json
import os
import tempfile
import webbrowser
from psd_tools import PSDImage
from groq import Groq

st.set_page_config(page_title="PSD to HTML Generator", layout="wide")
st.title("📄 PSD to HTML Generator")

# -------------------------------
# 1️⃣ Upload PSD File
# -------------------------------
uploaded_file = st.file_uploader("Upload PSD file", type=["psd"], accept_multiple_files=False)

if uploaded_file is not None:
    # Save uploaded PSD to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".psd") as tmp:
        tmp.write(uploaded_file.read())
        PSD_FILE = tmp.name
    
    st.success(f"✅ PSD file uploaded: {uploaded_file.name}")

    # -------------------------------
    # 2️⃣ Convert PSD to JSON
    # -------------------------------
    def psd_to_dict(layer):
        layer_dict = {
            "name": layer.name,
            "visible": layer.visible,
            "bbox": layer.bbox,
            "type": "FRAME" if layer.is_group() else "LAYER",
            "children": [psd_to_dict(l) for l in layer] if layer.is_group() else []
        }
        return layer_dict

    try:
        psd = PSDImage.open(PSD_FILE)
        psd_json = {"document": {"children": [psd_to_dict(layer) for layer in psd]}}
        st.success("✅ PSD converted to JSON")
    except Exception as e:
        st.error(f"❌ Failed to convert PSD to JSON: {e}")
        st.stop()

    # -------------------------------
    # 3️⃣ Generate HTML via Groq API
    # -------------------------------
    # API_KEY = st.secrets.get("GROQ_API_KEY", "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")
    API_KEY = "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"


    if st.button("Generate HTML"):
        with st.spinner("Generating HTML..."):
            prompt = f"""
            You are an expert web developer. 
            I am giving you a JSON representing my page layout from a PSD file. 
            Generate a complete, clean, semantic HTML page from it using proper tags like <header>, <nav>, <section>, <footer>, <main>, <article>. 
            - Use CSS Flexbox or Grid for layout instead of absolute positioning where possible.
            - Add placeholders for missing images (e.g., src='placeholder.png').
            - Include text from JSON where possible.
            - Use inline CSS sparingly only for essential styling.
            - Make the page responsive.
            - Do NOT include any explanations, comments, or markdown in the output.
            - Only return the HTML content.
            Here is the JSON:
            {json.dumps(psd_json)}
            """
            try:
                client = Groq(api_key=API_KEY)
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": prompt}],
                )
                html_result = response.choices[0].message.content

                if not html_result.strip():
                    st.error("❌ Groq API returned empty HTML")
                    st.stop()

            except Exception as e:
                st.error(f"❌ Groq API request failed: {e}")
                st.stop()

        # -------------------------------
        # 4️⃣ Save HTML to temp file
        # -------------------------------
        html_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        html_file.write(html_result.encode("utf-8"))
        html_file.close()

        st.success("✅ HTML generated successfully!")

        # -------------------------------
        # 5️⃣ Show options: Open in browser or download
        # -------------------------------
        if st.button("Open HTML in Browser"):
            webbrowser.open(f"file://{html_file.name}")

        st.download_button(
            label="Download HTML File",
            data=html_result,
            file_name="psd_to_html.html",
            mime="text/html"
        )
