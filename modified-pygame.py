'''
✅ Use a live stream script (pygame or OpenCV window — either works)

✅ Loop through 100 frames

✅ For each frame, extract a fixed center region (e.g. 10x10 or 20x20 pixels)

✅ Compute the mean depth of that region

✅ Store it in a list

✅ After 100 frames, take the average of the list → This is your accurate distance reading

🔄 Repeat if needed (for comparison: breast plate alone vs with implant)
'''


import aditofpython as tof
import numpy as np
import pygame
import sys
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import os
import cv2 

mode = 3

def help():
    print(f"{sys.argv[0]} usage:")
    print(f"USB: {sys.argv[0]} <mode number>")
    print(f"Network connection: {sys.argv[0]} <mode number> <ip>")
    print()
    print("For example:")
    print(f"python {sys.argv[0]} 0 10.43.0.1")
    exit(1)

if len(sys.argv) < 2 or len(sys.argv) > 3 or sys.argv[1] == "--help" or sys.argv[1] == "-h" :
    help()
    exit(-1)

jet_colormap = plt.get_cmap('jet')

system = tof.System()

print("SDK version: ", tof.getApiVersion(), " | branch: ", tof.getBranchVersion(), " | commit: ", tof.getCommitVersion())

cameras = []
ip = ""
if len(sys.argv) == 3:
    mode = sys.argv[1]
    ip = sys.argv[2]
    print (f"Looking for camera on network @ {ip}.")
    ip = "ip:" + ip
elif len(sys.argv) == 2:
    mode = sys.argv[1]
    print (f"Looking for camera on UVC.")
else :
    print("Too many arguments provided!")
    exit(-2)

status = system.getCameraList(cameras, ip)
print("system.getCameraList()", status)

camera1 = cameras[0]

status = camera1.initialize()
print("camera1.initialize()", status)

modes = []
status = camera1.getAvailableModes(modes)
print("camera1.getAvailableModes()", status)
print(modes)

if int(mode) not in modes:
    print(f"Error: Unknown mode - {mode}")
    help()
    exit(-3)

camDetails = tof.CameraDetails()
status = camera1.getDetails(camDetails)
print("camera1.getDetails()", status)
print("camera1 details:", "id:", camDetails.cameraId, "connection:", camDetails.connection)

status = camera1.setMode(int(mode))
print("camera1.setMode()", status)

status = camera1.start()
print("camera1.start()", status)

sensor = camera1.getSensor()
modeDetails = tof.DepthSensorModeDetails()
status = sensor.getModeDetails(int(mode),modeDetails)

################################################################################################################################################################
# Depth values might be large numbers! To turn depth into a visible image, we need to scale it down because image display functions (like OpenCV or Pygame) expect pixel values from 0–255
def normalize(image_scalar, width, height):
    image_scalar_norm = image_scalar / image_scalar.max()

    # Apply the colormap to the scalar image to obtain an RGB image
    image_rgb = jet_colormap(image_scalar_norm)
        
    surface = (image_rgb[:, :, :3] * 255).astype(np.uint8)
    return surface


def animate():
    frame = tof.Frame()
    status = camera1.requestFrame(frame)
    frameDataDetails = tof.FrameDataDetails()
    status = frame.getDataDetails("depth", frameDataDetails)
    image = np.array(frame.getData("depth"), copy=False)

    # Compute the starting row and column for the center region and get the depth:
    height, width = image.shape
    start_row = (height - 100) // 2
    start_col = (width - 100) // 2
    middle = image[start_row:start_row+100, start_col:start_col+100]
    middle_depth_average = np.mean(middle)
    
    image = np.rot90(image)

    return pygame.surfarray.make_surface(normalize(image, frameDataDetails.width, frameDataDetails.height)), middle_depth_average, normalize(image,frameDataDetails.width, frameDataDetails.height) #Converts NumPy image into a format Pygame can show
    
def main():
    pygame.init()
    window_size = (modeDetails.baseResolutionWidth, modeDetails.baseResolutionHeight)
    screen = pygame.display.set_mode(window_size)
    
    done = False
    x = 0
    total_average = 0

    # display the animation
    while x < 100 and not done:
        x += 1
        surface, average_depth, normalizedImage = animate()
        total_average = total_average + average_depth
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True


        screen.blit(surface, (0, 0)) 
        
        # Draw red rectangle overlay in center
        rect_size = 20
        rect_x = (window_size[0] - rect_size) // 2
        rect_y = (window_size[1] - rect_size) // 2
        pygame.draw.rect(screen, (255, 0, 0), (rect_x, rect_y, rect_size, rect_size), 2)
        
        pygame.display.flip()
        pygame.time.delay(20)

    # quit Pygame
    pygame.quit()

    #save the normalized image! if this works then I WANT TO PUT A DISPLAY TO SEE IF IT MATCHESSSS UP
    # surfaceLastImage, middlelastImage, normalizedImage = animate()
    # image_bgr = cv2.cvtColor(normalizedImage, cv2.COLOR_RGB2BGR)
    # image_bgr = np.rot90(image_bgr)
    # cv2.imwrite("last_normalized_depth.png", image_bgr)
    # print("Saved last normalized depth image as last_normalized_depth.png")
    
    #save the normalized image! if this works then I WANT TO PUT A DISPLAY TO SEE IF IT MATCHESSSS UP
    surfaceLastImage, middlelastImage, normalizedImage = animate()
    image_bgr = cv2.cvtColor(normalizedImage, cv2.COLOR_RGB2BGR)
    cv2.rectangle(image_bgr, (rect_x, rect_y), (rect_x + rect_size, rect_y + rect_size), (0, 0, 255), 2)
    cv2.imwrite("last_normalized_depth.png", image_bgr)
    print("Saved last normalized depth image as last_normalized_depth.png")


    middle_average_depth_100 = total_average / 100
    print(f"Average depth of center region over 100 frames: {middle_average_depth_100:.2f} mm")
    status = camera1.stop()
    
main()



#animate():	Gets a new depth frame, normalizes it, converts it to an image
#main():	Sets up a Pygame window, and keeps updating it with new depth data
'''
Streaming live from the ADI ToF camera

Capturing 100 depth frames

Averaging the depth values in the center region

Showing the stream live with Pygame
'''
