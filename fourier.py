import wave # for reading in wav files
import struct # also for reading wav files
import math # for complex numbers, math.pi and math.e

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
    frameArray = frameArray[0:32768] # must be power of 2
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
        print(frequencyValuePairs[i][0])

main()
