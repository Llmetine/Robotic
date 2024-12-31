import cv2
import mediapipe as mp
import time
from pyfirmata import Arduino, SERVO, util

time.sleep(2.0)

mp_draw = mp.solutions.drawing_utils  # Function to draw straight connect landmark points
mp_hand = mp.solutions.hands  # Function to find hands in camera

tipIds = [4, 8, 12, 16, 20]  # MediaPipe positions of fingertips

def check_user_input(input):
    try:
        # Convert input to an integer
        val = int(input)
        bv = True
    except ValueError:
        try:
            # Convert to float
            val = float(input)
            bv = True
        except ValueError:
            bv = False
    return bv

#### SERVO function control ####

def rotateservo(pin, angle):  # Function to control servo
    board.digital[pin].write(angle)
    time.sleep(0.015)

def servo(total, pin):  # Function to control servo based on finger count
    k = 0
    a = 0
    for i in range(10):
        if (total) == k:
            rotateservo(pin, a)
        else:
            k = k + 1
            a = a + 18
        if (total)==10:
            rotateservo(pin, 180)

########################################

# User input for camera and Arduino COM ports
cport = input('Enter the camera port: ')
while not (check_user_input(cport)):
    print('Please enter a number, not a string')
    cport = input('Enter the camera port: ')

comport = input('Enter the Arduino board COM port: ')
while not (check_user_input(comport)):
    print('Please enter a number, not a string')
    comport = input('Enter the Arduino board COM port: ')

board = Arduino('COM' + comport)
pin = 9
board.digital[pin].mode = SERVO  # Set pin mode to control servo

video = cv2.VideoCapture(0)  # Open Camera at index position 0

with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, image = video.read()  # Read frame from the camera
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert color from BGR to RGB
        image.flags.writeable = False  # Disable image modification
        results = hands.process(image)  # Process the image for hand landmarks
        image.flags.writeable = True  # Enable image modification
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Convert back to BGR for OpenCV display
        lmList = []
        total_fingers = 0  # Variable to hold the total number of fingers from both hands

        if results.multi_hand_landmarks:  # If hands are detected
            for hand_landmark in results.multi_hand_landmarks:
                hand = hand_landmark
                fingers = []  # List to store finger states (0 or 1)

                for id, lm in enumerate(hand.landmark):  # Iterate through hand landmarks
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])  # Store landmark position

                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)  # Draw hand landmarks

                # Count fingers for the current hand
                if hand.landmark[9].x < hand.landmark[5].x:  # Check if thumb is raised (for right hand)
                    if hand.landmark[tipIds[0]].y < hand.landmark[tipIds[0] - 1].y:  # Thumb raised (right hand)
                        fingers.append(1)
                    else:
                        fingers.append(0)
                elif hand.landmark[9].x > hand.landmark[5].x:  # Check if thumb is raised (for left hand)
                    if hand.landmark[tipIds[0]].y < hand.landmark[tipIds[0] - 1].y:  # Thumb raised (left hand)
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # Count other fingers (1 to 4)
                for id in range(1, 5):
                    if hand.landmark[tipIds[id]].y < hand.landmark[tipIds[id] - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                total_fingers += fingers.count(1)  # Add to total finger count

            # Control the servo based on the total number of raised fingers
            servo(total_fingers, pin)

            # Display the total number of fingers detected on the frame
            cv2.rectangle(image, (20, 300), (270, 425), (0, 255, 0), cv2.FILLED)
            cv2.putText(image, str(total_fingers), (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
            cv2.putText(image, "Servo", (120, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
            cv2.putText(image, str("Jeddelog"), (480, 30), cv2.FONT_HERSHEY_PLAIN, 2,
                (255, 255 , 255), 2)
            cv2.putText(image, str("670610749"), (460, 60), cv2.FONT_HERSHEY_PLAIN, 2,
                (255, 255 , 255), 2)

        # Show the image with landmarks
        cv2.imshow("Frame", image)

        k = cv2.waitKey(1)
        if k == ord('q'):  # Press "q" to exit the program
            break

video.release()
cv2.destroyAllWindows()
