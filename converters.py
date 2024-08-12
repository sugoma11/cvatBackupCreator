import os
import cv2
import logging
from base_converter import BaseConverter
from pydantic_classes import BackupRoot, Polygon, Rectangle


class YoloV8BboxTxtConverter(BaseConverter):

    def __init__(self, input_dir: str, class_map: dict, image_quality: int, task_name: str):
        self.input_dir = input_dir
        self.class_map = class_map
        self.image_quality = image_quality
        self.task_name = task_name

    def check_dataset_consistency(self, input_dir: str) -> [tuple[tuple, tuple]]:

        txt_and_image_dict = {}
        image_fnames = set()

        for f in os.listdir(input_dir):

            if f.endswith('txt'):

                if f.replace('txt', 'png') in image_fnames:
                    logging.warning(f'{f.replace("txt", "png")} is duplicated')
                    continue

                if f.replace('txt', 'jpg') in image_fnames:
                    logging.warning(f'{f.replace("txt", "jpg")} is duplicated')
                    continue

                elif os.path.isfile(os.path.join(self.input_dir, f.replace('txt', 'png'))):
                    txt_and_image_dict[f] = f.replace('txt', 'png')
                    image_fnames.add(f.replace('txt', 'png'))

                elif os.path.isfile(os.path.join(self.input_dir, f.replace('txt', 'jpg'))):
                    txt_and_image_dict[f] = f.replace('txt', 'jpg')
                    image_fnames.add(f.replace('txt', 'jpg'))
                else:
                    logging.warning(f'There is no im for {f}!')

        for fname in (im_name for im_name in os.listdir() if im_name.endswith('png') or im_name.endswith('jpg')):
            if fname not in image_fnames:
                logging.warning(f'There is no txt for {fname}!')

        return list(txt_and_image_dict.keys()), list(txt_and_image_dict.values())

    def convert_markdown(self, valid_labels: list, valid_ims: list) -> BackupRoot:

        valid_ims.sort()
        valid_labels.sort()
        list_of_objects_to_dump = []

        for i in range(len(valid_ims)):

            im = cv2.imread(valid_ims[i])

            if im is None:
                print(f'ERROR at {valid_ims[i]}.png')
                continue

            h, w, _ = im.shape

            with open(valid_labels[i]) as inf:

                for line in inf:
                    cls, x_c, y_c, w_c, h_c = map(float, line.strip().split(' '))

                    w_c = int(w_c * w)
                    h_c = int(h_c * h)
                    x_c = int(x_c * w)
                    y_c = int(y_c * h)

                    x_tl = x_c - w_c // 2
                    y_tl = y_c - h_c // 2
                    x_br = x_c + w_c // 2
                    y_br = y_c + h_c // 2

                    bbox = Rectangle(frame=i, points=[x_tl, y_tl, x_br, y_br], label=self.class_map[cls])

                    list_of_objects_to_dump.append(bbox.dict())

        root = BackupRoot(shapes=list_of_objects_to_dump)
        return root
    
    def run(self, *args, **kwargs) -> None:
        valid_txt, valid_ims = self.check_dataset_consistency(self.input_dir)
        root = self.convert_markdown(valid_txt, valid_ims)
        self.create_manifest_and_index(valid_ims)
        self.create_task(self.task_name, self.image_quality, len(valid_txt))
        self.create_annotations(root)
        self.create_backup(valid_ims)
