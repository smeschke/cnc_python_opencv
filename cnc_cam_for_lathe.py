import cv2, numpy as np

# Get profile
img = cv2.imread('/home/stephen/Desktop/club.png', 0)
_, img = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY)

# Width and height are in thousanths of an inch (1000 = 1 inch)
width = 500
height = 4000
img = cv2.resize(img, (height, width))

tops = [0]
# Iterate through each column in the image
for row in range(img.shape[1]-2):
    img_row = img[:, row:row+1]
    start = np.argmax(img_row)
    tops.append(start)
    a = row, 0
    b = row, start
    cv2.line(img, a, b, 123, 1)
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Display the path from the image
import matplotlib.pyplot as plt
plt.plot(tops)
plt.show()

gcode_string = "%\nM3\nG20\n%"



# Generate the gcode file




# Write the string to a file
f = open('/home/stephen/Desktop/workfile.ngc', 'w')
f.write(gcode_string)
f.close()
