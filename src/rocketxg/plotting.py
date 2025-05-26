from pathlib import Path
import matplotlib.pyplot as plt
from scipy import ndimage
import matplotlib.image as mpimg


def get_asset_path(relative_path: str) -> Path:
    """Get absolute path to asset from a relative path."""
    script_dir = Path(__file__).parent
    return (script_dir / relative_path).resolve()


def plot_field(vertical: bool = True):
    fig, ax = plt.subplots()
    field_path = get_asset_path("../assets/field.png")
    img = mpimg.imread(field_path)
    if vertical:
        img = ndimage.rotate(img, angle=90)
        ax.imshow(img, extent=[-4096,4096,-6000,6000], zorder=10)
        ax.set_xlim(-4500, 4500)
        ax.set_ylim(-6500, 6500)
    else:
        ax.imshow(img, extent=[-6000,6000,-4096,4096], zorder=10)
        ax.set_xlim(-6500, 6500)
        ax.set_ylim(-4500, 4500)
    return fig, ax
