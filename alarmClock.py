#Imports
from machine import I2C, Pin
import time
import math

#Functions
#Turning the buzzer and led on as long as it is the correct time for the alarm to go off and the alarm has not already been turned off
def alarm():
    global alarmSound
    if(alarmSound == True and alarmTurnedOff == False):
        buzzer.high()
        led.on()
        #Sleeping for half a second then turning the buzzer and led off
        time.sleep(0.5)
        buzzer.low()
        led.off()

#Moving the cursor on the LCD display to the left
def moveLeft():
    #Finding cursor position
    global cursorX
    global cursorY
    #Ensuring the cursor stays on the screen
    if(cursorX > 0):
        #Moving cursor and updating cursor position variable
        cursorX -= 1
        lcd.move_to(cursorX, cursorY)
    #Making the cursor visible to the user
    lcd.blink_cursor_on()
    #Waiting 200 milliseconds to ensure the cursor function does not immediately get called again repeatedly and move the cursor immedialtely to the left side of the display
    time.sleep(0.2)
    
#Moving the cursor on the LCD display to the right
def moveRight():
    #Finding cursor position
    global cursorX
    global cursorY
    #Ensuring the the cursor stays on the screen
    if(cursorX < 15):
        #Moving cursor and updated cursor position variable
        cursorX += 1
        lcd.move_to(cursorX, cursorY)
    #Making the cursor position visible to the user
    lcd.blink_cursor_on()
    #Waiting 200 milliseconds to ensure the cursor function does not immediately get called again repeatedly and move the cursor immedialtely to the right side of the display
    time.sleep(0.2)

#Using the current cursor position to use + or - symbols on the display to signal the user where to place the cursor to change the alarm time
def configButtonPress():
    global cursorX
    global alarmHour
    global alarmMin
    #If and elif statements finding which button the cursor is on if any and then nested if statements ensuring that the time the user is trying to change the alarm to is a valid time
    if(cursorX == 4):
        if(alarmHour == 0):
            alarmHour = 23
        else:
            alarmHour -= 1
    elif(cursorX == 7):
        if(alarmHour == 23):
            alarmHour = 0
        else:
            alarmHour += 1
    elif(cursorX == 12):
        if(alarmMin == 0):
            alarmMin = 59
        else:
            alarmMin -= 1
    elif(cursorX == 15):
        if(alarmMin == 59):
            alarmMin = 0
        else:
            alarmMin += 1


#Componet initialization
#LED code
led = Pin(15, Pin.OUT)

#Buzzer code
buzzer = Pin(17, Pin.OUT)

#LCD code
from pico_i2c_lcd import I2cLcd
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
cursorX = 0
cursorY = 1
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)


#Button code
#initializing the alarm time changing button
controlButton = Pin(18, Pin.IN, Pin.PULL_UP)
conStateNow = 1
conStateOld = 1

#initializing the button to turn off the alarm
alarmButton = Pin(14, Pin.IN, Pin.PULL_UP)
alarmStateNow = 1
alarmStateOld = 1
alarmSound = False
alarmTurnedOff = False

    
#Joystick Code
xPin = 27
yPin = 26
xJoy = machine.ADC(xPin)
yJoy = machine.ADC(yPin)

#Main code
#Initializing variables
savedMin = -1
alarmHour = 12
alarmMin = 0
configAlarmHour = 12
configAlarmMin = 0
oldSec = ''
#Infinite while loop to keep the code iterating
while True:
    #Reinitializing variables
    alarmSound = False
    xVal = xJoy.read_u16()
    yVal = yJoy.read_u16()
    alarmStateNow == alarmButton.value()
    currentTime = []
    #Stripping the local time variable for the current hour, minute, and second
    for i in time.localtime():
        currentTime.append(str(i))
    if(int(currentTime[4]) < 10):
        currentTime[4] = '0' + currentTime[4]
    if(int(currentTime[5]) < 10):
        currentTime[5] = '0' + currentTime[5]
    if(int(currentTime[3]) < 10):
        currentTime[3] = '0' + currentTime[3]
    #Ensuring that 1 second has passed since the last time the following code ran
    if(oldSec != currentTime[5]):
        oldSec = currentTime[5]
        #saving the current time in a variable
        timeConfig = (str(currentTime[3]) + ':' + str(currentTime[4]) + ':' + str(currentTime[5]))
        #Preparing the LCD display to be written on again
        lcd.clear()
        #Writing to the LCD display with some extra formatting to keep the amount of digits in the hours, minutes, and seconds consistent
        if(alarmHour < 10 and alarmMin < 10):
            #Reformatting the time in the event of single digit numbers and saving the new variable for later use
            configAlarmHour = '0' + str(alarmHour)
            configAlarmMin = '0' +str(alarmMin)
            lcd.putstr(timeConfig + '        Hour-' + str(configAlarmHour) + '+ Min-' + str(configAlarmMin) + '+')
        elif(alarmMin < 10 and alarmHour > 9):
            configAlarmMin = '0' + str(alarmMin)
            configAlarmHour = str(alarmHour)
            lcd.putstr(timeConfig + '        Hour-' + str(alarmHour) + '+ Min-' + str(configAlarmMin) + '+')
        elif(alarmHour < 10 and alarmMin > 9):
            configAlarmHour = '0' + str(alarmHour)
            configAlarmMin = str(alarmMin)
            lcd.putstr(timeConfig + '        Hour-' + str(configAlarmHour) + '+ Min-' + str(alarmMin) + '+')
        else:
            configAlarmHour = str(alarmHour)
            configAlarmMin = str(alarmMin)
            lcd.putstr(timeConfig + '        Hour-' + str(alarmHour) + '+ Min-' + str(alarmMin) + '+')
        #Resetting the cursor to ensure that it is blinking and visible to the user along with moving it to the last know location
        lcd.blink_cursor_on()
        lcd.move_to(cursorX, cursorY)
        #Checking if the alarm has been turned off
        if(savedMin != currentTime[4]):
            alarmTurnedOff = False
            savedMin = -1
            #Checking if the alarm time equals the real time, setting off the alarm
            if(currentTime[3] == configAlarmHour and currentTime[4] == configAlarmMin):
                #Verifying that the alarm should be sounded
                alarmSound = True
                #Calling the alarm function
                alarm()
    #Joystick parameters finding whether the joystick is being pushed to the right or left
    if(xVal <= 5000 and (yVal >= 25000 and yVal <= 35000)):
        moveRight()
    elif(xVal >= 50000 and (yVal >= 25000 and yVal <= 35000)):
        moveLeft()

#Finding the current state of the button that changes the alarm time
    conStateNow = controlButton.value()
    #Finding if the button has just been pressed down
    if(conStateNow == 1 and conStateOld == 0):
        #Changing the alarm time
        configButtonPress()
    #Recording the state of the buttons
    conStateOld = conStateNow
    alarmStateNow = alarmButton.value()
    #Finding if the alarm button was just pressed
    if(alarmStateNow == 1 and alarmStateOld == 0):
        #Turning off the alarm and saving the current minute when the alarm was turned off
       alarmTurnedOff = True
       savedMin = currentTime[4]
    #Recording the state of the button
    alarmStateOld = alarmStateNow
    
   