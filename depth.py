import aditofpython as tof
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import struct
import cv2 as cv

def help():
    print(f"{sys.argv[0]} usage:")
    print(f"USB: {sys.argv[0]} <mode number>")
    print(f"Network connection: {sys.argv[0]} <mode number> <ip>")
    print()
    print("For example:")
    print(f"python {sys.argv[0]} 0 10.43.0.1")
    exit(1)

## do this 
if len(sys.argv) < 2 or len(sys.argv) > 3 or sys.argv[1] == "--help" or sys.argv[1] == "-h" :
    help()
    exit(-1)

system = tof.System()

#print("SDK version: ", tof.getApiVersion(), " | branch: ", tof.getBranchVersion(), " | commit: ", tof.getCommitVersion())

mode = 0
cameras = []
ip = ""
if len(sys.argv) == 3:
    mode = sys.argv[1]
    ip = sys.argv[2]
    #print (f"Looking for camera on network @ {ip}.")
    ip = "ip:" + ip
elif len(sys.argv) == 2:
    mode = sys.argv[1]
    #print (f"Looking for camera on UVC.")
else :
    #print("Too many arguments provided!")
    exit(-2)

status = system.getCameraList(cameras, ip)
#print("system.getCameraList()", status)

camera1 = cameras[0]
#create callback and register it to the interrupt routine
def callbackFunction(callbackStatus):
    print("Running the python callback for which the status of ADSD3500 has been forwarded. ADSD3500 status = ", callbackStatus)

sensor = camera1.getSensor()
status = sensor.adsd3500_register_interrupt_callback(callbackFunction)

status = camera1.initialize()
#print("camera1.initialize()", status)

modes = []
status = camera1.getAvailableModes(modes)
#print("camera1.getAvailableModes()", status)
#print(modes)

if int(mode) not in modes:
    print(f"Error: Unknown mode - {mode}")
    exit(-3)

camDetails = tof.CameraDetails()
status = camera1.getDetails(camDetails)
#print("camera1.getDetails()", status)
#print("camera1 details:", "id:", camDetails.cameraId, "connection:", camDetails.connection)

status = camera1.setMode(int(mode))
#print("camera1.setMode(",mode,")", status)


   
num = 0


while True:
    
    # Example of getting/modifying/setting the current ADSD3500 parameters
    # status, currentFrameProcessParams = camera1.getFrameProcessParams()
    # currentFrameProcessParams["ab_thresh_min"] = "4"
    # camera1.setFrameProcessParams(currentFrameProcessParams)

    # Example of configuring the Dynamic Mode Switching
    # The expected sequence of frame is: mode2, mode2, mode2, mode3, mode2, ...
    # camera1.adsd3500setEnableDynamicModeSwitching(True)
    # camera1.adsds3500setDynamicModeSwitchingSequence([(2, 3), (3, 1)])

    status = camera1.start()
    #print("camera1.start()", status)

    frame = tof.Frame()
    status = camera1.requestFrame(frame)
    #print("camera1.requestFrame()", status)

    frameDataDetails = tof.FrameDataDetails()
    status = frame.getDataDetails("depth", frameDataDetails)
    #print("frame.getDataDetails()", status)
    #print("depth frame details:", "width:", frameDataDetails.width, "height:", frameDataDetails.height, "type:", frameDataDetails.type)

    status = camera1.stop()
    #print("camera1.stop()", status)







    # Get the depth frame
    image_depth = np.array(frame.getData("depth"), copy=False)
    # Get the AB frame
    image_ab = np.array(frame.getData("ab"), copy=False)
    # Get the confidence frame
    image_conf = np.array(frame.getData("conf"), copy=False)


    ## accessing the depth data here:
    print()
    print("LOOK HERE!!!!")
    print(image_depth)
    print()




























    ###################################################################################################################################################
    
    
    # Ensure output folder exists
    output_folder = os.path.join(os.getcwd(), "images")
    os.makedirs(output_folder, exist_ok=True)

    # Normalize the depth image to 0-255 for visualization
    depth_min = np.min(image_ab)
    depth_max = np.max(image_ab)
    depth_normalized = (255 * (image_ab - depth_min) / (depth_max - depth_min)).astype(np.uint8)

    # Save normalized depth image
    cv.imwrite(os.path.join(output_folder, f'depth_norm_{num}.png'), depth_normalized)

    # Save raw depth image as 16-bit PNG (will be clamped if out of range)
    cv.imwrite(os.path.join(output_folder, f'depth_raw_{num}.png'), image_ab)

    # Save raw data as .npy for full precision
    np.save(os.path.join(output_folder, f'depth_raw_{num}.npy'), image_ab)

    # ----------------------------------------------------------------
    # Annotations

    # Define cluster centers
    cluster1_center = (50, 50)  # near side
    cluster2_center = (frameDataDetails.width // 2, frameDataDetails.height // 2)  # center (implant area)
    cluster_size = 50  # pixels radius for rectangle

    # Create a copy to draw annotations (don't draw on original)
    depth_with_annotations = depth_normalized.copy()

    # Draw rectangles around cluster centers
    cv.rectangle(depth_with_annotations,
                (cluster1_center[0] - cluster_size, cluster1_center[1] - cluster_size),
                (cluster1_center[0] + cluster_size, cluster1_center[1] + cluster_size),
                color=200, thickness=2)

    cv.rectangle(depth_with_annotations,
                (cluster2_center[0] - cluster_size, cluster2_center[1] - cluster_size),
                (cluster2_center[0] + cluster_size, cluster2_center[1] + cluster_size),
                color=200, thickness=2)

    # Display and save annotated image
    #cv.imshow("Depth Image with Clusters", depth_with_annotations)
    cv.imwrite(os.path.join(output_folder, f'depth_annotated_{num}.png'), depth_with_annotations)
        

    #getting the actual data (where image_depth = is the image)

    height, width = image_depth.shape
    top_left_region = image_depth[0:100, 0:100] 


    # Compute the starting row and column for the center region
    start_row = (height - 100) // 2
    start_col = (width - 100) // 2

    middle = image_depth[start_row:start_row+100, start_col:start_col+100]

    # Mean of the top-left 100x100 region
    top_left_mean = np.mean(top_left_region)

    # Mean of the center 100x100 region
    middle_mean = np.mean(middle)

    print()
    print()
    
    print(f"Backgeound distance: {top_left_mean}")
    print(f"object distance: {middle_mean}")

    object_thickness = top_left_mean - middle_mean
    print(f"thickness of oject: {object_thickness} millimeters")
    
    
    print()
    print()
    print("CONFIDENCE DATA BELOW!!!!")


    
    
    #getting the actual data (where image_depth = is the image)
    Con_top_left_region = image_conf[0:100, 0:100]
    Con_middle = image_conf[start_row:start_row+100, start_col:start_col+100]
    
    # Mean of the top-left 100x100 region
    Con_top_left_mean = np.mean(top_left_region)
    # Mean of the center 100x100 region
    Con_middle_mean = np.mean(middle)
    
    print(f"Confidence background distance: {Con_top_left_mean}")
    print(f"Confidence object distance: {Con_middle_mean}")

    Con_object_thickness = Con_top_left_mean - Con_middle_mean
    print(f"Confidence thickness of oject: {Con_object_thickness} ")
    
    print()
    print()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    if ((frameDataDetails.width != 1024 and frameDataDetails.height != 1024) or (frameDataDetails.width != 512 and frameDataDetails.height != 640)):
        image_conf2 = image_conf.flatten()
        count = 0
        final_conf = np.zeros(frameDataDetails.width*frameDataDetails.height*4)
        for i in range(frameDataDetails.width*(frameDataDetails.height // 2)):
            packed_float = struct.pack('f', image_conf2[i])

        # Unpack the bytes into four uint8 values
            uint8_values = struct.unpack('2H', packed_float)
            array_data = np.array(uint8_values)
            for j in range(2):
                final_conf[count+j] = array_data[j]
                #print(j)
            count = count + 2
        image_conf = np.reshape(final_conf[frameDataDetails.width*frameDataDetails.height*0:frameDataDetails.width*frameDataDetails.height*1], \
                                [frameDataDetails.height,frameDataDetails.width])

    metadata = tof.Metadata
    status, metadata = frame.getMetadataStruct()

    #Unregister callback
    status = sensor.adsd3500_unregister_interrupt_callback(callbackFunction)

    # Metadata values
    sensor_temp = metadata.sensorTemperature
    laser_temp = metadata.laserTemperature
    frame_num = metadata.frameNumber
    imager_mode = metadata.imagerMode

    #print("Sensor temperature from metadata: ", sensor_temp)
    #print("Laser temperature from metadata: ", laser_temp)
    #print("Frame number from metadata: ", frame_num)
    #print("Mode from metadata: ", imager_mode)

    print()
    print("DONE TAKING PICS")
    print()

    num = num + 1
    output_folder = os.path.join(os.getcwd(), "images")

    # Ensure the folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # cv.imwrite('saved_image_depth' + str(num) + '.jpg', image_depth)
    # cv.imwrite('saved_image_ab' + str(num) + '.jpg', image_ab, params=None)
    # cv.imwrite('saved_image_confidence' + str(num) + '.jpg', image_conf, params=None)

    cv.imwrite(os.path.join(output_folder, 'saved_image_depth' + str(num) + '.jpg'), image_depth)
    cv.imwrite(os.path.join(output_folder, 'saved_image_ab' + str(num) + '.jpg'), image_ab, params=None)
    cv.imwrite(os.path.join(output_folder, 'saved_image_confidence' + str(num) + '.jpg'), image_conf, params=None)


    key = input("want to take another photo? Y/N ")
    if key == 'N':
        break
    else:
        continue

