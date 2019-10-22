import os
import imageio
import imagehash
from PIL import Image
from .ailab_multiprocessing import pool_worker


def __get_average_hash(path):
    im = Image.open(path)
    return imagehash.average_hash(im)


def __extract_distinct_hash_indexes(hashes, min_distant=2):
    distinct_indexs = [0]
    for i in range(1, len(hashes)):
        for idx in distinct_indexs:
            if hashes[i] - hashes[idx] < min_distant:
                break
        else:
            distinct_indexs.append(i)
    return distinct_indexs

def extract_distinct_video(video_path, dest_dir, size=None, fps=1, min_distant=2, num_worker=None, verbose=True):
    """Extract distinct frame of video and save to dest_dir

    Parameters
    ----------
    video_path : str
        path of video
    dest_dir: str
        path of directory to save frames
    size: (int, int)
        size of output images
    fps: int
        how many second to get one frame
        if None: get all frame of video
    min_distant: int ~ [0, 64]
        minimum distant of average hash of frame (http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html)
    num_worker: int
        number of worker
    verbose: bool
        True: progress bar
        False: silent

    Returns
    -------
    None
    """
    video = imageio.get_reader(video_path, format='ffmpeg', size=size, fps=fps)
    frames = [Image.fromarray(video.get_data(i)) for i in range(len(video))]
    hashes = pool_worker(imagehash.average_hash, frames, num_worker, verbose)
    distinct_indexs = __extract_distinct_hash_indexes(hashes, min_distant)
    
    for index in distinct_indexs:
        Image.fromarray(video.get_data(index)).save(os.path.join(dest_dir, '{:05}.png'.format(index)))

def extract_distinct_image(paths, min_distant=2, num_worker=None, verbose=True):
    """Extract distinct image

    Parameters
    ----------
    paths : str
        path of images
    min_distant: int ~ [0, 64]
        minimum distant of average hash of frame (http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html)
    num_worker: int
        number of worker
    verbose: bool
        True: progress bar
        False: silent

    Returns
    -------
    list of paths of distinct image
    """
    hashes = pool_worker(__get_average_hash, paths, num_worker, verbose)
    distinct_indexs = __extract_distinct_hash_indexes(hashes, min_distant)
    return [paths[i] for i in distinct_indexs]