import clearviewai.architectures.min_vgg as mnvgg
from clearviewai.training.train_model import Train


# train network in 3 lines of code
trn = Train("C:/Users/Christopher Dzuwa/Desktop/Flower17-master/dataset/train", nepochs=2)
trn.image_preprocessor(1, 64)
trn.prepare_data()
trn.compile_model(mnvgg.MiniVGGNet.build(64, 64, 3, 17))
trn.train()

# save the model
trn.save_model('./model.h5')

# evaluate model
trn.evaluate_model("./graph.png")
