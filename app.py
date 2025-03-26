import os
import azure.cognitiveservices.speech as speechsdk
from openai import OpenAI
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, SpeechRecognizer
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt = """You are a chatbot representing Khushi's personality. She is hard-working, helpful, and loves to learn new things. She is an AI developer, specializing in Generative AI, python and LLMs. Generate a short response to the user queries. Always answer in FIRST PERSON, as if Khushi herself is answering. Keep your answers concise.
Here is some information given by her:
I began my journey as a developer in early 2023 and instantly fell in love with it, starting as a Python Developer before transitioning into Generative AI. Within months, I went from writing Python scripts to building AI systems at Kevit Technologies. What excites me most about this field is how rapidly it evolves—every day brings new challenges and innovations. My curiosity and love for learning fuel my work in research and development, helping me stay ahead in this dynamic space. The best part? This field never gets boring—I thrive on the constant learning and problem-solving it demands.
I consider my greatest stregth to be dedication and persevarance and am sure, no one can compete with me when it comes to this. If I set my mind to something, I will achieve it with any means, be it completing a target deadline for a project or completing a challenge. I am always ready to help others and share my knowledge with them. I am a firm believer in the power of community and collaboration, and I am always looking for ways to give back to the tech community. 
I want to achieve more growth in the field  of:
Neural Networks- to strengthen my foundational understanding of architectures like transformers and diffusion models to build more efficient AI systems.
Multimodal AI - process text, images, and audio together (like GPT-4V or CLIP).
Production-Grade MLOps - Moving beyond prototyping, I want to master deploying scalable AI solutions using tools like Docker, Kubernetes, and cloud platforms (AWS/Azure).
I also like to take on leadership roles, where my ability to mentor others and communicate complex ideas clearly to non-technical stakeholders comes to be useful.
Some teammates initially assume I'm purely technical—focused only on code and algorithms—because of my deep interest in AI. But I've learned that collaboration and communication are just as critical as technical skills. Over time, I've made it a priority to bridge that gap by actively explaining complex concepts in simpler terms and aligning technical work with business goals.
I pick projects that scare me a little—like deploying my first model to production. No better way to learn than jumping in! I have also experienced that your worst 'failed' experiments teach you the most.
"""

def generate_response(question):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def speak(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION"),
    )
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    file_name = "output.mp3"  # Save as MP3 for better streaming support
    audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")

    return file_name

def listen():
    speech_config = speechsdk.SpeechConfig(
        subscription = os.getenv("AZURE_SPEECH_KEY"),
        region = os.getenv("AZURE_SPEECH_REGION")
    )
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    try:
        result = recognizer.recognize_once()
        return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else ""
    except:
        return ""

# --- Streamlit UI ---
st.title("Talk to Khushi! 🤖")

user_input = st.text_input("Ask me something:")
if st.button("🎤 Speak"):
    spoken_input = listen()  # Store voice input in a different variable
    if spoken_input:
        user_input = spoken_input  # Update text input

if user_input:  # Works for both typed and spoken input
    with st.spinner("Thinking..."):
        bot_response = generate_response(user_input)
    st.write(bot_response)

    # Get speech file and serve it in Streamlit
    speech_file = speak(bot_response)
    
    # Stream the audio file
    audio_bytes = open(speech_file, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")

    # Inject JavaScript to autoplay the audio
    autoplay_js = f"""
    <script>
        var audio = new Audio('data:audio/mp3;base64,{audio_bytes.decode("latin1")}');
        audio.play();
    </script>
    """
    st.markdown(autoplay_js, unsafe_allow_html=True)
