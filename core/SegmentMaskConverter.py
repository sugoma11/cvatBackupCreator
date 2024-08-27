import os
import cv2
import numpy as np
import logging

from core.base_converter import BaseConverter
from core.pydantic_classes import BackupRoot, Polygon


class SegmentMaskConverter(BaseConverter):

    def __init__(self, input_dir: str, class_map: dict, image_quality: int, task_name: str):
        self.input_dir = input_dir
        self.class_map = class_map
        self.image_quality = image_quality
        self.task_name = task_name

    @staticmethod
    def check_dataset_consistency(input_dir: str) -> [tuple[tuple, tuple]]:

        masks_dir = os.path.join(input_dir, 'masks')
        images_dir = os.path.join(input_dir, 'images')

        masks_fnanes = {fname for fname in os.listdir(masks_dir)}
        image_fnames = {fname for fname in os.listdir(images_dir)}

        valid = masks_fnanes.intersection(image_fnames)

        for f in masks_fnanes.difference(valid):
            logging.warning(f'There is no image for {os.path.join("masks", f)}!')

        for f in image_fnames.difference(valid):
            logging.warning(f'There is no mask for {os.path.join("images", f)}!')

        return (list(map(lambda x: os.path.join(masks_dir, x), valid)),
                list(map(lambda x: os.path.join(images_dir, x), valid)))

    def convert_markdown(self, valid_labels: list, valid_ims: list) -> BackupRoot:

        valid_ims.sort()
        valid_labels.sort()
        list_of_objects_to_dump = []

        labels_colors = {label: label_dict['color'] for label, label_dict in self.class_map.items()}

        for i in range(len(valid_ims)):

            im = cv2.imread(valid_ims[i])
            mask = cv2.imread(valid_labels[i])

            if im is None:
                logging.warning(f'ERROR at {valid_ims[i]}')
                continue

            if mask is None:
                logging.warning(f'ERROR at {valid_labels[i]}')
                continue

            for label, color in labels_colors.items():
                current_label_mask = np.where(mask == color, 255, 0).astype('uint8')
                current_label_mask = cv2.cvtColor(current_label_mask, cv2.COLOR_BGR2GRAY)

                contours, _ = cv2.findContours(current_label_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for cont in contours:
                    cont = cont.squeeze()
                    cont = cont.reshape(1, -1).squeeze()
                    cont = cont.tolist()
                    poly = Polygon(frame=i, points=cont, label=self.class_map[label]['name'])
                    list_of_objects_to_dump.append(poly.dict())

        root = BackupRoot(shapes=list_of_objects_to_dump)
        return root

    def run(self, *args, **kwargs) -> None:
        valid_labels, valid_images = self.check_dataset_consistency(self.input_dir)
        root = self.convert_markdown(valid_labels, valid_images)
        self.create_manifest_and_index(valid_images)
        self.create_task(self.task_name, self.image_quality, len(valid_labels))
        self.create_annotations(root)
        self.create_backup(valid_images)


if __name__ == '__main__':

    from utils import Config

    cfg = Config('../config.yaml')
    converter = SegmentMaskConverter(**cfg.backup_params)

    converter.run()
