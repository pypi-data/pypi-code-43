# tensorflow2.0
import tensorflow as tf
from tensorflow.keras import Input,Model, layers, regularizers 
from tensorflow.keras.layers import Dense
import numpy as np

class Encoder(tf.keras.Model):
    def __init__(self, w, h, dim=256):
        super().__init__()
        self.fc1 = Dense(dim, activation='relu', input_shape=(w*h,) )                         
        self.fc2 = Dense(dim/2, activation='relu')
        self.fc3 = Dense(dim/4, activation='relu')
    def call(self,x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x

class Decoder(tf.keras.Model):
    def __init__(self, w, h, dim=256):
        super().__init__()
        Out_dim = w*h

        self.fc1 = Dense(dim/2, activation='relu', input_shape=(dim,) )
        self.fc2 = Dense(dim, activation='relu')
        self.fc3 = Dense(Out_dim, activation='sigmoid')
        
    def call(self,x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x

class AE:
	def __init__(self, dim, w, h):
		self.dim = dim
		self.w, self.h = w, h
	def compile(self):
		input_img = Input(shape=(self.w*self.h),)
		self.encoder = Encoder(self.w,self.h, self.dim)
		self.encoded = self.encoder(input_img)

		self.decoder = Decoder(self.w,self.h, self.dim)
		self.decoded = self.decoder(self.encoded)

		self.autoencoder = Model(input_img, self.decoded)
		self.autoencoder(input_img)
		self.autoencoder.compile(optimizer=tf.keras.optimizers.Adam(), loss='binary_crossentropy')
	def fit(self, x_train,x_test, epochs=10, batch_size=256):
		self.autoencoder.fit(x_train, x_train,
						epochs=epochs,
						batch_size=batch_size,
						shuffle=True,
						validation_data=(x_test, x_test))


if __name__ == "__main__":
	from tensorflow.keras.datasets import mnist
	import matplotlib.pyplot as plt
	(x_train, _), (x_test, _) = mnist.load_data()
	x_train = x_train.astype('float32') / 255.
	x_test = x_test.astype('float32') / 255.
	x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
	x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))
	dim = 256
	w,h = 28,28
	ae = AE(dim, w, h)
	ae.compile()
	ae.fit(x_train, x_test)

	decoded_imgs = ae.autoencoder.predict(x_test)
	n = 10  # how many digits we will display
	plt.figure(figsize=(20, 4))
	for i in range(n):
		# display original
		ax = plt.subplot(2, n, i + 1)
		loc = i + 20
		plt.imshow(x_test[loc].reshape(28, 28))
		plt.gray()
		ax.get_xaxis().set_visible(False)
		ax.get_yaxis().set_visible(False)

		# display reconstruction
		ax = plt.subplot(2, n, i + 1 + n)
		plt.imshow(decoded_imgs[loc].reshape(28, 28))
		plt.gray()
		ax.get_xaxis().set_visible(False)
		ax.get_yaxis().set_visible(False)
	plt.show()