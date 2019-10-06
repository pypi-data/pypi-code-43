# split images into NxN pieces

import image_splitter


def main():

    tiles = image_slicer.slice("cake.jpg", 4, save=False)
    image_slicer.save_tiles(tiles, directory="~/cake_slices", prefix="slice", format="jpg")


if __name__ == "__main__":
    main()
