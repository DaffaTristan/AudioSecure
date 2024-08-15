from scipy.io import wavfile
import numpy as np
import pandas as pd
import math

def reverse_string(input_string):
    return input_string[::-1]

wavFilename = '/data/Audio/data1_mono.wav'
payFilename = '/data/Payload/payload1.txt'
### Embedding -------------------------------------------------------------------------------------------------------------
## Step 1 - Read audio and sample to 16-bit and normalize audio sample
samplerate, audiodata = wavfile.read(wavFilename)
print("\nEmbedding Process~~~\n")
print("Length of Audio Sample: ", len(audiodata))
normaudiodata = [x + 32768 for x in audiodata]

## Step 2 - Make interpolation sample between each original sample
interpolasi = np.resize(normaudiodata, ((len(normaudiodata)*2)-1))
x = 0
for i in range(len(interpolasi)):
    # Even Sample (Original Sample)
    if i % 2 == 0:
        interpolasi[i] = normaudiodata[int(i/2)]
    # Odd Sample (Interpolation)
    else:
        interpolasi[i] = math.floor((normaudiodata[int((i-1)/2)]+normaudiodata[i-x])/2)
        x+=1

## Save Interpolation Audio
interpolasi = [x - 32768 for x in interpolasi]
wavfile.write('/results/InterAudio-embed.wav', samplerate, np.array(interpolasi, dtype=np.int16))
wavfile.write('/data/Audio/InterAudio-embed.wav', samplerate, np.array(interpolasi, dtype=np.int16))

## Step 3 - Find variable C
duration = len(interpolasi) / samplerate
C = (duration * 1000)/((len(interpolasi))*2)
print("C = ", C)

## Steps 4 and 5 - Embedding Process
with open(payFilename, 'r') as file:
    payload = file.read()
payload = payload.replace('\t', '')
nSpace = 0
interpolasi = [x + 32768 for x in interpolasi]
truekey = ''
for i in range(len(interpolasi)-1):
    # Step 5 - Odd number (Interpolation)
    if i % 2 != 0:
        key = ''
        if abs(N) == 0:
            key += '00'
        for x in range(abs(N)):
            if len(pn) < abs(N) and x == len(pn):
                break
            r = interpolasi[i] % 2 
            if int(pn[x]) > 0:
                key += '11'
                interpolasi[i] += 1
            elif int(pn[x]) == 0:
                key += '10'
                interpolasi[i] -= 1
        reversed_key = reverse_string(key)
        truekey += reversed_key
        if nSpace > len(payload) or nSpace == len(payload):
            break
    # Step 4 - Even number except last (Original)
    elif i < len(interpolasi):
        d = math.sqrt((i+1-(i+2))**2+(interpolasi[i]-interpolasi[i+1])**2)
        N = math.floor(math.log2(C * d))
        if N == 0:
            pn = 0
            nSpace+=abs(N)
        elif nSpace < len(payload) and (nSpace + abs(N) - 1) < len(payload):
            pn = payload[nSpace:(nSpace+abs(N))]
            nSpace+=abs(N)
        elif nSpace + abs(N) > len(payload):
            pn = payload[nSpace:len(payload)]
            nSpace+=abs(N)
print("Length of Key : ", len(truekey))

## Step 6 - Denormalize and save Stego Audio sample
interpolasi = [x - 32768 for x in interpolasi]
norinterpolasi = [x + 32768 for x in interpolasi]
wavfile.write('/results/StegoAudio-embed.wav', samplerate, np.array(interpolasi, dtype=np.int16))
wavfile.write('/data/Audio/StegoAudio-embed.wav', samplerate, np.array(interpolasi, dtype=np.int16))

## Find PSNR value
isamplerate, iaudiodata = wavfile.read('/data/Audio/InterAudio-embed.wav')
fsamplerate, faudiodata = wavfile.read('/data/Audio/StegoAudio-embed.wav')

# Ensure both signals have the same length
min_length = min(len(iaudiodata), len(faudiodata))
original_audio = iaudiodata[:min_length]
reconstructed_audio = faudiodata[:min_length]

# Calculate the Mean Squared Error (MSE)
tes = (original_audio - reconstructed_audio)
mse = np.mean(tes ** 2)

# Determine the maximum possible value for the audio signal
max_possible_value = 2 ** 16

# Calculate the PSNR value
psnr_value = 10 * np.log10((max_possible_value ** 2) / mse)

print('PSNR value : ', psnr_value)

### Extracting ---------------------------------------------------------------------------------------------------------------------------
## Step 1 - Normalize stego audio
print("\nExtracting Process~~~\n")
normstegodata = [x + 32768 for x in faudiodata]

## Step 2-1 - Divide sample between odd (changed) and even (non-changed) samples
oriSample = np.resize(normstegodata, (int((len(normstegodata)+1)/2)))
paySample = np.resize(normstegodata, (int(len(normstegodata)-((len(normstegodata)+1)/2))))
for i in range(len(normstegodata)):
    # Even samples (original)
    if i % 2 == 0:
        oriSample[int(i/2)] = normstegodata[i]
    # Odd samples (payload-embedded samples)
    else:
        paySample[int((i-1)/2)] = normstegodata[i]
oriSample = [x + 0 for x in oriSample]
paySample = [x + 0 for x in paySample]

## Step 2-2 - Make another sample using interpolation from the divided even sample
stegoInterpolasi = np.resize(oriSample, ((len(oriSample)*2)-1))
x = 0
for i in range(len(stegoInterpolasi)):
    if i % 2 == 0:
        stegoInterpolasi[i] = oriSample[int(i/2)]
    else:
        stegoInterpolasi[i] = math.floor((oriSample[int((i-1)/2)]+oriSample[i-x])/2)
        x+=1

## Step 3-1 - Save the interpolation sample and find variable C
stegoInterpolasi = [x - 32768 for x in stegoInterpolasi]
wavfile.write('/results/InterAudio-extract.wav', samplerate, np.array(stegoInterpolasi, dtype=np.int16))
wavfile.write('/data/Audio/InterAudio-extract.wav', samplerate, np.array(stegoInterpolasi, dtype=np.int16))
stegoDuration = len(stegoInterpolasi) / samplerate
sC = (stegoDuration * 1000)/((len(stegoInterpolasi))*2)
print("C = ", sC)

## Steps 3-2 and 4 - Extraction Process
stegoInterpolasi = [x + 32768 for x in stegoInterpolasi]
spay = ''
y = 1
for z in range(len(stegoInterpolasi)-1):
    # Step 4 - Odd sample (changed sample)
    if z % 2 != 0:
        stegoInterpolasi[z] = paySample[z-y]
        y += 1
        retpay = ''
        if abs(sN) == 0 and truekey[:2] == '00':
            retpay += ''
            truekey = truekey[2:]
        for x in range(abs(sN)):
            if len(truekey) == 0:
                break
            elif truekey[:2] == '01':
                retpay += '0'
                truekey = truekey[2:]
            elif truekey[:2] == '11':
                retpay += '1'
                truekey = truekey[2:]
        reversed_pay = reverse_string(retpay)
        spay += reversed_pay
        if len(truekey) == 0:
            break
    # Step 3-2 - Even sample except last (Original)
    elif z % 2 == 0:
        sd = math.sqrt((z+1-(z+2))**2+(stegoInterpolasi[z]-stegoInterpolasi[z+1])**2)
        sN = math.floor(math.log2(sC * sd))

# Ensure that the payload retrived and the original payload are the same
sPayload = "".join(str(x) for x in spay)
print("Length of Retrieved Payload = ", len(sPayload))
print("Length of Original Payload  = ", len(payload))
rpayload = sPayload[:1] + sPayload[1:len(payload)].replace('', '\t')
truepayload = payload[:1] + payload[1:].replace('', '\t')
pc = ",".join(str(x) for x in payload)

err = 0
for i in range(len(sPayload)):
    if sPayload[i] != payload[i]:
        err+=1
print("How many error = ", err)

# Save Payload
with open('/data/Payload/RetrievedPayload.txt', 'w') as file:
    # Write the data to the file
    file.write(rpayload)
if sPayload[:len(payload)] == payload:
    print("Payload retrieved successfully.")
else:
    # print("Fail to get the payload.")
    raise ValueError("Fail to get the payload.")

with open('/results/RetrievedPayload.txt', 'w') as file:
    # Write the data to the file
    file.write(rpayload)
if sPayload[:len(payload)] == payload:
    print("Payload retrieved successfully.")
else:
    # print("Fail to get the payload.")
    raise ValueError("Fail to get the payload.")

## Step 6 - Denormalize and save Original Audio sample
denormOriSample = [x - 32768 for x in oriSample]
wavfile.write('/results/OriginalAudio-extract.wav', samplerate, np.array(denormOriSample, dtype=np.int16))
wavfile.write('/data/Audio/OriginalAudio-extract.wav', samplerate, np.array(denormOriSample, dtype=np.int16))
ocsamplerate, ocaudiodata = wavfile.read('/data/Audio/OriginalAudio-extract.wav')
if np.array_equal(ocaudiodata, audiodata):
    print("Cover retrieved successfully.")
else:
    print("Cover is not the same as the original.")