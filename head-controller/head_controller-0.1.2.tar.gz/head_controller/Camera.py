import cv2,time
import head_controller.Features as Features
import pandas as pd
import numpy as np
import json
import db
import Model

RESIZE_FACTOR = 0.02

def check_video_frame_data():
    video=cv2.VideoCapture(0)
    check,frame = video.read()
    print(check)
    print(frame)
    video.release()
    return

def check_video_frame_data_predict():

    m = Model.Model()
    print('training...')
    m.build_svc()
    print('done')
    start_time = time.time()

    video=cv2.VideoCapture(0)
    while ( time.time() - start_time ) < 2:
        print('calibrating camera')
        check,frame = video.read()
        # Play stream
        key = cv2.waitKey(1)
        if key== ord('q'):
            break
        continue

    while True:

        check,frame = video.read()
        print(check)
        print(frame)

        orig = frame
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (0,0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
        time_ = time.time()*1000.0
        X = np.array([int(x) for x in gray.ravel()])

        cv2.imshow('Image',orig)
        print('PREDICTION:',m.clf.predict(X.reshape(1, -1)))


        # Play stream - Press w to predict next and q to quit
        key = cv2.waitKey(1)
        if key== ord('q'):
            break
        if key== ord('w'):
            continue
        time.sleep(1)
        cv2.destroyAllWindows
    video.release()

    return

def get_features():

    f = Features.Collector()
    df = f.get_key()
    return df

def capture_review_submit_labels():

    df = get_features()
    print('Length',len(df))
    resp=input('Enter Y to submit')
    if resp.lower() == 'y':
        db.send_df_to_table(df,'training_data_small',operation='append')
    else:
        df.to_csv('Rejected.csv')

    # Recall the training data once saved
    X,y = db.get_training_data()

    # Check cross validation cross on it
    score = db.cross_validation_score_from_data(X,y)
    print('Cross validated with a score of {}'.format(score))
    return
