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
        self.create_manifest_and_index(*args, **kwargs)
        self.create_task(*args, **kwargs)
        self.create_annotations(*args, **kwargs)
        self.create_backup(*args, **kwargs)

    @staticmethod
    def create_annotations(root=BackupRoot) -> None:
        with open('script_created_annotations.json', 'w') as outfile:
            json.dump([root.dict()], outfile)

    def create_manifest_and_index(self, valid_ims: list) -> None:

        lines = [
            {"version": "1.1"},
            {"type": "images"}
        ]

        # structure of index.json in cvat: https://github.com/cvat-ai/cvat/issues/7157#issuecomment-1820549030
        frame_cnt = 0
        index = 36
        index_dict = {frame_cnt: index}

        for f in valid_ims:
            # get name without file extension (jpg, png)
            # so strange way because there may be '.' in fnames
            name, ext = '.'.join(f.split('.')[:-1]), f.split('.')[-1]
            h, w, _ = cv2.imread(os.path.join(self.input_dir, f)).shape
            lines.append({
                "name": name,
                "extension": ext,
                "width": w,
                "height": h,
                "meta": {"related_images": []}
            })
            frame_cnt += 1
            index_dict[frame_cnt] = index + len(str(lines[-1]))

        with open('script_created_manifest.jsonl', 'w') as outfile:
            for entry in lines:
                json.dump(entry, outfile)
                outfile.write('\n')

        with open('script_created_index.json', 'w') as fp:
            fp.write(json.dumps(index_dict))

    def create_task(self, backup_name: str, image_quality: int, number_of_images: int) -> None:

        task_dict = {
            "name": backup_name,
            "labels": [],

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
        shutil.move('script_created_index.json', os.path.join('script_created_backup/data', 'index.json'))
        shutil.move('script_created_task.json', os.path.join('script_created_backup', 'task.json'))
        shutil.move('script_created_annotations.json', os.path.join('script_created_backup', 'annotations.json'))

        for f in valid_ims:
            shutil.copy(os.path.join(self.input_dir, f), os.path.join('script_created_backup/data', f))

        def add_directory_to_zip(zip_file_path, directory_path):
            with zipfile.ZipFile(zip_file_path, 'a', compression=zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        zipf.write(file, os.path.relpath(os.path.join(directory_path, file),
                                                         os.path.dirname(directory_path)))
            zipf.close()

        zip_file_path = '../script_created_backup.zip'
        add_directory_to_zip(zip_file_path, 'script_created_backup')

        shutil.rmtree('script_created_backup')

    @abstractmethod
    def check_dataset_consistency(self, input_dir: str) -> [tuple[list, list]]:
        pass

    @abstractmethod
    def convert_markdown(self, valid_ims: list, valid_labels: list) -> BackupRoot:
        pass


