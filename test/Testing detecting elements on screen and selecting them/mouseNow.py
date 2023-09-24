"""
Simple demo from https://automatetheboringstuff.com/chapter18/#:~:text=You%20can%20also%20perform%20a,around%20these%20two%20function%20calls

Note the mouse location and the colour of the pixel at the mouse location.
Will be useful for checking if a button is greyed out or not ?

"""

import pyautogui

# mouseNow.py - Displays the mouse cursor's current position.
print("Press Ctrl-C to quit.")
try:
    while True:
        # Get and print the mouse coordinates
        x, y = pyautogui.position()
        positionStr = "X: " + str(x).rjust(4) + " Y: " + str(y).rjust(4)
        pixelColor = pyautogui.screenshot().getpixel((x, y))
        positionStr += " RGB: (" + str(pixelColor[0]).rjust(3)
        positionStr += ", " + str(pixelColor[1]).rjust(3)
        positionStr += ", " + str(pixelColor[2]).rjust(3) + ")"
        # print(positionStr)
        print("\b" * len(positionStr), end="", flush=True)
        print(positionStr, end="")
except KeyboardInterrupt:
    print("\nDone.")
