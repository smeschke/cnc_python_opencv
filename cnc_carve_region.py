import cv2
import numpy as np
import cnc_functions

# Define parameters
cutter_size = 250
stepover = 75
jog_speed = "15"
pixels_per_inch = 1000
cut_depth = 125
feed_speed = "12"
plunge_speed = "3"

# Read in image
img = 255-cv2.imread('/home/stephen/Desktop/cnc_test/cnc_img_carve.png',0)
cutter_size = 250
img = cnc_functions.buffer(img, cutter_size, 1.25)
h,w = img.shape

# Find the contours in the image
contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("# of contours found in image: ", len(contours))
contour = contours[0]
bg = np.zeros_like(img)

# Generate the path
path = cnc_functions.carve_region_contour_to_points(img, contour,cutter_size, stepover, w)
for idx in range(len(path)-1):
    a, b = path[idx], path[idx+1]
    cv2.line(bg, a, b, 123, 1)
cv2.imshow('img', cv2.resize(bg, (987,987)))
cv2.waitKey()
cv2.destroyAllWindows()

# Create string for g_code
g_code = cnc_functions.g_code_header(jog_speed)
# Go to first point
point = path[0]
g_code += "G1 X" + str(point[0]/pixels_per_inch) + "Y" + str(point[1]/pixels_per_inch) + "\n"
# Plunge in
g_code += "G1 F" + plunge_speed + " Z" + str(-cut_depth/pixels_per_inch) + "\n"
# Go back to feed speed
g_code += "G1 F" + feed_speed + "\n"

for point in path: 
    x = point[0]/pixels_per_inch
    y = point[1]/pixels_per_inch
    g_code += "X" + str(x) + "Y" + str(y) + "\n"

# Retract to above the work
g_code += "G1 F" + plunge_speed + " Z" + str(.2) + "\n"
# Add the footer
g_code += cnc_functions.g_code_footer()
g_code += "G1 Z" + str(cut_depth/pixels_per_inch) + "\n"
file = open("/home/stephen/Desktop/g_code_carve.ngc", "a")
file.write(g_code)
file.close()
