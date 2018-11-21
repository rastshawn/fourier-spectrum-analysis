import wave # for reading in wav files
import struct # also for reading wav files
import math # for complex numbers, math.pi and math.e






def getPitchFromFrequency(frequency):
	# https://en.wikipedia.org/wiki/Cent_(music)

	# convert hertz to cents
	
	# we need something to base all of the calculations on
	# octaves increment to the next octave at C, not A, so these things will look out of order
	# trust me it works
	c_zero = 16.35 # C0 is 16.35 Hz
	
	# number of cents between a note and a_zero is 1200 * log2(b / a_zero)
	# so number of half steps is 12 * log2(b / a_zero)
	# where b is the hertz of the second note

	log2 = math.log(frequency / c_zero) / math.log(2)

	cents_from_C = 1200 * log2
	half_steps_from_C = cents_from_C / 100

	# for each cent, cycle through ABCDEFG and then 0+
	notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
	octave = 0
	
	index = int(half_steps_from_C % 12)	
	note = notes[index]
	octave = int(half_steps_from_C / 12) # probably have to convert to int

	return str(note) + str(octave)



# this takes a filename / relative path to a wav file 
# it returns an array of signed shorts, 
# corresponding to the sound pressure level / voltage of the 
# file at that point. 
# it is normalized. 
def getFrameArray(filename):
    wavFile = wave.open(filename, 'rb')
    nextFrame = wavFile.readframes(1)
    frameArray = []
    while nextFrame:
        num = struct.unpack("<h", nextFrame)[0]
        frameArray.append(num)
        nextFrame = wavFile.readframes(1)

    return frameArray

# This is a Fast Fourier Transform using the Cooley–Tukey algorithm.
# It calculates a discrete fourier transform in nlog(n) time.
def fft(frames, n):

    ## these next two lines force n or n/2 into ints so range(n/2) works
    n = int(n)
    half = int(n/2)

    # if there's only one element in the remaining array
    # just return it; there's no further processing to do
    if n<2: return frames

    # separate the frames into two arrays 
    # one for even indexes, one for odd
    left = []
    right = []
    for i in range(0, n):
        if i%2 == 1:
            left.append(frames[i])
        else:
            right.append(frames[i])
    
    # keep recursing through to the left and right arrays
    left = fft(left, half)
    right = fft(right, half)
    
    # only go to half, because the second half of n
    # just repeats the first half. No need to do double
    # the calculations
    for i in range(0, half):
        e = left[i]
        o = right[i]

        # w is the magic bit - this is where the waveform is 
        # "wrapped around" a circle. This allows the overall 
        # center of mass for the wavform (around the circle)
        # to be calculated, which in a sense represents
        # how strong that particular frequency is 
        # in the complex waveform. 
        w = math.e ** complex(0, -2.0 * math.pi * i/n)
        left[i] = e + w * o
        right[i] = e - w * o

    for x in right:
        left.append(x)

    return left

def main(): 
    print(
        "This is a multi-note pitch detector. It works best with only "+
        "a few notes at a time ( < 3 or so ) but theoretically " + 
        "can work with more. More notes in a recording lead to more " +
        "problems with harmonics."
    )

    print(
        "Enter the file you'd like to process. This will only process " + 
        "the first second of the file, and the file must be a " + 
        "mono wav file with a 44.1khz sample rate. Enter a relative path."
    )

    filename = input("Filename: ")
    print("How many frequencies do you want to detect?")
    numFrequencies = int(input("Number of frequencies: "))
    processFile(filename, numFrequencies)

def processFile(filename, numPitches):
    frameArray = getFrameArray(filename)


	# to use only a fixed length of time, use the commented line. 
    frameArray = frameArray[0:32768] # must be power of 2

	# shorten the number of frames down to a power of two

    n = len(frameArray)
    ff = fft(frameArray, n)
    sampleRate = 44100.0

    frequencyValuePairs = []
    outputFreq = 0
    i = 0 
    while outputFreq < 2000:
        outputFreq = (i) * (sampleRate / n)
        val = abs(ff[i]) / n
        
        frequencyValuePairs.append(
            [ outputFreq , val ]
        )

        #if val > 1000:
        #    print("%dhz: %d" % (outputFreq, val))
        
        i += 1

    frequencyValuePairs.sort(key=lambda x: x[1], reverse=True)

    print("the %d top pitches are:" % (numPitches))
    for i in range(0, numPitches):
        print(getPitchFromFrequency(frequencyValuePairs[i][0]))

main()


# ideas
# use standard deviations to see how many peaks there are?
# use a lookup table to figure out pitch
# pass in sound file from command line arg
# use with recordings - instead of passing by 1-second chunks, pass instead by a rolling one-second chunk of frames
# make fft work with frame counts that are not a power of 2, or alternatively a 1-second rolling chunk to skip the problem entirely

 
