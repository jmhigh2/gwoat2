import cv2
import os
import random
import cherrypy
from threading import Thread
from jinja2 import Template

GOAT_SCALE_FACTOR = 3 #how much to scale goat photo

def draw_on_faces(filepath): #path to image

    print("Filepath: ",filepath) #debug
    file = os.path.basename(filepath) #get filename
    file = os.path.splitext(file)[0] #get filename without extension
    img = cv2.imread(filepath) #read image

    y_size, x_size, channels = img.shape

    print ("X size {}  Y size: {} Channels: {}".format(x_size, y_size, channels))

    photo_resize_x = x_size
    photo_resize_y = y_size

    while (photo_resize_x > 1920 or photo_resize_y > 1080):
        photo_resize_x = photo_resize_x//2
        photo_resize_y = photo_resize_y//2

    x_offset = 55 #pixels
    y_offset = 60


    print("X off: {}  y off: {} x_resize: {} y_resize: {}".format
    (x_offset, y_offset, photo_resize_x, photo_resize_y))

    resized_img = cv2.resize(img, (photo_resize_x, photo_resize_y))
    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY) #get grayscale image

    img_copy = gray_img.copy()

    classifier = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml') #open opencv model
    faces = classifier.detectMultiScale(img_copy, scaleFactor=1.1, minNeighbors=5) #detect faces

    print("Number of Faces: " + str(len(faces)))

    for (x, y, w, h) in faces: #loop over all faces
        print("X, Y, W, H: {} {} {} {}".format(x, y, w, h))
        w_scaled = int(w * GOAT_SCALE_FACTOR) #opencv returns a rectangle around face. Going to need to enlarge goat picture to cover all of it
        h_scaled = int(h * GOAT_SCALE_FACTOR)
        #print("goat w scaled:{}, h_scaled:{}".format(w_scaled, h_scaled))
        num =  random.randint(1, 7) #select random goat
        goat_img = cv2.imread("static/goats/" + str(num) + '.jpg')
        #cv2.rectangle(resized_img, (x, y), (x+w, y+h), (0, 255, 0), thickness=2)
        resized_goat = cv2.resize(goat_img, (w_scaled,h_scaled)) #scale goat picture to face
        print (resized_goat.shape)
        goat_a = 0
        goat_b = 0

        x_start = x - x_offset
        x_end = x - x_offset + w_scaled - 1
        y_start = y - y_offset
        y_end = y - y_offset + h_scaled - 1

        if (x_start < 0):
            x_start = 0
        if (y_start < 0):
            y_start = 0

        if (y_end > photo_resize_y):
            y_end = photo_resize_y

        if (x_end > photo_resize_x):
            x_end = photo_resize_x
        #print("x range: {}-{}".format(x - x_offset, x - x_offset + w_scaled - 1))
        #print ("y range: {}-{}".format(y - y_offset,  y - y_offset + h_scaled - 1))
        for a in range(x_start, x_end):
            for b in range(y_start, y_end):
                if (resized_goat[goat_b, goat_a][0] != 0 or resized_goat[goat_b, goat_a][1] != 0 or resized_goat[goat_b, goat_a][2] != 0):
                    resized_img[b,a] = resized_goat[goat_b, goat_a] #if pixel is not the darkest shade of black, overwrite with goat pixel.
                goat_b += 1
            goat_b = 0
            goat_a += 1


    new_file =  "new_" + file + '.jpg'
    cv2.imwrite("static/" + new_file, resized_img) #write modified image to media folder
    print("process complete for", new_file)
    return new_file

class Index():
    @cherrypy.expose
    def index(self):
      return open('templates/index.html','r').read()

    @cherrypy.expose
    def process(self, pic):
        data = pic.file.read()
        filename = pic.filename
        type = pic.content_type

        print("Received: ", filename)

        with open(filename, 'wb') as file:
            file.write(data)

        thread = Thread(target = draw_on_faces, args=((filename,)))
        thread.start()

        filewoext = filename.split(".")[0]
        new_file = "new_" + filewoext + ".jpg"

        web_page = open('templates/process.html').read()
        template = Template(web_page)
        return template.render(filename=new_file)


def error_page_404(status, message, traceback, version):
    return "404 Error!"

if os.getcwd() == '/app': #heroku settings
    address = '0.0.0.0'
else: #debug
    address = '127.0.0.1'


conf = {
'/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
},

'global': {
        'server.socket_host': address,
        'server.socket_port': int(os.environ.get('PORT', 8000)),
        'error_page.404': error_page_404
},

'/static': {
 'tools.staticdir.on': True,
 'tools.staticdir.dir': './static'
}
}

cherrypy.quickstart(Index(), '/', conf)
