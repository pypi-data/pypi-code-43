from data_loading.data_io import Data_IO
from data_loading.interfaces.nifti_io import NIFTI_interface

interface = NIFTI_interface(pattern="case_0000[0]", channels=1, classes=3)
data_path = "/home/mudomini/projects/KITS_challenge2019/kits19/data.original/"
data_io = Data_IO(interface, data_path)
sample_list = data_io.get_indiceslist()

sample = data_io.sample_loader(sample_list[0], load_seg=True)

from miscnn.utils.visualizer import visualize_sample


from processing.subfunctions.resampling import Resampling
new_spacing = (3.22, 1.62, 1.62)
sf = Resampling(new_spacing=new_spacing)
sf.preprocessing(sample, training=True)

visualize_sample(sample.img_data, sample.seg_data, sample.index, "test")


# calculate quotient in spacing between actual and desired -> factor
# multiply factor with current_shape -> new_shape
# run batchgenerators.resize for the image
# or https://scikit-image.org/docs/dev/api/skimage.transform.html#skimage.transform.resize
