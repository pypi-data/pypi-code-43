class TrackerInfo:
  def __init__(self, ip='11.163.182.45', port=20093):
    self.ip = ip
    self.port = port
  def asStr(self):
    return self.ip + ':' + str(self.port)
  def asTuple(self):
    return (self.ip, self.port)

class RpcInfo:
  def __init__(self, key, path):
    self.key = key
    self.path = path

class ThreadMod:
  def __init__(self, type, num):
    self.type = type
    self.num = num
  def asTuple(self):
    return (self.type, self.num)

class TargetProvider:
  def __init__(self, key, core_type=1, core_num=1):
    self.tracker = TrackerInfo()
    self.core    = ThreadMod(core_type, core_num)
    self.target   = 'llvm'
    self.host     = 'llvm'
    self._get_target(key)

  def _get_target(self, key):
    alios_bin_dir = '/home/wzh/alios/prebuilts/gcc/linux-x86'
    arm_target = 'llvm -device=arm_cpu -mattr=+neon'
    a53_target = arm_target + ' -mcpu=cortex-a53'
    a53_aarch64_target = a53_target + ' -target=aarch64-none-linux-gnueabi'
    a53_arm32_target = a53_target + ' -target=armv7a-none-linux-gnueabihf'

    if key == 'imx6':
      self.target = arm_target + ' -target=armv7l-none-linux-gnueabihf -mcpu=cortex-a9'
      self.host = self.target
      self.rpc = RpcInfo(key, '/data/wzh/rpc.tvm/arm32/')
      os.environ['TVM_NDK_CC'] = alios_bin_dir + '/arm/arm-linux-gnueabihf-4.9-glibc-2.21/bin/arm-linux-gnueabihf-g++'
    elif key == 'imx8':
      self.target = a53_aarch64_target
      self.host = self.target
      self.rpc = RpcInfo(key, '/data/wzh/rpc.tvm/alios/')
      os.environ['TVM_NDK_CC'] = alios_bin_dir + '/aarch64/aarch64-linux-gnueabi-4.9-glibc-2.20/bin/aarch64-linux-gnueabi-g++'
    elif key in ['rasp0', 'dmlc']:
      self.target = a53_aarch64_target
      self.host = self.target
      self.rpc = RpcInfo(key, '/home/wzh/rpc.tvm/aarch64/')
      os.environ['TVM_NDK_CC'] = 'aarch64-linux-gnu-g++'
    elif key == 'rasp0.arm32':
      self.target = a53_arm32_target
      self.host = self.target
      self.rpc = RpcInfo(key, '/home/wzh/rpc.tvm/arm32/')
      os.environ['TVM_NDK_CC'] = 'arm-linux-gnueabihf-g++'
    elif key == 'rasp.pool':
      self.target = a53_aarch64_target
      self.host = self.target
      self.rpc = RpcInfo(key, '/home/ubuntu/rpc.tvm/pool/')
      os.environ['TVM_NDK_CC'] = 'aarch64-linux-gnu-g++'
    elif key == 'llvm':
      self.target = key
      self.host = self.target
      self.rpc = RpcInfo(key, None)
    else:
      raise ValueError("Unknow target name %s", key)

class TvmDeployables:
  graph = None # 
  lib = None
  params = None
  path_so
  def build(self, target, model, net, params, opt_level=3):
    logging.info("Compiling...")
    if IsUpstream:
      with relay.build_config(opt_level=opt_level):
        self.graph, self.lib, self.params = relay.build(
            net, target=target.target, target_host=target.host, params=params)
    else:
      with nnvm.compiler.build_config(opt_level=opt_level):
        self.graph, self.lib, self.params = nnvm.compiler.build(
              net, target=target.target, target_host=target.host,
              shape=model.dict('input', 'shape'),
              dtype=model.dict('input', 'dtype'), params=params)

  def export(self, target, export_path=None):
    if export_path is None:
      export_path = os.path.join(target.rpc.key, 'deploy')
    logging.info("Exporting deployables to %s..." % export_path)

    if not os.path.exists(export_path): os.makedirs(export_path)

    self.path_so = os.path.join(export_path, 'deploy_lib.so')
    if target.rpc.path:
      from tvm.contrib import ndk
      self.lib.export_library(self.path_so, ndk.create_shared)
    else: self.lib.export_library(self.path_so)
    # self.lib.save(os.path.join(export_path, 'lib.ll'), 'll')
    # self.lib.save(os.path.join(export_path, 'lib.asm'), 'asm')
    # self.lib.save(os.path.join(export_path, 'lib.o'), 'o')

    if not IsUpstream:
      path_json = os.path.join(export_path, 'deploy_graph.json')
      with open(path_json, 'w') as fo:
        fo.write(self.graph.json())

    path_params = os.path.join(export_path, 'deploy_param.params')
    with open(path_params, 'wb') as fo:
      fo.write(nnvm.compiler.save_param_dict(self.params))

class TvmRuntimeWrapper:
  def __init__(self, model, target, deployables):
    if target.rpc.path:
        # upload module to device
        logging.info("Upload...")
        if IsUpstream:
            remote = autotvm.measure.request_remote(target.rpc.key, target.tracker.ip, target.tracker.port, timeout=1000)
        else:
            remote = autotvm.measure.request_remote(target.rpc.key, tracker_addr=target.tracker.asTuple(), timeout=1000)
        remote.upload(deployables.path_so, target=target.rpc.path + 'mylib.so')
        logging.info("Load library...")
        rlib = remote.load_module(target.rpc.path + 'mylib.so')

        my_config_threadpool = remote.get_function('runtime.config_threadpool')
        my_config_threadpool(target.core.type, target.core.num)
        rparams = {k: tvm.nd.array(v, remote.context(str(target.target), 0)) \
                    for k, v in deployables.params.items()}
        # upload parameters to device
        ctx = remote.context(str(target.target), 0)
        module = runtime.create(deployables.graph, rlib, ctx)
        for i in range(0, len(model.inputs)):
            module.set_input(model.inputs[i].name,
                             tvm.nd.array(model.inputs[i].ndarray))
        module.set_input(**rparams)
    else:
        ctx = tvm.context(str(target.target), 0)
        rlib = tvm.module.load(deployables.path_so)
        module = runtime.create(deployables.graph, rlib, ctx)
        for i in range(0, len(model.inputs)):
            module.set_input(model.inputs[i].name,
                             tvm.nd.array(model.inputs[i].ndarray))
        module.set_input(**deployables.params)
    self.module = module
    self.ctx = ctx

  def run(self, model, useLayout, dumpOutput=False):
    logging.info("Running TVM...")
    self.module.run()
    for i in range(len(model.outputs)):
      model.outputs[i].ndarray = self.module.get_output(i,
              tvm.nd.empty(model.outputs[i].shapeAs(useLayout),
                           model.outputs[i].dtype, ctx=self.ctx)).asnumpy()
    if dumpOutput:
      model.store('output')

  def profile(self, target, times=50):
    logging.info("Evaluate inference time cost...")
    ftimer = self.module.module.time_evaluator('run', self.ctx, number=times)
    prof_res = np.array(ftimer().results) * 1000 # convert to millisecond
    logging.info("Mean inference time (std dev): %.2f ms (%.2f ms)" %
                 (np.mean(prof_res), np.std(prof_res)))

    if not IsUpstream:
      if target.rpc.path:
        profile_path = target.rpc.path + 'profile.' + '.log'
        self.module.run_profile(False, 1, times, custom_filename=profile_path)
      else:
        self.module.run_profile(False, 1, times)

