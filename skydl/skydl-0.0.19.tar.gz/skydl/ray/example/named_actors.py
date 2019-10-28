import traceback

import ray
from ray.experimental import named_actors, signal
from skydl.ray.experimental import revised_named_actors
from skydl.ray.experimental.ray_ring_buffer import RayRingBuffer

if __name__ == '__main__':
    try:
        ray.init()
        ###########################
        # #on the driver
        @ray.remote
        class Counter1:
            def __init__(self):
                print("global_queue init...")
                self.count = 0
                self.ringbuffer = RayRingBuffer(10)
                for i in range(20):
                    self.inc(1)

            def inc(self, n):
                self.count += n
                self.ringbuffer.put(self.count)

            def get(self):
                return self.ringbuffer.get()

        try:
            counter1 = named_actors.get_actor("global_queue2")
            print("counter1=", counter1)
        except Exception as e:
            print("error occurred while get counter1!!!, %s", str(e))

        global_object_id = Counter1.remote()
        try:
            revised_named_actors.register_actor_with_overwrite("global_queue2", global_object_id)
        except Exception as e:
            print("error occured at named_actors.register_actor!!!, %s", str(e))
            # https://github.com/ray-project/ray/blob/57d6e983022ad86559b07f6a863404198ebf2347/doc/source/fault-tolerance.rst
            result_list = signal.receive([global_object_id], timeout=5)
            # Expected signal is 'ErrorSignal'.
            if type(result_list[0][1]) == signal.ErrorSignal:
                print(result_list[0][1].get_error())
        try:
            counter2 = named_actors.get_actor("global_queue2")
            ray.get(counter2.inc.remote(1))
            print("counter2.get()=", ray.get(counter2.get.remote()))
        except Exception as e:
            print("error occurred while get counter1!!!, %s", str(e))
    except:
        print("ray error occured at ray.init()...")
        traceback.print_exc()
