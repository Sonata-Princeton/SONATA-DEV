import numpy as np
import matplotlib.pyplot as plt

# Generate some data that where each slice has a different range
# (The overall range is from 0 to 2)
data = np.random.random((4,10,10))
data *= np.array([0.5, 1.0, 1.5, 2.0])[:,None,None]

# Plot each slice as an independent subplot
fig, axes = plt.subplots(nrows=2, ncols=2)
for dat, ax in zip(data, axes.flat):
    # The vmin and vmax arguments specify the color limits
    im = ax.imshow(dat, vmin=0, vmax=2, cmap='gnuplot')

# Make an axis for the colorbar on the right side
cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
fig.colorbar(im, cax=cax)
