from LabelmeUtils.LabelmePayload import LabelmePayload
import json

TEST_IMAGE = "./test.json"
if __name__ == "__main__":
    with open(TEST_IMAGE) as fp:
        labelme_payload = LabelmePayload.from_json(json.load(fp))

    cropped_img_gen = labelme_payload.cropped_image_generator(10).filter(lambda shape: shape.label == "obj")

    for img in cropped_img_gen:
        img.show()

    cropped_img_gen = labelme_payload.cropped_image_generator(10)

    for img in cropped_img_gen:
        img.show()