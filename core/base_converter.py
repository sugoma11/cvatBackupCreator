import os
import cv2
import json
import shutil
import zipfile
from abc import ABC, abstractmethod
from core.pydantic_classes import BackupRoot


class BaseConverter(ABC):

    def run(self, *args, **kwargs) -> None:
        self.check_dataset_consistency(*args, **kwargs)
        self.convert_markdown(*args, **kwargs)
        self.create_manifest(*args, **kwargs)
        self.create_task(*args, **kwargs)
        self.create_annotations(*args, **kwargs)
        self.create_backup(*args, **kwargs)

    @staticmethod
    def create_annotations(root=BackupRoot) -> None:

        with open('script_created_annotations.json', 'w') as fp:
            fp.write(json.dumps([root.model_dump()], indent=2))

    def create_manifest(self, valid_ims: list) -> None:

        valid_ims.sort()

        lines = [
            {"version": "1.1"},
            {"type": "images"}
        ]

        for i, im_fname in enumerate(valid_ims):
            # get name without file extension (jpg, png)
            # so strange way because there may be '.' and in fnames
            name, ext = '.'.join(im_fname.split('.')[:-1]), im_fname.split('.')[-1]
            h, w, _ = cv2.imread(im_fname).shape
            lines.append({
                "name": name.split('/')[-1],
                "extension": '.' + ext,
                "width": w,
                "height": h,
                "meta": {"related_images": []}
            })


        with open('script_created_manifest.jsonl', 'w') as outfile:
            for entry in lines:
                json.dump(entry, outfile, separators=(',', ':'))
                outfile.write('\n')


    def create_task(self, backup_name: str, image_quality: int, number_of_images: int) -> None:

        task_dict = {
            "name": backup_name,

            "labels": [{"name": obj['name'], "color": '#%02x%02x%02x' % tuple(obj['color']), "type": obj['type'],
                        "sublabels": [], "attributes": []} for obj in self.class_map.values()],

            "bug_tracker": "",
            "status": "annotation",
            "subset": "",
            "version": "1.0",
            "data": {
                     "image_quality": image_quality,
                     "start_frame": 0,
                     "stop_frame": number_of_images,

                     "chunk_size": 3,
                     "storage_method": "cache",
                     "storage": "local",
                     "sorting_method": "lexicographical",
                     "chunk_type": "imageset",
                     "deleted_frames": []},

            "jobs": [{"start_frame": 0,
                      "stop_frame": number_of_images,
                      "status": "annotation"}]
        }

        with open('script_created_task.json', 'w') as fp:
            fp.write(json.dumps(task_dict))

    def create_backup(self, valid_ims) -> None:

        if not os.path.isdir('script_created_backup'):
            os.mkdir('script_created_backup')
        else:
            shutil.rmtree('script_created_backup')
            os.mkdir('script_created_backup')

        os.makedirs('script_created_backup/data')
        shutil.move('script_created_manifest.jsonl', os.path.join('script_created_backup/data', 'manifest.jsonl'))
        shutil.move('script_created_task.json', os.path.join('script_created_backup', 'task.json'))
        shutil.move('script_created_annotations.json', os.path.join('script_created_backup', 'annotations.json'))

        for f in valid_ims:
            shutil.copy(f, os.path.join('script_created_backup/data', f.split('/')[-1]))

        def zip_files_and_dir(zip_name, files, directory):
            with zipfile.ZipFile(zip_name, 'w') as zipf:
                # Add files to the zip
                for file in files:
                    zipf.write(file, os.path.basename(file))

                # Add all files from the directory to the zip
                for root, _, filenames in os.walk(directory):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        zipf.write(file_path, os.path.join('data', filename))

        files_to_zip = ['script_created_backup/task.json', 'script_created_backup/annotations.json']
        directory_to_zip = 'script_created_backup/data'
        zip_name = 'self_created_backup.zip'

        zip_files_and_dir(zip_name, files_to_zip, directory_to_zip)

    @staticmethod
    @abstractmethod
    def check_dataset_consistency(input_dir: str) -> [tuple[list, list]]:
        pass

    @abstractmethod
    def convert_markdown(self, valid_ims: list, valid_labels: list) -> BackupRoot:
        pass


