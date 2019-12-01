import cv2
import numpy as np
import math

def get_finish_pass(img, cutter_size, clear_depth, cut_depth, pixels_per_inch, feedSpeed, jogSpeed, plungeSpeed):
        
    # Find the contours in the image
    contours = find_contours(img)
    print('eroding image')
    # Draw the contours by the cutter size to erode the image
    cv2.drawContours(img, contours, -1, 255, cutter_size)
    cv2.imshow('img', cv2.resize(img, (567,567)))
    cv2.waitKey(1000)


    # Make a list for the contour positions
    contourPositions = []
    # Find the center of the part - there should only be one contour
    contours, heir = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    # Iterate through the contours in the image
    for contour, h in zip(contours, heir[0]):
        # Convert the contour to the list
        contour_list = contour_to_list(contour)
        # Create a list for the current contour positions
        current_contour_positions = []
        # Add the first contour point to the list
        current_contour_positions.append(contour_list[0])
        for i in range(len(contour_list)-1):
            a = contour_list[i]
            b = contour_list[i-1]
            current_contour_positions.append(b)
            cv2.line(img, a, b, 123, cutter_size)
            cv2.imshow('img', cv2.resize(img, (567,567)))
            k = cv2.waitKey(1)
            if k == 27: break
        # Re-add the first point to the list so that it will complete the shape
        current_contour_positions.append(current_contour_positions[0])
        # Save the current contour positions to the list
        contourPositions.append(current_contour_positions)
    g_code = contour_to_gcode(contourPositions, pixels_per_inch, clear_depth, cut_depth, jogSpeed, feedSpeed, plungeSpeed)
    return g_code

# Function that converts lists of contours points to g-code
def contour_to_gcode(contourPositions, pixels_per_inch, clear_depth, cut_depth, jogSpeed, feedSpeed, plungeSpeed):
    g_code = ''
    for points in contourPositions:
        print('writing contour')
        # Go to the first point
        g_code += "G1 F" +  jogSpeed + "\n"
        g_code += "X" + str(points[0][0]/pixels_per_inch) + "Y" + str(points[0][1]/pixels_per_inch) + "\n"
        # Lower the cutter
        g_code += "G1 F" +  plungeSpeed + "\n"
        g_code +=  "Z" + str(cut_depth/pixels_per_inch) + "\n"
        g_code += "G1 F" +  feedSpeed + "\n"
        for point in points:
            g_code += "X" + str(point[0]/pixels_per_inch) + "Y" + str(point[1]/pixels_per_inch) + "\n"
        # Go to the first point again to complete the contour
        g_code += "X" + str(points[0][0]/pixels_per_inch) + "Y" + str(points[0][1]/pixels_per_inch) + "\n"
        # Retract the cutter
        g_code += "Z" + str(clear_depth/pixels_per_inch) + "\n"
        g_code += "G1 F" +  jogSpeed + "\n"
    # return the text g-code    
    return g_code

def buffer(img, cutter_size, buffer_factor):
    h,w = img.shape
    b = int(cutter_size* 1.25)
    img_buffer = np.zeros((h+b*2, w+b*2), np.uint8)
    img_buffer[b:b+h, b:b+w] = img
    return img_buffer

def contour_to_list(contour):
    points_list = []
    for point in contour: points_list.append(tuple(point[0]))
    return points_list

def dilate_contour(contour, width, height, kernelSize, iterations):
    kernel = np.ones((kernelSize, kernelSize), np.uint8)
    img = np.zeros((height, width), np.uint8)
    img = cv2.drawContours(img, [contour], -1, 255, cv2.FILLED)
    img = cv2.dilate(img, kernel, iterations = iterations)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours[0]

def erode_contour(contour, width, height, kernelSize, iterations):
    kernel = np.ones((kernelSize, kernelSize), np.uint8)
    img = np.zeros((hight, width), np.uint8)
    img = cv2.drawContours(img, [contour], -1, 255, cv2.FILLED)
    img = cv2.erode(img, kernel, iterations = iterations)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours[0]

def g_code_header(jog_speed):
    g_code = "%" + "\n"
    g_code += "G64 P0.001" + "\n"
    g_code += "M6 T1" + "\n"
    g_code += "M3 S5000" + "\n"
    g_code += "G1 F" + jog_speed + "\n"
    return g_code


def g_code_footer():
    g_code = "G0Z.1"
    g_code += "M5\n"
    g_code += "M02\n"
    g_code += "%"
    return g_code

def leftmost_point_in_contour_by_row(contour, y_position, w):
    leftMost = w, y_position
    for point in contour:
        point = tuple(point[0])
        if point[1] == y_position:
            if point[0] < leftMost[0]:
                leftMost = point
    return leftMost

def rightmost_point_in_contour_by_row(contour, y_position, w):
    rightMost = 0, y_position
    for point in contour:
        point = tuple(point[0])
        if point[1] == y_position:
            if point[0] > rightMost[0]:
                rightMost = point
    return rightMost

def distance(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def closest(a, b, c):
    if distance(a,b) < distance(a, c): return b
    else: return c

def contour_to_list(contour):
    contourList = []
    for point in contour: contourList.append(tuple(point[0]))
    return contourList

def arrage_list_to_nearest_point(point, contourList):
    closePointIndex = 0
    closeDistance = distance(point, contourList[0])
    for contourPoint in contourList:
        dist = distance(point, contourPoint)
        if dist < closeDistance:
            closeDistance = dist
            closePointIndex = contourList.index(contourPoint)
    newList = contourList[closePointIndex:] + contourList[:closePointIndex]
    return newList

def carve_region_contour_to_points(img, contour, cutter_size, stepover, w):    
    # Find the extereme points in the contour
    top = tuple(contour[contour[:,:,1].argmin()][0])
    bottom = tuple(contour[contour[:,:,1].argmax()][0])
    # Draw lines through the image
    y_position = int(top[1]+cutter_size/3)
    last_point = top
    leftSide = True
    path = [top]
    while y_position < bottom[1]:
        row = img[y_position:y_position+1, :]
        row = cv2.flip(row, 1)
        left = np.argmax(cv2.flip(row, 2)), y_position
        right = w-np.argmax(row), y_position
        if leftSide:
            side, opposite = left, right
            leftSide = False
        else:
            side, opposite = right, left
            leftSide = True
        path.append(side)
        path.append(opposite)
        last_point = opposite
        y_position += stepover        
    points = contour_to_list(contour)
    points = arrage_list_to_nearest_point(last_point, points)
    for point in points:
        path.append(last_point)
        last_point = point
    path.append(points[-1])
    path.append(points[0])
    return path

def find_contours(img):
    try: x,y = img.shape
    except: print('must use grayscale image in cnc_functions.find_contours(img)')
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


    
