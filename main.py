import os.path
import tkinter as tk
import subprocess
from PIL import Image, ImageTk
import dlib
import util
import cv2

class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        # Add a button called "Click" instead of login and signup buttons
        self.click_button_main_window = util.get_button(self.main_window, 'Click', 'black', self.click)
        self.click_button_main_window.place(x=750, y=300)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        # Initialize Dlib's face detector
        self.detector = dlib.get_frontal_face_detector()

        # Call the add_webcam method to start capturing from the webcam
        self.add_webcam(self.webcam_label)

    def add_webcam(self, label):
        # Initialize the VideoCapture object
        self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = self.detector(gray)

        # Draw rectangles around detected faces
        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert the frame to PIL format
        pil_img = Image.fromarray(frame)

        # Convert PIL image to Tkinter format
        imgtk = ImageTk.PhotoImage(image=pil_img)

        # Update label with the new image
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        # Call process_webcam function again after 20 milliseconds
        self._label.after(20, self.process_webcam)

    def click(self):
        unknown_img_path = './.tmp.jpg'
        ret, frame = self.cap.read()
        cv2.imwrite(unknown_img_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
        print(output)
        name = output.split(',')[1][:-5]
        if name in ['unknown_person', 'no_persons_found']:
            # If the user is unknown, display a messagebox asking for username
            util.msg_box('Unknown User', 'Unknown user. Please register new user or try again.')
            self.ask_username()
        else:
            # If the user is recognized, display a welcome messagebox
            util.msg_box('Welcome back!', 'Welcome, {}'.format(name))
        os.remove(unknown_img_path)

    def ask_username(self):
        # Create a new window to ask for username
        self.username_window = tk.Toplevel(self.main_window)
        self.username_window.geometry("400x200+500+300")

        self.username_label = util.get_text_label(self.username_window, 'Enter name:')
        self.username_label.place(x=270, y=40)

        self.username_entry = util.get_entry_text(self.username_window)
        self.username_entry.place(x=270, y=80)

        self.username_submit_button = util.get_button(self.username_window, 'Submit', 'green', self.store_username)
        self.username_submit_button.place(x=290, y=190)

    def store_username(self):
        name = self.username_entry.get(1.0, "end-1c")
        ret, frame = self.cap.read()
        image_path = os.path.join(self.db_dir, '{}.jpg'.format(name))
        cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        print("Image saved at:", image_path)  # Print the full path of the saved image
        util.msg_box('Success!', 'User {} was registered successfully!'.format(name))
        self.username_window.destroy()

    def start(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()
