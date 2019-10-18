import numpy as np
from keras.models import model_from_json
import time
from deepcinac.utils.utils import horizontal_flip, vertical_flip, v_h_flip, create_one_tiff_file_by_frame, load_movie
from deepcinac.cinac_movie_patch import MoviePatchGeneratorMaskedVersions, MoviePatchData
from deepcinac.utils.cells_map_utils import CellsCoord, create_cells_coord_from_suite_2p
import PIL
import os
from abc import ABC, abstractmethod
from ScanImageTiffReader import ScanImageTiffReader
from PIL import ImageSequence
import scipy.io as sio
from shapely.geometry import MultiPoint, LineString
from datetime import datetime


class CinacMovie(ABC):
    def __init__(self):
        self.dimensions = None
        self.n_frames = 0

    @abstractmethod
    def get_frames_section(self, frames, minx, maxx, miny, maxy):
        pass

    def get_dimensions(self):
        """
        Get x and y dimensions of the movie
        Returns: a 1d array of integers

        """
        return self.dimensions

    def get_n_frames(self):
        """
        The number of frames in the movie
        Returns: integer

        """
        return self.n_frames


class CinacDataMovie(CinacMovie):
    """
    Take the movie as a 2d array directly
    """
    def __init__(self, movie, already_normalized=False):
        super().__init__()

        if already_normalized:
            self.movie_normalized = movie
        else:
             self.movie_normalized = movie - np.mean(movie)
             self.movie_normalized = self.movie_normalized / np.std(movie)
        self.n_frames = len(self.movie_normalized)
        self.dimensions = self.movie_normalized.shape[1:]

    def get_frames_section(self, frames, minx, maxx, miny, maxy):
        return self.movie_normalized[frames, miny:maxy + 1, minx:maxx + 1]

class CinacTiffMovie(CinacMovie):
    def __init__(self, tiff_file_name=None, tiff_movie=None):
        super().__init__()
        if tiff_movie is None:
            if tiff_file_name is None:
                raise Exception("tiff_file_name and tiff_movie can't both be set to None.")
            self.tiff_movie_normalized = load_movie(file_name=tiff_file_name, with_normalization=True, verbose=True)

        self.n_frames = len(self.tiff_movie_normalized)
        self.dimensions = self.tiff_movie_normalized.shape[1:]

    def get_frames_section(self, frames, minx, maxx, miny, maxy):
        return self.tiff_movie_normalized[frames, miny:maxy + 1, minx:maxx + 1]

class CinacSplitedTiffMovie(CinacMovie):

    def __init__(self, identifier, tiffs_dirname, tiff_file_name=None, tiff_movie=None):
        """

        Args:
            identifier: string
            tiffs_dirname: dirname of where to save the tiffs created
            tiff_file_name: string, if not None, will create a tiff by frame from this tiff movie if not already done.
            Will be saved in tiffs_dirname. If tiff_movie is not None, the tiff movie will be chosen.
            tiff_movie: numpy 3d array f not None, will create a tiff by frame from this tiff movie if not already done.
            Will be saved in tiffs_dirname.
        """
        super().__init__()
        self.tiffs_dirname = tiffs_dirname
        self.identifier = identifier

        # first if tiff_file_name or tiff_movie are not None, it means we should try to create the SplittedTiffVersion
        # if they doesn't exist yet
        if tiff_file_name is not None or tiff_movie is not None:
            movies_to_split = dict()
            if tiff_movie is not None:
                movies_to_split[identifier] = tiff_movie
            else:
                movies_to_split[identifier] = tiff_file_name
            # won't do anything if the tiffs already have been created
            create_one_tiff_file_by_frame(movies_to_split=movies_to_split, results_path=tiffs_dirname)

        self.tiff_movie_mean = None
        self.tiff_movie_std = None

        file_names = []

        # look for filenames in the fisrst directory, if we don't break, it will go through all directories
        for (dirpath, dirnames, local_filenames) in os.walk(os.path.join(self.tiffs_dirname, self.identifier)):
            file_names.extend(local_filenames)
            break

        # we loop in the directory filenames in order to set the mean and std of the movie and count how many frames
        # are in the movie (according they have all be saved correctly)
        self.n_frames = 0
        for file_name in file_names:
            if file_name.endswith("mean.npy"):
                mean_value = np.load(os.path.join(self.tiffs_dirname, self.identifier, file_name))
                self.tiff_movie_mean = mean_value
            elif file_name.endswith("std.npy"):
                std_value = np.load(os.path.join(self.tiffs_dirname, self.identifier, "std.npy"))
                self.tiff_movie_std = std_value
            elif file_name.endswith("tiff") or file_name.endswith("tif"):
                self.n_frames += 1
                if self.dimensions is None:
                    im = PIL.Image.open(os.path.join(self.tiffs_dirname, self.identifier, file_name))
                    im = np.array(im)
                    self.dimensions = im.shape

    def get_frames_section(self, frames_indices, minx, maxx, miny, maxy):
        """
        get section of given frames from the calcium imaging movie
        Args:
            frames_indices: numpy array of integers, representing the frame's indices to select
            minx: integer, min x coordinate
            maxx: integer, max x coordinate
            miny: integer, min y coordinate
            maxy: integer, max y coordinate

        Returns:

        """

        frames_section = np.zeros((len(frames_indices), maxy - miny + 1, maxx - minx + 1))
        for frame_index, frame in enumerate(frames_indices):
            try:
                im = ScanImageTiffReader(os.path.join(self.tiffs_dirname,
                                                      self.identifier, f"{frame}.tiff")).data()
            except Exception as e:
                im = PIL.Image.open(os.path.join(self.tiffs_dirname,
                                                 self.identifier, f"{frame}.tiff"))
                im = np.array(im)
            frames_section[frame_index] = im[miny:maxy + 1, minx:maxx + 1]
        # normalizing using the mean and std from the whole movie
        frames_section = (frames_section - self.tiff_movie_mean) / self.tiff_movie_std
        return frames_section


class CinacRecording:
    # TODO: add fields that will contains the ground truth

    def __init__(self, identifier):
        self.cinac_movie = None
        self.identifier = identifier
        self.coord_obj = None

    def set_movie(self, cinac_movie):
        """
        Set the instance of CinacMovie, that will be used to get the frames given to the network
        Args:
            cinac_movie:

        Returns:

        """
        self.cinac_movie = cinac_movie

    def set_rois_from_suite_2p(self, is_cell_file_name, stat_file_name):
        """

        Args:
            is_cell_file_name: path and file_name of the file iscell.npy produce by suite2p segmentation process
            stat_file_name: path and file_name of the file stat.npy produce by suite2p segmentation process

        Returns:

        """
        if self.cinac_movie is None:
            raise Exception(f"cinac_movie should be set using the method set_movie() before setting the Rois")
        pass

        self.coord_obj = create_cells_coord_from_suite_2p(is_cell_file_name=is_cell_file_name,
                                                          stat_file_name=stat_file_name,
                                                          movie_dimensions=self.cinac_movie.get_dimensions())

    def set_rois_2d_array(self, coord, from_matlab):
        """

        Args:
            coord: numpy array of 2d, first dimension of length 2 (x and y) and 2nd dimension of length the number of
            cells. Could also be a list of lists or tuples of 2 integers
            from_matlab: Indicate if the data has been computed by matlab, then 1 will be removed to the coordinates
            so it starts at zero.

        Returns:

        """
        if self.cinac_movie is None:
            raise Exception(f"cinac_movie should be set using the method set_movie() before setting the Rois")
        dimensions = self.cinac_movie.get_dimensions()
        self.coord_obj = CellsCoord(coords=coord, nb_lines=dimensions[0], nb_col=dimensions[1], from_matlab=from_matlab)

    def set_rois_from_nwb(self, nwb_data, name_module, name_segmentation, name_seg_plane):
        """

        Args:
            nwb_data: nwb object instance
            name_module: Name of the module to find segmentation. Will be used this way: nwb_data.modules[name_module]
                Ex: name_module = 'ophys'
            name_segmentation: Name of the segmentation in which find the plane segmentation.
                Used this way:get_plane_segmentation(name_segmentation)
                Ex: name_segmentation = 'segmentation_suite2p'
            name_seg_plane: Name of the segmentation plane in which to find the ROIs data
            Used this way: mod[name_segmentation]get_plane_segmentation(name_seq_plane)
                Ex: name_segmentation = 'my_plane_seg'

        Returns:

        """
        if self.cinac_movie is None:
            raise Exception(f"cinac_movie should be set using the method set_movie() before setting the Rois")
        mod = nwb_data.modules[name_module]
        plane_seg = mod[name_segmentation].get_plane_segmentation(name_seg_plane)

        if 'pixel_mask' not in plane_seg:
            raise Exception("'pixel_mask' has to exist in plane_segmentation in order to create ROIs")

        self.set_rois_using_pixel_mask(pixel_masks=plane_seg['pixel_mask'])

    def set_rois_using_pixel_mask(self, pixel_masks):
        """

        Args:
            pixel_masks: list of list of 2 integers representing for each cell all the pixels that belongs to the cell

        Returns:

        """
        if self.cinac_movie is None:
            raise Exception(f"cinac_movie should be set using the method set_movie() before setting the Rois")

        # TODO: use pixel_mask instead of using the coord of the contour of the cell
        #  means changing the way coord_cell works
        coord_list = []
        for cell in np.arange(len(pixel_masks)):
            pixels_coord = pixel_masks[cell]
            list_points_coord = [(pix[0], pix[1]) for pix in pixels_coord]
            convex_hull = MultiPoint(list_points_coord).convex_hull
            if isinstance(convex_hull, LineString):
                coord_shapely = MultiPoint(list_points_coord).convex_hull.coords
            else:
                coord_shapely = MultiPoint(list_points_coord).convex_hull.exterior.coords
            coord_list.append(np.array(coord_shapely).transpose())

        dimensions = self.cinac_movie.get_dimensions()
        self.coord_obj = CellsCoord(coords=coord_list, nb_lines=dimensions[0], nb_col=dimensions[1],
                                    from_matlab=False)


    def get_n_frames(self):
        """
        Return the number of frames in the movie
        Returns:

        """
        return self.cinac_movie.get_n_frames()

    def get_n_cells(self):
        return self.coord_obj.n_cells

    def get_source_profile_frames(self, frames_indices, coords):
        """
        Return frames section based on the indices of the frames and the coordinates of the corners of the section
        Args:
            frames_indices: array of integers
            coords: tuple of 4 integers: (minx, maxx, miny, maxy)

        Returns: A numpy array of dimensions len(frames_indices) * (maxy - miny + 1) * (maxx - minx + 1)

        """

        frames_section = self.cinac_movie.get_frames_section(frames_indices, *coords)

        return frames_section


def load_data_for_prediction(cinac_recording, cell, sliding_window_len, overlap_value,
                             augmentation_functions, n_frames):
    """
    Create data that will be used to predict neural activity. The data will be representing by instances of
    MoviePatchData that will contains information concerning this movie segment for a given
    cell to give to the neuronal network.
    Args:
        cinac_recording: instance of CinacRecording, contains the movie frames and the ROIs
        cell: integer, the cell index
        sliding_window_len: integer, length in frames of the window used by the neuronal network. Predictions will be
        made for each frame of this segment
        overlap_value: float value between 0 and 1, representing by how much 2 movie segments will overlap.
        0.5 is equivalent to a 50% overlap. It allows the network to avoid edge effect in order to get a full temporal
        vision of all transient. A good default value is 0.5
        augmentation_functions: list of function that takes an image (np array) as input and return a copy of the image
        transformed.
        n_frames: number of frames in the movie

    Returns: a list of MoviePatchData instance and an integer representing the index of the first frame of the patch

    """
    # n_frames is None, the movie need to have been loaded
    # we suppose that the movie is already loaded and normalized
    movie_patches = []
    data_frame_indices = []
    frames_step = int(np.ceil(sliding_window_len * (1 - overlap_value)))
    # number of indices to remove so index + sliding_window_len won't be superior to number of frames
    n_step_to_remove = 0 if (overlap_value == 0) else int(1 / (1 - overlap_value))
    frame_indices_for_movies = np.arange(0, n_frames, frames_step)
    if n_step_to_remove > 0:
        frame_indices_for_movies = frame_indices_for_movies[:-n_step_to_remove + 1]
    # in case the n_frames wouldn't be divisible by frames_step
    if frame_indices_for_movies[-1] + frames_step > n_frames:
        frame_indices_for_movies[-1] = n_frames - sliding_window_len

    for i, index_movie in enumerate(frame_indices_for_movies):
        break_it = False
        first_frame = index_movie
        if (index_movie + sliding_window_len) == n_frames:
            break_it = True
        elif (index_movie + sliding_window_len) > n_frames:
            # in case the number of frames is not divisible by sliding_window_len
            first_frame = n_frames - sliding_window_len
            break_it = True
        movie_data = MoviePatchData(cinac_recording=cinac_recording, cell=cell, index_movie=first_frame,
                                    window_len=sliding_window_len,
                                    max_n_transformations=3,
                                    with_info=False, encoded_frames=None,
                                    decoding_frame_dict=None)

        movie_patches.append(movie_data)
        data_frame_indices.append(first_frame)
        if augmentation_functions is not None:
            for augmentation_fct in augmentation_functions:
                new_movie = movie_data.copy()
                new_movie.data_augmentation_fct = augmentation_fct
                movie_patches.append(new_movie)
                data_frame_indices.append(first_frame)

        if break_it:
            break

    return movie_patches, data_frame_indices


def predict_transient_from_model(cinac_recording, cell, model,
                                 n_frames, overlap_value=0.8, pixels_around=0,
                                 use_data_augmentation=False, buffer=None):
    # if n_frames is None, then the movie need to have been loaded
    start_time = time.time()
    # multi_inputs = (model.layers[0].output_shape == model.layers[1].output_shape)
    window_len = model.layers[0].output_shape[1]
    max_height = model.layers[0].output_shape[2]
    max_width = model.layers[0].output_shape[3]

    # Determining how many classes were used
    if len(model.layers[-1].output_shape) == 2:
        using_multi_class = 1
    else:
        using_multi_class = model.layers[-1].output_shape[2]
        # print(f"predict_transient_from_model using_multi_class {using_multi_class}")

    if use_data_augmentation:
        augmentation_functions = [horizontal_flip, vertical_flip, v_h_flip]
    else:
        augmentation_functions = None
    # start_time_bis = time.time()
    movie_patches, data_frame_indices = load_data_for_prediction(cinac_recording=cinac_recording,
                                                                 cell=cell,
                                                                 sliding_window_len=window_len,
                                                                 overlap_value=overlap_value,
                                                                 augmentation_functions=augmentation_functions,
                                                                 n_frames=n_frames)
    # stop_time_bis = time.time()
    # print(f"Time to get load_data_for_prediction: "
    #       f"{np.round(stop_time_bis - start_time_bis, 3)} s")

    movie_patch_generator = \
        MoviePatchGeneratorMaskedVersions(window_len=window_len, max_width=max_width, max_height=max_height,
                                          pixels_around=pixels_around, buffer=buffer, with_neuropil_mask=True,
                                          using_multi_class=using_multi_class)

    data_dict = movie_patch_generator.generate_movies_from_metadata(movie_data_list=movie_patches,
                                                                    with_labels=False)

    stop_time = time.time()
    print(f"Time to get the data: "
          f"{np.round(stop_time - start_time, 3)} s")
    start_time = time.time()

    predictions = model.predict(data_dict)

    stop_time = time.time()
    print(f"Time to get predictions for cell {cell}: "
          f"{np.round(stop_time - start_time, 3)} s")

    # now we want to take the prediction with the maximal value for a given frame
    # the rational being that often if a transient arrive right at the end or the beginning
    # it won't be recognized as True
    if (overlap_value > 0) or (augmentation_functions is not None):
        frames_predictions = dict()
        # print(f"predictions.shape {predictions.shape}, data_frame_indices.shape {data_frame_indices.shape}")
        for i, data_frame_index in enumerate(data_frame_indices):
            frames_index = np.arange(data_frame_index, data_frame_index + window_len)
            predictions_for_frames = predictions[i]
            for j, frame_index in enumerate(frames_index):
                if frame_index not in frames_predictions:
                    frames_predictions[frame_index] = dict()
                if len(predictions_for_frames.shape) == 1:
                    if 0 not in frames_predictions[frame_index]:
                        frames_predictions[frame_index][0] = []
                    frames_predictions[frame_index][0].append(predictions_for_frames[j])
                else:
                    # then it's muti_class labels
                    for index in np.arange(len(predictions_for_frames[j])):
                        if index not in frames_predictions[frame_index]:
                            frames_predictions[frame_index][index] = []
                        frames_predictions[frame_index][index].append(predictions_for_frames[j, index])

        predictions = np.zeros((n_frames, using_multi_class))
        for frame_index, class_dict in frames_predictions.items():
            for class_index, prediction_values in class_dict.items():
                # max value
                predictions[frame_index, class_index] = np.max(prediction_values)
    else:
        # to flatten all but last dimensions
        predictions = np.ndarray.flatten(predictions)

        # now we remove the extra prediction in case the number of frames was not divisible by the window length
        if (n_frames % window_len) != 0:
            print("(n_frames % window_len) != 0")
            real_predictions = np.zeros((n_frames, using_multi_class))
            modulo = n_frames % window_len
            real_predictions[:len(predictions) - window_len] = predictions[
                                                               :len(predictions) - window_len]
            real_predictions[len(predictions) - window_len:] = predictions[-modulo:]
            predictions = real_predictions

    if len(predictions) != n_frames:
        raise Exception(f"predictions len {len(predictions)} is different from the number of frames {n_frames}")

    return predictions


class CinacPredictor:

    def __init__(self):
        self.recordings = []
        print("CinacPredictor init")

    def add_recording(self, cinac_recording, model_files_dict=None, removed_cells_mapping=None):
        """
        Add a recording as a set of a calcium imaging movie, ROIs, and a list of cell to predict
        Args:
            cinac_recording: an instance of CinacRecording
            model_files_dict: dictionary. Key is a tuple of three string representing the file_name of the json file,
              the filename of the weights file and network_identifier and an identifier for the model
             and weights used (will be added to the name of files containing the predictions
             in addition of recording identifier.)
             the value of the dict being a list or array of integers that represents
             the indices of the cell to be predicted by the given model and set of weights.
             If None, means all cells activity will be predicted. Cells not including, will have their prediction
             set to 0 for all the frames
            removed_cells_mapping: integers array of length the original numbers of cells
            (such as defined in CinacRecording)
            and as value either of positive int representing the new index of the cell or -1 if the cell has been
            removed

        Returns:

        """
        self.recordings.append((cinac_recording, model_files_dict, removed_cells_mapping))

    @staticmethod
    def get_new_cell_indices_if_cells_removed(cell_indices_array, removed_cells_mapping):
        """
        Take an array of int, and return another one with new index in case some cells would have been removed
        and some cells ROIs are not matching anymore
        Args:
            cell_indices_array: np.array of integers, containing the cells indices to remap
            removed_cells_mapping: integers array of length the original numbers of cells
            (such as defined in CinacRecording)
            and as value either of positive int representing the new index of the cell or -1 if the cell has been
            removed

        Returns: new_cell_indices_array an np.array that contains integers representing the new indices of cells that
        have not been removed
        original_cell_indices_mapping, np.array, for each new cell index, contains the corresponding original index

        """

        if removed_cells_mapping is None:
            return np.copy(cell_indices_array), np.copy(cell_indices_array)

        new_cell_indices_array = removed_cells_mapping[cell_indices_array]
        # removing cell indices of cell that has been removed
        copy_new_cell_indices_array = np.copy(new_cell_indices_array)
        new_cell_indices_array = new_cell_indices_array[new_cell_indices_array >= 0]
        original_cell_indices_mapping = np.copy(cell_indices_array[copy_new_cell_indices_array >= 0])

        return new_cell_indices_array, original_cell_indices_mapping

    def predict(self, results_path, overlap_value=0.5, output_file_formats="npy", **kwargs):
        """
        Will predict the neural activity state of the cell for each frame of the calcium imaging movies.
        Recordings have to be added previously though the add_recording method.
        Args:
            results_path:
            overlap_value:
            output_file_formats: a string or list of string, representing the format in which saving the 2d array
            representing the prediction for each movie. The choices are: "mat" or "npy". If "mat", matlab format, then
            the predictions named will be "predictions"
            **kwargs:


        Returns: None

        """

        use_data_augmentation = False
        if "use_data_augmentation" in kwargs:
            use_data_augmentation = kwargs["use_data_augmentation"]

        # output_file_formats = "npy"
        if "output_file_formats" in kwargs:
            output_file_formats = kwargs["output_file_formats"]

        # dictionary that will contains the predictions results. Keys are the CinacRecording identifiers
        predictions_dict = dict()
        for recording in self.recordings:
            cinac_recording, model_files_dict, removed_cells_mapping = recording
            n_cells = cinac_recording.get_n_cells()
            n_frames = cinac_recording.get_n_frames()

            for file_names, cells_to_predict in model_files_dict.items():
                json_model_file_name, weights_file_name, network_identifier = file_names
                # ms.tiffs_for_transient_classifier_path = tiffs_for_transient_classifier_path

                if cells_to_predict is None:
                    cells_to_load = np.arange(n_cells)
                else:
                    cells_to_load = np.array(cells_to_predict)

                cells_to_load, \
                original_cell_indices_mapping = self.get_new_cell_indices_if_cells_removed(cells_to_load,
                                                                                           removed_cells_mapping)
                total_n_cells = len(cells_to_load)
                # print(f'total_n_cells {total_n_cells}')

                if total_n_cells == 0:
                    print(f"No cells loaded for {cinac_recording.identifier}")
                    continue

                # print(f"transients_prediction_from_movie n_frames {n_frames}")
                # we keep the original number of cells, so if a different segmentation was used another prediction,
                # we can still compare it using the indices we know
                predictions_by_cell = np.zeros((n_cells, n_frames))

                # loading model
                # Model reconstruction from JSON file
                with open(json_model_file_name, 'r') as f:
                    model = model_from_json(f.read())

                # Load weights into the new model
                model.load_weights(weights_file_name)

                start_time = time.time()
                predictions_threshold = 0.5
                # in case we want to use tqdm
                # for cell_index in tqdm(range(len(cells_to_load)),
                #                              desc=f"{cinac_recording.identifier} - {network_identifier}"):
                #     cell = cells_to_load[cell_index]
                for cell_index in range(len(cells_to_load)):
                    cell = cells_to_load[cell_index]
                    original_cell = original_cell_indices_mapping[cell_index]
                    predictions = predict_transient_from_model(cinac_recording=cinac_recording,
                                                               cell=cell, model=model, overlap_value=overlap_value,
                                                               use_data_augmentation=use_data_augmentation,
                                                               n_frames=n_frames)
                    if len(predictions.shape) == 1:
                        predictions_by_cell[original_cell] = predictions
                    elif (len(predictions.shape) == 2) and (predictions.shape[1] == 1):
                        predictions_by_cell[original_cell] = predictions[:, 0]
                    elif (len(predictions.shape) == 2) and (predictions.shape[1] == 3):
                        # real transient, fake ones, other (neuropil, decay etc...)
                        # keeping predictions about real transient when superior
                        # to other prediction on the same frame
                        max_pred_by_frame = np.max(predictions, axis=1)
                        real_transient_frames = (predictions[:, 0] == max_pred_by_frame)
                        predictions_by_cell[original_cell, real_transient_frames] = 1
                    elif predictions.shape[1] == 2:
                        # real transient, fake ones
                        # keeping predictions about real transient superior to the threshold
                        # and superior to other prediction on the same frame
                        max_pred_by_frame = np.max(predictions, axis=1)
                        real_transient_frames = np.logical_and((predictions[:, 0] >= predictions_threshold),
                                                               (predictions[:, 0] == max_pred_by_frame))
                        predictions_by_cell[original_cell, real_transient_frames] = 1

            stop_time = time.time()
            print(f"Time to predict {total_n_cells} cells: "
                  f"{np.round(stop_time - start_time, 3)} s")
            if isinstance(output_file_formats, str):
                output_file_formats = [output_file_formats]

            # TODO: use all network_identifier if more than one
            if network_identifier is None:
                network_identifier = ""
            else:
                network_identifier = "_" + network_identifier

            time_str = datetime.now().strftime("%Y_%m_%d.%H-%M-%S")
            new_dir_results = os.path.join(results_path, f"{time_str}/")
            os.mkdir(new_dir_results)

            file_name = f"{cinac_recording.identifier}_predictions{network_identifier}"
            for output_file_format in output_file_formats:
                if "mat" in output_file_format:
                    sio.savemat(os.path.join(new_dir_results, file_name + ".mat"), {'predictions': predictions_by_cell})
                elif "npy" in output_file_format:
                    np.save(os.path.join(new_dir_results, file_name + ".npy"), predictions_by_cell,
                            allow_pickle=True)
            predictions_dict[cinac_recording.identifier] = predictions_by_cell

        return predictions_dict
