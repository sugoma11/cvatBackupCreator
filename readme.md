# CVAT Backup creator

---

This simple quick-and-dirty python code allows to create CVAT-zip (*2.3.0*) backups from other
dataset formats. It's very useful when you want to edit markdown but your dataset can't be loaded in CVAT directly.  
Possible dataset formats are:
- RGB segmentation masks
- YoloV8 Bbox or segmentation mask  
  (These formats may be uploaded in CVAT 2.3.0, but you must have some CVAT metafiles which may absent)

## Usage:
```python3 main.py <config.yaml>```

---
### Code structure:

There is a base class which performs creating metadata and annotation jsons and compressing all data in CVAT-backup zip in
the core dir. Only the ```check_dataset_consistency``` and ```convert_markdown``` methods are abstract.  
Also there are inheritors-converters in the core dir.

---
There are a specific data-input format and a converter object for every dataset format. So,
### RGB segmentations masks
Create an "rgb_masks" (the dir name can be changed in config.yaml) directory with "images" and "masks" subdirs with images and labels respectively. Masks and images should have the same names. See
```check_dataset_consistency``` method of converter. Don't forget to set class-color mapping in the config.yaml.
```
├── rgb_masks
│   ├── images
│   │   └── 1.jpg
│   └── masks
│       └── 1.jpg

```
### YoloV8TxtBbox or YoloV8TxtSegm
The same structure as for RGB segmentations masks, but there are txt files instead of masks in the "labels" dir. Txt-files and images should have the same names. See
```check_dataset_consistency``` method of converter.
```
├── yolotxt
│   ├── images
│   │   └── 1.jpg
│   └── labels
│       └── 1.txt

```