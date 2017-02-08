import numpy as np

def create_power_spectrum(data):
  data = np.fromstring(data, dtype=np.int16)
  left, right = data[0::2], data[1::2]
  lf, rf = abs(np.fft.rfft(left)), abs(np.fft.rfft(right))
  avgf = (lf+rf)/2

  # Downsample into logspace
  buckets = np.logspace(0,5,num=100)
  samples = []
  for i in range(buckets.size-1):
    start = int(buckets[i])
    end = int(buckets[i+1])
    if start == end:
      samples.append(0)
    elif avgf.size > end:
      samples.append(float(avgf[start:end].max()))
    else:
      samples.append(0)

  return samples