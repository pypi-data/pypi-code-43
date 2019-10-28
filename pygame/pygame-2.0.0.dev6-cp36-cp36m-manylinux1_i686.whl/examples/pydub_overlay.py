from pydub import AudioSegment

# from pydub.playback import play

sound1 = AudioSegment.from_wav("data/boom.wav")
sound2 = AudioSegment.from_wav("data/punch.wav")

# mix sound2 with sound1, starting at 5000ms into sound1)
# output = sound1.overlay(sound2, position=5000)
output = sound1.overlay(sound2)
# play(output)

# save the result
output.export("/tmp/mixed_sounds.wav", format="wav")
