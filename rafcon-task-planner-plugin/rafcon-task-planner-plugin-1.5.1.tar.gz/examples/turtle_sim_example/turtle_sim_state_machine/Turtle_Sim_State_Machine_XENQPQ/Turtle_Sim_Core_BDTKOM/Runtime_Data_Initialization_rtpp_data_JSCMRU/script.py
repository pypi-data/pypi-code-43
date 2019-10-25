def execute(self, inputs, outputs, gvm):
    self.logger.info('Updating rtpp_data.')
    rtpp_data = gvm.get_variable('rtpp_data')
    rtpp_data = rtpp_data if rtpp_data else {}
    rtpp_data.update({
  "down_right": {
    "x_pos": 8,
    "y_pos": 3
  },
  "top_right": {
    "x_pos": 8,
    "y_pos": 8
  },
  "alice": {
    "phi": 30,
    "global_storage_id_of_turtle_pos": "turtle_alice",
    "name": "alice"
  },
  "eve": {
    "phi": 30,
    "global_storage_id_of_turtle_pos": "turtle_eve",
    "name": "eve"
  },
  "middle": {
    "x_pos": 5.5,
    "y_pos": 4.5
  },
  "down_left": {
    "x_pos": 3,
    "y_pos": 3
  },
  "top_left": {
    "x_pos": 3,
    "y_pos": 8
  },
  "bob": {
    "phi": 30,
    "global_storage_id_of_turtle_pos": "turtle_bob",
    "name": "bob"
  }
})
    gvm.set_variable('rtpp_data', rtpp_data)
    return "success"