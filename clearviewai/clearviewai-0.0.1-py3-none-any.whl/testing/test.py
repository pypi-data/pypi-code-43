import clearviewai.architectures.min_vgg as mnvgg
from clearviewai.utils.utils import net_architecture
model = mnvgg.MiniVGGNet.build(64, 64, 3, 17)

net_architecture(model,out_dir='./', filename='net.png')
