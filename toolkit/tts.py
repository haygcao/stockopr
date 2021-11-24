import pyttsx3
engine = pyttsx3.init()   # object creation

""" RATE"""
rate = engine.getProperty('rate')   # getting details of current speaking rate
engine.setProperty('rate', 150)     # setting up new voice rate

"""VOLUME"""
volume = engine.getProperty('volume')   # getting to know current volume level (min=0 and max=1)
engine.setProperty('volume', 1.0)    # setting up volume level  between 0 and 1

"""VOICE"""
voices = engine.getProperty('voices')       # getting details of current voice
# 67 - Mandarin 普通话
# engine.setProperty('voice', voices[0].id)   # changing index, changes voices. o for male, #changing index, changes voices. 1 for female
engine.setProperty('voice', 'zh')
# engine.setProperty('voice', 'Mandarin')


def say(txt):
    print(txt)
    engine.say(txt)
    engine.runAndWait()
    engine.stop()


def read(path='tts.txt'):
    with open(path, 'rb') as f:
        txt = f.read().decode()
    engine.say(txt)
    engine.runAndWait()
    engine.stop()


def save(txt):
    """Saving Voice to a file"""
    # On linux make sure that 'espeak' and 'ffmpeg' are installed
    engine.save_to_file(txt, 'tts.mp3')

    engine.runAndWait()
    engine.stop()


# from playsound import playsound
# playsound('/path/to/a/sound/file/you/want/to/play.mp3')

if __name__ == '__main__':
    say('hello world')
    say('注意， 买入， 3 0 0')
