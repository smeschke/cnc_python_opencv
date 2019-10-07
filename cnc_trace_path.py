import cv2
import numpy as np
import cnc_functions

# Read in image
img = 255-cv2.imread('/home/stephen/Desktop/cnc_test/cnc_img_path.png',0)
cutter_size = 250
img = cnc_functions.buffer(img, cutter_size, 1.25)
h,w = img.shape

# Define parameters
pixels_per_inch = 1000
depth_per_cut = 125 # Value in thousands
depth = 500 # Value in thousands
jog_speed = "15"
feed_speed = "9"
plunge_speed = "3"
current_depth = 0
cuts = 2

# Find the center of the part - there should only be one contour
contours, _ = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contour = contours[0]

# Dilate the contour (this allows for a machining margin)
# This makes two parallel paths, a place for the chips to go
contour_dilate = cnc_functions.dilate_contour(contour, w, h, 20, 4)

# Change the contours from arrays to lists
outter = cnc_functions.contour_to_list(contour_dilate)
inner = cnc_functions.contour_to_list(contour)

# Draw the contours and show the user
h,w = img.shape
bg = np.zeros((h,w,3), np.uint8)
for i in range(len(inner)-1):
    a = inner[i]
    b = inner[i-1]
    cv2.line(bg, a, b, (0,255,0), cutter_size)
for i in range(len(outter)-1):
    a = outter[i]
    b = outter[i+1]
    cv2.line(bg, a, b, (255,0,255), cutter_size)
bg = cv2.drawContours(bg, [contour], -1, (255,255,0), 2)
bg = cv2.drawContours(bg, [contour_dilate], -1, (0,0,255), 2)
cv2.imshow('img', cv2.resize(bg, (987,987)))
cv2.waitKey()
cv2.destroyAllWindows()

# Create string for g_code
g_code = cnc_functions.g_code_header(jog_speed)

# Jog to the first point in the contour
dilate_origin = tuple(contour_dilate[0][0])
g_code += "G1 X" + str(dilate_origin[0]/pixels_per_inch) + "Y" + str(dilate_origin[1]/pixels_per_inch) + "\n"
origin = tuple(contour[0][0])
previous_point = dilate_origin

# Change the contours from arrays to lists
outter = cnc_functions.contour_to_list(contour_dilate)
inner = cnc_functions.contour_to_list(contour)

# Make cuts
for cut in range(cuts):
    # Plunge into the material
    g_code += "G1 F" + plunge_speed + "\n"
    current_depth -= depth_per_cut
    g_code += "G1 Z" + str(current_depth/pixels_per_inch) + "\n"

    # Cut the bigger contour
    g_code += "G1 F" + feed_speed + "\n"

    # Iterate through each point in the dilated contour
    for point in outter:
        x = point[0]/pixels_per_inch
        y = point[1]/pixels_per_inch
        g_code += "X" + str(x) + "Y" + str(y) + "\n"
 
    # Go back to the origin
    g_code += "G1 X" + str(dilate_origin[0]/pixels_per_inch) + "Y" + str(dilate_origin[1]/pixels_per_inch) + "\n"
        
    # Iterate through each point in the contour
    for point in inner:
        x = point[0]/pixels_per_inch
        y = point[1]/pixels_per_inch
        g_code += "X" + str(x) + "Y" + str(y) + "\n"
        
    # Go back to the origin
    g_code += "G1 X" + str(origin[0]/pixels_per_inch) + "Y" + str(origin[1]/pixels_per_inch) + "\n"

# Add the footer
g_code += cnc_functions.g_code_footer()

# Write g-code to disk
file = open("/home/stephen/Desktop/g_code.ngc", "a")
file.write(g_code)
file.close()
