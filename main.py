import asyncio
import pyaudio
import wave
from voicevox import Client
import keyboard
import speech_recognition as sr
from googletrans import Translator
import time
translator = Translator()

voice_chan = 3
voice_virtual = 8
voice_headphone = 6
enterLanguage = "fr-FR"
srcVoice = 'fr'
voiceCharact = 20
TIMEOUT = 10

# fonction pour transcrire la voix en texte
def speech_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source, duration=5)
    try:
        text = r.recognize_google(audio, language=enterLanguage)
        return text
    except sr.UnknownValueError:
        return "Erreur de traitement de l information"
    except sr.RequestError as e:
        return f"Erreur de traitement de l information ; {e}"


# fonction pour enregistrer la voix
def record_voice(device_id, filename):
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_id) as source:
        print("Enregistrement en cours...")
        audio = r.record(source, duration=6)
        print("Enregistrement terminé.")
    with open(filename, "wb") as f:
        f.write(audio.get_wav_data())


def play_wav_on_outputs(wav_file, output_indices):
    CHUNK = 1024

    # Ouverture du fichier WAV
    wf = wave.open(wav_file, 'rb')

    # Initialisation de PyAudio
    p = pyaudio.PyAudio()

    # Ouverture des flux de sortie audio
    stream1 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                     channels=wf.getnchannels(),
                     rate=wf.getframerate(),
                     output_device_index=output_indices[0],
                     output=True)
    stream2 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                     channels=wf.getnchannels(),
                     rate=wf.getframerate(),
                     output_device_index=output_indices[1],
                     output=True)

    # Lecture et envoi du contenu du fichier WAV aux deux sorties audio
    data = wf.readframes(CHUNK)
    while data:
        stream1.write(data)
        stream2.write(data)
        data = wf.readframes(CHUNK)

    # Fermeture des flux de sortie audio et de PyAudio
    stream1.stop_stream()
    stream2.stop_stream()
    stream1.close()
    stream2.close()
    p.terminate()


def translate(text):
    translated = translator.translate(text, src=srcVoice, dest='ja')
    return translated.text


def write_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

last_v_pressed_time = time.time()
async def main():
    print("Logiciel est lancé")
    while True:
        if keyboard.is_pressed('v'):
            ast_v_pressed_time = time.time()
            record_voice(voice_chan, "audio.wav")
            txt1 = speech_to_text("audio.wav")
            txt2 = translate(txt1)
            if txt2 != "情報処理エラー":
                print(txt2)
                async with Client() as client:
                    audio_query = await client.create_audio_query(
                        txt2, speaker=voiceCharact
                    )
                    with open("voice.wav", "wb") as f:
                        f.write(await audio_query.synthesis())
                        print("voice generate")
                write_to_file("text.txt", txt1)
                play_wav_on_outputs('voice.wav', [voice_virtual, voice_headphone])
        if time.time() - last_v_pressed_time > TIMEOUT:
            write_to_file("text.txt", "")
if __name__ == "__main__":
    asyncio.run(main())
