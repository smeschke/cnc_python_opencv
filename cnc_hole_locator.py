import cv2
import numpy as np
import cnc_functions

# Read in image that has 
img = 255-cv2.imread('/home/stephen/Desktop/cnc_test/cnc_img_holes.png', 0)
# Buffer image
cutter_size = 250
img = cnc_functions.buffer(img,cutter_size, 1.25)

# Find the contours and show the image to the user
contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, -1, 123, 20)
cv2.imshow('img', cv2.resize(img, (567,567)))
cv2.waitKey()
cv2.destroyAllWindows()

# Find the contour centers
contour_centers = []
for contour in contours:
    center, _ = cv2.minEnclosingCircle(contour)
    contour_centers.append(center)


# Create string for g_code
jog_speed = "15"
plunge_speed = "3"
scale = 1000
depth = "-0.2"
g_code = "%" + "\n"
g_code += "M6 T1" + "\n"

# Write the g-code to the string
for center in contour_centers:
    g_code += "G1 F" + jog_speed + "X" + str(center[0]/scale) + " Y" + str(center[1]/scale) + "\n"
    g_code += "G1 F" + jog_speed + "Z0.1"+ "\n"
    g_code += "G1 F" + plunge_speed + "Z" + str(depth)+ "\n"
    g_code += "G1 F" + jog_speed + "Z0.1"+ "\n"
g_code += "M5\n"
g_code += "M02\n"
g_code += "%"

# Write gcode file to hard drive
file = open("/home/stephen/Desktop/g_code_holes.ngc", "a")
file.write(g_code)
file.close()
