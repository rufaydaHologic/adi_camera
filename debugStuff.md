(ADIcamera-setup) PS C:\Users\RuS0325\OneDrive - Hologic Inc\Desktop\olderPythonAdi_camera> python .\completedBin.py --frame .\binTesting.bin
SDK version:  6.0.1  | branch:  HEAD  | commit:  e748dbfd
frame.getDataDetails() Status.Ok
depth frame details: width: 1024 height: 1024 type: depth
WARNING: Logging before InitGoogleLogging() is written to STDERR
E20250717 14:25:35.734994 24144 frame_impl.cpp:125] conf is not supported by this frame!
W20250717 14:25:35.734994 24144 frame_impl.cpp:107] Could not find any details for type: conf
Traceback (most recent call last):
  File "C:\Users\RuS0325\OneDrive - Hologic Inc\Desktop\olderPythonAdi_camera\completedBin.py", line 55, in <module>
    image_conf = np.array(frame.getData("conf"), copy=False)
RuntimeError: Item size 128 for PEP 3118 buffer format string f does not match the dtype f item size 4.
(ADIcamera-setup) PS C:\Users\RuS0325\OneDrive - Hologic Inc\Desktop\olderPythonAdi_camera> 
