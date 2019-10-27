# Import the MIScnn module
import miscnn

# Create a Data I/O interface for kidney tumor CT scans in NIfTI format
from miscnn.data_loading.interfaces import NIFTI_interface
interface = NIFTI_interface(pattern="case_000[0-9]*", channels=1, classes=3)

# Initialize data path and create the Data I/O instance
data_path = "/home/mudomini/projects/KITS_challenge2019/kits19/data.original/"
data_io = miscnn.Data_IO(interface, data_path)

# Create a Preprocessor instance to configure how to preprocess the data into batches
pp = miscnn.Preprocessor(data_io, batch_size=4, analysis="patchwise-crop",
                         patch_shape=(128,128,128))

# Create a deep learning neural network model with a standard U-Net architecture
from miscnn.neural_network.architecture.unet.standard import Architecture
unet_standard = Architecture()
model = miscnn.Neural_Network(preprocessor=pp, architecture=unet_standard)



# Training the model with 80 samples for 500 epochs
sample_list = data_io.get_indiceslist()
model.train(sample_list[0:80], epochs=500)

# Predict the segmentation for 20 samples
pred = model.predict(sample_list[80:100], direct_output=True)



from miscnn.evaluation import cross_validation

cross_validation(sample_list, model, k_fold=5, epochs=100,
                 evaluation_path="evaluation_results", draw_figures=True)
