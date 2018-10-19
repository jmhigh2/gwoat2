import cv2
import os
import random
import cherrypy

PHOTO_RESIZE_X = 920 #width of resized photos
PHOTO_RESIZE_Y = 480
GOAT_SCALE_FACTOR = 1.5 #how much to scale goat photo

def draw_on_faces(filepath): #path to image

    print(filepath) #debug
    file = os.path.basename(filepath) #get filename
    file = os.path.splitext(file)[0] #get filename without extension
    img = cv2.imread(filepath) #read image

    resized_img = cv2.resize(img, (PHOTO_RESIZE_X, PHOTO_RESIZE_Y)) #scale down photo. Make dynamic rescaling later
    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY) #get grayscale image

    img_copy = gray_img.copy()

    classifier = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml') #open opencv model
    faces = classifier.detectMultiScale(img_copy, scaleFactor=1.1, minNeighbors=5) #detect faces

    print("Number of Faces: " + str(len(faces)))

    for (x, y, w, h) in faces: #loop over all faces
        w_scaled = int(w * GOAT_SCALE_FACTOR) #opencv returns a rectangle around face. Going to need to enlarge goat picture to cover all of it
        h_scaled = int(h * GOAT_SCALE_FACTOR)
        num =  random.randint(1, 7) #select random goat
        goat_img = cv2.imread("static/goats/" + str(num) + '.jpg')
        #cv2.rectangle(resized_img, (x, y), (x+w, y+h), (0, 255, 0), thickness=2)
        resized_goat = cv2.resize(goat_img, (w_scaled,h_scaled)) #scale goat picture to face
        for a in range(0, PHOTO_RESIZE_X): #loop over every pixel in the photo
            for b in range(0, PHOTO_RESIZE_Y):
                if (a > x and a < x+w_scaled and (b > y and b < y + h_scaled)): #if current pixel is within the boundaries of the face
                    goat_a = x - a #get the corresponding pixel on goat photo
                    goat_b = y - b
                    if (resized_goat[goat_b, goat_a][0] != 0 or resized_goat[goat_b, goat_a][1] != 0 or resized_goat[goat_b, goat_a][2] != 0):
                        resized_img[b,a] = resized_goat[goat_b, goat_a] #if pixel is not the darkest shade of black, overwrite with goat pixel.


    new_file =  "new_" + file + '.jpg'
    cv2.imwrite("static/" + new_file, resized_img) #write modified image to media folder

    return new_file

class Index():
    @cherrypy.expose
    def index(self, name, pic):

        if not name:
            return open('index.html','r').read()

        else:
            print(name)
            data = pic.file.read()
            filename = pic.filename
            type = pic.content_type

            with open(filename, 'wb') as file:
                file.write(data)

            new_file = draw_on_faces(filename)

            return("""<html>

            <img src="static/{0}">

            </html>""".format(new_file) )

conf = {
'/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
},

'global': {
        'server.socket_host': '127.0.0.1',
        'server.socket_port': int(os.environ.get('PORT', 8080)),
    },

'/static': {
 'tools.staticdir.on': True,
 'tools.staticdir.dir': './static'
}
}

cherrypy.quickstart(Index(), '/', conf)
