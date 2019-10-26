import time
from pihat_widget import image


class TrafficLight(image.ImageLoader):


    def set_state(self, state):
        """
        Set the state using a binary string
        :param state: binary string controlling red, amber green. 100 = (red(on) amber(off) green(off))
        :return: Exception on red, green and green amber
        """
        if state == "100":
            status = "red"
        elif state == "110":
            status ="redamber"
        elif state == "010":
            status = "amber"
        elif state == "001":
            status = "green"
        else:
            raise ValueError(f"Invalid Light State {state}")
        s = int(state, 2)
        self.q.put(("load",status))

if __name__ == "__main__":

    lg = TrafficLight()
    count =0
    while count<1:
        lg.set_state("100")

        time.sleep(5)
        lg.set_state("110")
        time.sleep(2.7)
        lg.set_state("001")
        time.sleep(5)
        lg.set_state("010")
        time.sleep(2.7)
        count+=1
    lg.close()