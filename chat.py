import os
import asyncio
import speech_recognition as sr
import google.generativeai as genai
import serial
import pygame
import time
from gtts import gTTS

# Serial port sozlamalari
ser = serial.Serial('COM6', 9600, timeout=1)
lk = [0, 0, 0, 0]
print("ulandi!")
# Pygame audio sozlamalari
pygame.mixer.init()

class Chat:
    def __init__(self, start):
        genai.configure(api_key="TOKEN")
        model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat = model.start_chat()
        self.chat.send_message(start)

    def ask(self, prompt):
        response = self.chat.send_message(prompt)
        return response.text

    def listen(self,source=None):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Buyruqni tinglamoqda...")
            audio = recognizer.listen(source, timeout=15)
            try:
                text = recognizer.recognize_google(audio, language="uz")
                print(f"Siz dedingiz: {text}")
                return text
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                return None

    def holat(self, response_text):
        try:
            c = response_text.split(" = ")[1].strip()[1:-1].split(", ")
            if len(c) < 4:
                c = response_text.split(" = ")[1].strip()[1:-1].split(",")
        except:
            c = response_text.split(": ")[1].strip()[1:-1].split(", ")
            if len(c) < 4:
                c = response_text.split(": ")[1].strip()[1:-1].split(",")

        return list(map(int, c))
    def speak(self, text):
        filename = "voice.mp3"
        try:
            # Agar fayl mavjud bo‘lsa, o‘chirib tashlash
            if os.path.exists(filename):
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                os.remove(filename)

            # TTS orqali saqlash
            tts = gTTS(text=text, lang="tr")
            tts.save(filename)

            # Ovoz chiqarish
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            # Ovoz chiqib bo‘lgach, faylni o‘chirish
            os.remove(filename)

        except Exception as e:
            print("Ovoz chiqarishda xatolik:", e)

        print(text)

# Chat obyektini yaratish
a = Chat("Sen aqilli uy tizimisan. Sening vazifang uyni boshqarish va savollarimga qisqa javob berish. "
         "Sen boshqarishing mumkin bo‘lgan narsa 4 ta elektr razetka. Har chat oxirida  holat = {0,0,0,0} "
         "ko‘rinishida portlar holatini berib borasan. Tizim o‘zi buni moslaydi, biz sendan buni o‘zgartirishni so‘raganimizda "
         "raqamlarni o‘zgartirasan.")

# Razetka portlari belgilari
l = [["b", "B"], ["i", "I"], ["u", "U"], ["t", "T"]]

# Asosiy sikl
while True:
    k = a.listen()
    if not k:
        continue
    n = a.ask(k)
    c=a.holat(c)
    n = n.lower().split("holat")[0].strip()
    a.speak(n)

    for i in range(4):
        if lk[i] != c[i]:
            ser.write(l[i][c[i]].encode("ascii"))
    lk = c
    print("Yangi holat:", c)
