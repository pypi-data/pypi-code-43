from sys import path

import speech_recognition as sr


def extract_text(inputfile, output):
    r = sr.Recognizer()
    with sr.AudioFile(inputfile) as source:
        audio = r.record(source) # read the entire audio file

    try:
        print("Start recognize")
        with open(output, "w+") as file_txt:
            file_txt.write(r.recognize_sphinx(audio))
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))

    # try:
    #     # for testing purposes, we're just using the default API key
    #     # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    #     # instead of `r.recognize_google(audio)`
    #     with open("feris_test_google.txt", "w+") as file_txt:
    #         file_txt.write(r.recognize_google(audio))
    # except sr.UnknownValueError:
    #     print("Google Speech Recognition could not understand audio")
    # except sr.RequestError as e:
    #     print("Could not request results from Google Speech Recognition service; {0}".format(e))


if __name__ == "__main__":
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "feris_test.wav")