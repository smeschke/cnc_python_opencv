import cv2
import numpy as np
import cnc_functions

bg = 255-cv2.imread('/home/stephen/Desktop/star.png')
#bg = cv2.resize(bg, (000,2000))
cutter_size = 250

img = 255-cv2.imread('/home/stephen/Desktop/star.png',0)
img = cv2.flip(img, 1)
#img = cv2.resize(img, (2000,2000))

pixels_per_inch = 1000
feedSpeed = "15"
jogSpeed = "20"
plungeSpeed = "6"


clear_depth = 125
cut_depth = -125


# Mouse callback function
global click_list
positions, click_list, last = [], [], [(0,0)]
def callback(event, x, y, flags, param):
    last.append((x,y))
    if event == 1: click_list.append((x,y))
cv2.namedWindow('img')
cv2.setMouseCallback('img', callback)

# Draws the paths in the image
def draw_paths(paths, tt):
    for path in paths:
        for idx in range(len(path)-1):
            a, b = path[idx], path[idx+1]
            cv2.line(tt, a, b, (255, 0, 0), 5)
    return tt

# This is a list of paths. For example, if you recorded the trips you took in your car for a week you would have several paths.
paths = []
# This is a list of points that describes a single path. For example, if you took a trip in your can and recorded your gps coordinates every minute.
path = []
# Iterate through each frame of video
x,y = 0,0
roi_h, roi_w = 900,1400
while True:
    cv2.imshow('imgsmall', cv2.resize(bg, (250,250)) )    
    roi = bg[y:y+roi_h, x:x+roi_w].copy()
    cv2.circle(roi, last[-1], int(cutter_size/2), (0,255,255), 10)
    cv2.imshow('img', roi)
    # Wait, and allow the user to quit with the 'esc' key
    k = cv2.waitKey(1)
    # If the user presses 's', save the last mouse click to the path
    if k == 115:
        adjusted = click_list[-1][0]+ x,click_list[-1][1]+ y
        path.append(adjusted)
        cv2.circle(bg, adjusted, 2, (0,0,255), 10)
        if len(path) > 1: cv2.line(bg, path[-2], path[-1], (123,0,255), cutter_size)
    # If the user presses 't', save the path to the paths
    if k == 116:
        paths.append(path)
        bg = draw_paths(paths, bg)
        path = []
    if k != -1:
        print(k)
        print(x,y)
    if k == 56 and y>0: y-=100
    if k == 52 and x>0: x-=100
    if k == 50 and y+roi_h < bg.shape[0]: y +=100
    if k == 54 and x+roi_w < bg.shape[1]: x +=100
    
    if k == 27: break    
 
cv2.destroyAllWindows()
print(click_list)


# Function that converts the coordinates from the roughing calculations in to text gcode
def getRoughPassGcode(paths, pixels_per_inch, clear_depth, cut_depth):
    # Create a g_code string to work on
    g_code = ''
    # Iterate through each path
    for path in paths:
        # Go to the first point
        g_code += "G1 F" +  jogSpeed + "\n"
        print(path[0], pixels_per_inch)
        x = str(path[0][0]/pixels_per_inch)
        y = str(path[0][1]/pixels_per_inch)
        g_code += "G1 X" + x + "Y" + y + "\n"
        # Plunge
        g_code += "G1 F" + plungeSpeed + "\n"
        g_code += "G1 Z" + str(cut_depth/pixels_per_inch) + "\n"
        g_code += "G1 F" +  feedSpeed + "\n"
        for position in path:            
            x = str(position[0]/pixels_per_inch)
            y = str(position[1]/pixels_per_inch)
            g_code += "G1 X" + x + "Y" + y + "\n"
        # Lift the cutter
        g_code += "G1 Z" + str(clear_depth/pixels_per_inch) + "\n"
        g_code += "\n\n\n\n"
    return g_code


# Create string for g_code
g_code = cnc_functions.g_code_header(jogSpeed)
# Create the roughing code
g_code += getRoughPassGcode(paths, pixels_per_inch, clear_depth, cut_depth)

# Get the finish pass
g_code += cnc_functions.get_finish_pass(img, cutter_size, clear_depth, cut_depth, pixels_per_inch, feedSpeed, jogSpeed, plungeSpeed)

# Add the footer
g_code += cnc_functions.g_code_footer()
cv2.destroyAllWindows()

# Write g-code to disk
file = open("/home/stephen/Desktop/g_code.ngc", "a")
file.write(g_code)
file.close()
