from optimeed.core.collection import Collection, Parametric_Collection
from optimeed.core.tools import getPath_workspace, rsetattr, rgetattr
import os
import copy
import queue
from optimeed.core.Multithreaded_action import multithread_compute


class Parametric_parameters:
    def __init__(self, attribute_name, filename_collection, description_collection, attr_values, value_is_adim=False):
        self.attribute_name = attribute_name
        self.filename_collection = filename_collection
        self.description_collection = description_collection
        self.attr_values = attr_values
        self.is_adim = value_is_adim

    def set_attr_value(self, device):
        devices_out = list()
        for attr_value in self.attr_values:
            if self.is_adim:
                attr_value *= rgetattr(device, self.attribute_name)
            # set Devices options
            theDevice = copy.deepcopy(device)
            rsetattr(theDevice, self.attribute_name, attr_value)
            devices_out.append(theDevice)
        return devices_out

    def get_filename(self, curr_index=''):
        if curr_index:
            return self.filename_collection
        return self.filename_collection + '_' + str(curr_index)

    def get_description(self):
        return self.description_collection

    def get_attr_name(self):
        return self.attribute_name


class Reevaluation_parameters:
    def __init__(self, attribute_name, filename_collection, description_collection, attr_value):
        self.attribute_name = attribute_name
        self.filename_collection = filename_collection
        self.description_collection = description_collection
        self.attr_value = attr_value

    def set_attr_value(self, devices):
        devices_out = list()
        for device in devices:
            theDevice = copy.deepcopy(device)
            rsetattr(theDevice, self.attribute_name, self.attr_value)
            devices_out.append(theDevice)
        return devices_out

    def get_filename(self):
        return self.filename_collection

    def get_description(self):
        return self.description_collection


def _get_workspace_folder(saving_foldername):
    curr_index = 1
    workspace_folder = getPath_workspace() + '/' + saving_foldername
    while os.path.isdir(workspace_folder):
        curr_index += 1
        workspace_folder = getPath_workspace() + '/' + saving_foldername + '_' + str(curr_index)
    os.mkdir(workspace_folder)
    return workspace_folder


def reevaluate_population(filename_collection_in, saving_foldername, theCharacterization, theReevaluation_parameters):
    """Create new folder"""
    workspace_folder = _get_workspace_folder(saving_foldername)

    """Instantiates input arguments for analysis"""
    # Collections of devices
    theCollection_devices = Collection.load(filename_collection_in)
    theCollection_devices.autosave = False
    theCollection_characterization = Collection()

    theCollection_out = Collection()
    theCollection_out.theData = []
    theCollection_out.set_filename(workspace_folder + '/' + theReevaluation_parameters.get_filename(), change_filename_if_exists=True)
    theCollection_out.set_info(theReevaluation_parameters.get_description() + '\n' + theCollection_devices.get_info())
    theCollection_out.autosave = True
    theCollection_out.save()

    theCollection_devices.theData = theReevaluation_parameters.set_attr_value(theCollection_devices.get_data())
    theCollection_characterization.theData = [theCharacterization] * len(theCollection_devices)

    # Simulates
    _parametric_analysis(theCollection_devices, theCollection_characterization, theCollection_out, 27, fine_compute=True)
    theCollection_out.autosave = False
    theCollection_out.save()
    print("Over")


def launch_parametric_analysis(filename_collection_in, saving_foldername, theCharacterization, theParametric_parameters, device_transformation=None):
    # Get folderName
    workspace_folder = _get_workspace_folder(saving_foldername)

    """Instantiates input arguments for analysis"""
    # Collections of devices
    theCollection_devices = Collection.load(filename_collection_in)
    theCollection_devices.autosave = False

    # Collections of characterization
    theCollection_characterization = Collection()

    # Collections out:
    theCollection_out = Parametric_Collection()

    for index, device in enumerate(theCollection_devices.get_data()):
        # Set collection device
        theCollection_devices.theData = theParametric_parameters.set_attr_value(device)
        if device_transformation is not None:
            for device_to_transform in theCollection_devices.theData:
                device_transformation(device_to_transform, device)
        theCollection_characterization.theData = [theCharacterization] * len(theCollection_devices)

        # Set collection out
        theCollection_out.theData = []
        theCollection_out.set_filename(workspace_folder + '/' + theParametric_parameters.get_filename(index), change_filename_if_exists=True)
        theCollection_out.set_info(theParametric_parameters.get_description() + '\n' + theCollection_devices.get_info())
        theCollection_out.set_reference(device)
        theCollection_out.set_analysed_attribute(theParametric_parameters.get_attr_name())
        theCollection_out.autosave = True

        # Simulates
        _parametric_analysis(theCollection_devices, theCollection_characterization, theCollection_out, 28, fine_compute=True)
        theCollection_out.autosave = False
        theCollection_out.save()

        print("Progression: " + str(index/len(theCollection_devices))*100 + " %")
    print("Over")


def _evaluate_gmsh(queue_parameters_to_evaluate, queue_out, _lock):
    while not queue_parameters_to_evaluate.empty():  # While there are still parameters to evaluate
        try:
            theParameters = queue_parameters_to_evaluate.get(block=False)
            theDevice = theParameters[0]
            theCharacterization = theParameters[1]
            fine_compute = theParameters[2]
            if fine_compute:
                theCharacterization.fine_compute(theDevice)
            else:
                theCharacterization.compute(theDevice)
            queue_out.put(theDevice)
        except queue.Empty:
            print("Queue Empty 1")
    print("Queue empty 2")
    return


def _parametric_analysis(collection_devices_in, collection_characterization_in, collection_devices_out, number_of_cores, fine_compute=False):
    """
    Launch a multithreaded evaluation of each item in the list "parameters_to_evaluate"
    :param collection_devices_in: collection of devices that will be evaluated
    :param collection_devices_out: real-time output collection with element added with simulation
    :param collection_characterization_in: collection of characterization that will evaluate the devices
    :param number_of_cores: number of cores to use simultaneously
    :param fine_compute: use fine_compute instead of compute in characterization
    :return: a collection containing the results devices (same as collection_devices_out)
    """
    data_devices = collection_devices_in.get_data()
    data_characs = collection_characterization_in.get_data()
    outputs = multithread_compute([(data_devices[i], data_characs[i], fine_compute) for i in range(len(data_devices))], _evaluate_gmsh, collection_out=collection_devices_out, numberOfCores=number_of_cores)

    return outputs
