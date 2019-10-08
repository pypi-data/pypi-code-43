import onnx
from onnx_coreml import convert
from coremltools.proto import NeuralNetwork_pb2

## Load ONNX Model
model = onnx.load('/Volumes/Common/Work/CoreML/converters/onnx-coreml/tests/bn.onnx')

## Convert ONNX Model into CoreML MLModel
c_model = convert(model, disable_coreml_rank5_mapping=True)