import cv2
filename = "image.jpg"
# find faces in image and create list
faces = []
img = cv2.imread(filename)
h, w = img.shape[:2]
for y in range(h):
    for x in range(w):
        if img[y, x] == 255:
            faces.append((y, x))
        else:
            continue
print('{0}'.format(len(faces)))