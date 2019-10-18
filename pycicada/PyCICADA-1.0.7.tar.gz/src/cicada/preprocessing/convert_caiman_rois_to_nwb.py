from cicada.preprocessing.convert_to_nwb import ConvertToNWB
from cicada.preprocessing.utils import load_tiff_movie_in_memory, update_frames_to_add
from pynwb.ophys import ImageSegmentation, Fluorescence
import numpy as np
from PIL import ImageSequence
import PIL
import PIL.Image as pil_image
import os
import hdf5storage
from scipy import ndimage

class ConvertCaimanRoisToNWB(ConvertToNWB):

    """Class to convert ROIs data from Caiman to NWB"""

    def __init__(self, nwb_file):
        ConvertToNWB.__init__(self, nwb_file)

    def convert(self, **kwargs):
        """Convert the data and add to the nwb_file

        Args:
            **kwargs: arbitrary arguments
        """

        super().convert(**kwargs)

        from_matlab = True
        if "from_matlab" in kwargs:
            from_matlab = bool(kwargs["from_matlab"])

        from_fiji = False
        if "from_fiji" in kwargs:
            from_fiji = bool(kwargs["from_fiji"])
            if from_fiji:
                from_matlab = False

        coords = kwargs.get("coords", None)
        if coords is None:
            raise Exception(f"'coords' argument should be pass to convert "
                            f"function in class {self.__class__.__name__}")

        # looking for the motion_corrected_ci_movie, return None if it doesn't exists
        image_series = self.nwb_file.acquisition.get("motion_corrected_ci_movie")
        if image_series is None:
            raise Exception(f"No calcium imaging movie named 'motion_corrected_ci_movie' found in nwb_file")

        mod = self.nwb_file.create_processing_module('ophys', 'contains optical physiology processed data')
        img_seg = ImageSegmentation(name="segmentation_caiman")
        mod.add_data_interface(img_seg)
        imaging_plane = self.nwb_file.get_imaging_plane("my_imgpln")
        ci_sampling_rate = imaging_plane.imaging_rate
        # description, imaging_plane, name=None
        ps = img_seg.create_plane_segmentation(description='output from segmenting',
                                               imaging_plane=imaging_plane, name='my_plane_seg',
                                               reference_images=image_series)

        if image_series.format == "tiff":
            dim_y, dim_x = image_series.data.shape[1:]
            n_frames = image_series.data.shape[0]
            print(f"dim_y, dim_x: {image_series.data.shape[1:]}")
        elif image_series.format == "external":
            im = PIL.Image.open(image_series.external_file[0])
            n_frames = len(list(ImageSequence.Iterator(im)))
            dim_y, dim_x = np.array(im).shape
            print(f"dim_y, dim_x: {np.array(im).shape}")
        else:
            raise Exception(f"Format of calcium movie imaging {image_series.format} not yet implemented")

        # Add rois
        # ---------------------------
        # we clean coords if not None
        # ---------------------------
        for cell, coord in enumerate(coords):
            if from_matlab:
                # it is necessary to remove one, as data comes from matlab, starting from 1 and not 0
                coord = coord - 1
            # in case it would be floats
            coord = coord.astype(int)
            coords[cell] = coord

        n_cells = len(coords)

        for cell, coord in enumerate(coords):
            if coord.shape[0] == 0:
                print(f'Error: {cell} coord.shape {coord.shape}')
                continue

            if from_fiji:
                image_mask = np.zeros((dim_y, dim_x), dtype="int8")
                image_mask[coord[1, :], coord[0, :]] = 1
            else:
                image_mask = np.zeros((dim_y, dim_x), dtype="int8")
                image_mask[coord[1, :], coord[0, :]] = 1
            # we  use morphology.binary_fill_holes to build pixel_mask from coord
            image_mask = ndimage.binary_fill_holes(image_mask).astype(int)
            pix_mask = np.argwhere(image_mask)
            pix_mask = [(pix[0], pix[1], 1) for pix in pix_mask]
            # we can add id to identify the cell (int) otherwise it will be incremented at each step
            ps.add_roi(pixel_mask=pix_mask, image_mask=image_mask)

        fl = Fluorescence(name="fluorescence_caiman")
        mod.add_data_interface(fl)

        rt_region = ps.create_roi_table_region('all cells', region=list(np.arange(n_cells)))
        if image_series.format == "external":
            print(f"external: {image_series.external_file[0]}")
            if image_series.external_file[0].endswith(".tiff") or \
                    image_series.external_file[0].endswith(".tif"):
                frames_to_add = dict()
                # print(f"ci_sampling_rate {ci_sampling_rate}")
                update_frames_to_add(frames_to_add=frames_to_add, nwb_file=self.nwb_file,
                                     ci_sampling_rate=ci_sampling_rate)
                ci_movie = load_tiff_movie_in_memory(image_series.external_file[0], frames_to_add=frames_to_add)
            else:
                raise Exception(f"Calcium imaging format not supported yet {image_series.external_file[0]}")
        else:
            ci_movie = image_series.data

        if ci_movie is not None:
            raw_traces = np.zeros((n_cells, ci_movie.shape[0]))
            for cell in np.arange(n_cells):
                img_mask = ps['image_mask'][cell]
                img_mask = img_mask.astype(bool)
                raw_traces[cell, :] = np.mean(ci_movie[:, img_mask], axis=1)
            print(f"######## fl.create_roi_response_series raw_traces")
            rrs = fl.create_roi_response_series(name='raw_traces', data=raw_traces, unit='lumens',
                                                rois=rt_region, timestamps=np.arange(n_frames),
                                                description="raw traces")