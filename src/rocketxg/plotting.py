import matplotlib.pyplot as plt
from scipy import ndimage
import matplotlib.image as mpimg

def plot_field():
    fig, ax = plt.subplots()
    img = mpimg.imread("field.jpeg")
    img = ndimage.rotate(img, angle=90)
    ax.imshow(img, extent=[-4150,4100,-6250,6200])
    return fig, ax