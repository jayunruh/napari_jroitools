# napari_jroitools 0.0.12
These files are intended to provide Napari plugins to read and write ImageJ (and Fiji) roi and multi-roi (.zip) files.  The importroi.py and exportroi.py files represent python implementations of the ImageJ RoiDecoder and RoiEncoder files.  The importroi.py file contains the Roi class which is used to hold Roi data.  The napari_jroireader.py and napari_jroiwriter.py files contain the Napari plugin hooks.  

The imgprofiler.py file contains tools for creating kymographs from thick line profiles.  There is a version for sparse bead data where the underlying image is a set of 2D bead coordinates rather than a dense 2D image.