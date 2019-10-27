import head_controller.Camera as Camera
import head_controller.capture_features as capture_features
import head_controller.db as db
import head_controller.Features as Features
import head_controller.init_db as init_db
import head_controller.Model as Model
import head_controller.predict_gesture as predict_gesture
import head_controller.tests as tests


# Setup mysql tables
db.setup_db()
