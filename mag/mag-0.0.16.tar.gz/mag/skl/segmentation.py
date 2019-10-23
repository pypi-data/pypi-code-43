import os, copy, math
import numpy as np

from multiprocessing import Pool
from numpy import mean, subtract
from scipy.spatial.distance import euclidean

from mag.np.arr import runs, binarize, nonzero_1d, consecutive, smooth_runs
from .iou import iou_1d
from .alignment import align_channel_objects
from .mask_accuracy import mask_accuracy

'''-----------------------------------------------------------------------------

EXAMPLE'S CHANNEL LEVEL FUNCTIONS

-----------------------------------------------------------------------------'''
def detect_channel_binary_objects(
    channel:list,
    mask_threshold:float=0.5,
    gap_threshold:int=0,
    length_threshold:int=1

):
    ''' Finds the boundaries of objects in a channel.

    Notes:
        - The the process for detection an object follows:
            1. binarize the channel at `mask_threshold`
            2. determine runs of consecutive "hits".
            3. merge runs within `gap_threshold`.

    Args:
        channel (list): a list of floats

        mask_threshold (float): a float in `[0, 1]` determining which values in
            channel should be transformed to `1` and those which should be `0`.
            By default 0.5.

        gap_threshold (int): an int in `[0, inf)` determing how far two objects
            can be and still be considered the same. By default 1.

        length_threshold (int): the minimum length an object must be to considered
            valid. By default 1.

    Returns:
        objects (list): a list of objects, [obj1, obj2,...], where each object
            is itself a list [start, stop] indicating the indices in channel
            at which the object starts and stops.

    '''
    # ensure numpy array and apply binary mask
    channel = binarize(np.array(channel), mask_threshold)
    # get indices of signal
    signal_indicies = nonzero_1d(channel)
    # handle channel with no signal
    if signal_indicies.size == 0: return []
    # get the runs of signal from our channel
    segments = runs(signal_indicies)
    # apply gap smoothing
    smoothed = smooth_runs(segments, gap_threshold)
    # run with stop-start=0 has len 1
    len_filter = lambda run: len(run) > 0 and run[1]-run[0] >= length_threshold-1
    return list(filter(len_filter, smoothed))




'''-----------------------------------------------------------------------------

EXAMPLE'S LEVEL FUNCTIONS

-----------------------------------------------------------------------------'''
def detect_sequence_binary_objects(
    channel_matrix,
    mask_threshold:float=0.5,
    gap_threshold:int=0,
    length_threshold:int=1
):
    ''' Finds the boundaries of objects for all channels in a matrix following a binary masking.

    Args:
        channel_matrix (list): a list of list of floats. Each sub-list represents
            a channel.

        mask_threshold (float): a float in `[0, 1]` determining which values in
            channel should be transformed to `1` and those which should be `0`.
            By default 0.5.

        gap_threshold (int): an int in `[0, inf)` determing how far two objects
            can be and still be considered the same. By default 1.

        length_threshold (int): the minimum length an object must be to considered
            valid. By default 1.

    Returns:
        objects (list): a list of list of objects, [[obj1, obj2,...], [...],...]
            where each sub-list corresponds to the list of objects for that
            channel where each object is itself a list [start, stop] indicating
            the indices in channel at which the object starts and stops.

    '''
    channel_matrix = binarize(np.array(channel_matrix), mask_threshold)
    return [
        detect_channel_binary_objects(
            channel, mask_threshold, gap_threshold, length_threshold
        ) for channel in channel_matrix
    ]



def evaluate_segmentation(
    output_channel_matrix,
    target_channel_matrix,
    mask_threshold:float=0.5,
    gap_threshold:int=0,
    length_threshold:int=1,
    alignment_scoring_fn=iou_1d,
    tie_breaking_fn=euclidean,
    alignment_scoring_optimal=min,
    tie_breaking_optimal=min
):
    metrics = {
        'perfect_absences': 0,
        'false_negatives': 0,
        'false_positives': 0,
        'perfect_coverages': 0,
        'aligned': [],
        'offsets': [],
        'ious': [],
        'average_iou': float('nan'),
        'average_offset': [float('nan'), float('nan')]
    }

    additive_metrics = [
        'perfect_absences', 'perfect_coverages',
        'false_negatives', 'false_positives',
        'aligned', 'offsets', 'ious'
    ]

    output_channel_matrix = binarize(np.array(output_channel_matrix), mask_threshold)
    target_channel_matrix = binarize(np.array(target_channel_matrix), mask_threshold)

    for channel_index in range(len(target_channel_matrix)):
        # shorter
        channel_str = 'channel_{}_'.format(channel_index)

        # current channel
        output_channel = output_channel_matrix[channel_index]
        target_channel = target_channel_matrix[channel_index]

        # get objects
        output_objects = detect_channel_binary_objects(output_channel, mask_threshold, gap_threshold, length_threshold)
        target_objects = detect_channel_binary_objects(target_channel, mask_threshold, gap_threshold, length_threshold)

        alignment_metrics = align_channel_objects(
            output_objects, target_objects,
            alignment_scoring_fn, tie_breaking_fn,
            alignment_scoring_optimal, tie_breaking_optimal
        )

        for k, v in alignment_metrics.items():
            # store channel wise metrics
            metrics[channel_str+k] = v
            # aggregate metrics of interest
            if k in additive_metrics:
                if type(v) is not list and math.isnan(v): continue
                metrics[k] += v

    if len(metrics['offsets']):
        metrics['average_offset'] = [mean(errors) for errors in zip(*metrics['offsets'])]
    if len(metrics['ious']):
        metrics['average_iou'] = mean(metrics['ious'])

    return metrics


def evaluate_batched_segmentation(
    batched_output_channel_matrix,
    batched_target_channel_matrix,
    mask_threshold:float=0.5,
    gap_threshold:int=0,
    length_threshold:int=1,
    processes:int=None,
    alignment_scoring_fn=iou_1d,
    tie_breaking_fn=euclidean,
    alignment_scoring_optimal=min,
    tie_breaking_optimal=min,
    data_format='channels_first'
):
    metrics = []
    shape = batched_target_channel_matrix.shape
    num_channels = shape[-1] if data_format == 'channels_last' else shape[1]
    if processes is None: processess = os.cpu_count()
    with Pool(processes=processess) as pool:
        starargs = [
            (
                batched_output_channel_matrix[example_index],
                batched_target_channel_matrix[example_index],
                mask_threshold, gap_threshold, length_threshold,
                alignment_scoring_fn,
                tie_breaking_fn, alignment_scoring_optimal, tie_breaking_optimal
            ) for example_index in range(len(batched_target_channel_matrix))
        ]
        metrics = pool.starmap(evaluate_segmentation, starargs)
    metrics = merge_batched_metrics(metrics, num_channels)
    metrics['accuracy'] = mask_accuracy(
        batched_output_channel_matrix,
        batched_target_channel_matrix,
        mask_threshold
    )
    return metrics



def merge_batched_metrics(mapped_metrics:dict, num_channels:int):
    merged = {
        'perfect_absences': 0,
        'false_negatives': 0,
        'false_positives': 0,
        'perfect_coverages': 0,
        'aligned': [],
        'offsets': [],
        'ious': [],
        'average_iou': float('nan'),
        'average_offset': [float('nan'), float('nan')]
    }

    _additive_metrics = [
        'perfect_absences', 'perfect_coverages',
        'false_negatives', 'false_positives',
    ]
    _list_metrics = [
        'aligned', 'offsets', 'ious'
    ]

    additive_metrics = copy.deepcopy(_additive_metrics)
    list_metrics = copy.deepcopy(_list_metrics)


    for channel_index in range(num_channels):
        channel_str = 'channel_{}_'.format(channel_index)
        for additive_metric in _additive_metrics:
            additive_metrics.append(channel_str+additive_metric)
            merged[channel_str+additive_metric] = 0
        for list_metric in _list_metrics:
            list_metrics.append(channel_str+list_metric)
            merged[channel_str+list_metric] = []

    for metrics in mapped_metrics:
        for k, v in metrics.items():
            if k in additive_metrics or k in list_metrics:
                if type(v) is not list and math.isnan(v): continue
                merged[k] += v

    if len(merged['offsets']):
        merged['average_offset'] = [mean(errors) for errors in zip(*merged['offsets'])]
    if len(merged['ious']):
        merged['average_iou'] = mean(merged['ious'])

    return merged
