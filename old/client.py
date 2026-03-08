from common import ssid, psk, url
import requests as reqs
import json
import time
import threading as t
import random as r # testing

from pyray import * # window using raylib

shouldConnect = False
interval = 1  ## wait 5s between requests as accordant to mission doc

pulledData = {} # data fetched
startTime = time.time()

class ConnectThread(t.Thread):
    def __init__(self):
        t.Thread.__init__(self)
        self.name = "connectThread"

    def run(self):
        global pulledData
        global shouldConnect

        while True:
            time.sleep(interval)
            if (shouldConnect):
                pulledData = ConnectTo() ## connect

def FetchDict(url : str) -> dict:
    s = reqs.get(url=url).content.decode("utf-8")
    return json.loads(s)

def ConnectTo() -> dict:
    #return {'name': 'TEST', 'number': "EX23", 'time': time.time() - startTime, 'depth': r.randint(0, 10), 'pressure': r.randint(0, 10), 'temp': 13} # test data supplier
    return FetchDict(url=url)

def test(o : object) -> object:
    print(o)
    return o

# graph drawing - raylib
dataPoints = [] # list of tuples
xLabel = ""
yLabel = ""
xUnit = ""
yUnit = ""
originPos = (0, 0)
selectedIndex = -1

lineLength = 0
axisScale = (0, 0)
maxDepth = 0

shouldDrawPoints = True
shouldDrawAllPoints = False

def clamp(x : float, lo : float, hi : float):
    return max(min(x, lo), hi)

def drawAxes(x : int, y : int, xScale : int, yScale : int, col : Color) -> tuple[int, int]:
    fontSize = 10
    scaleFontSize = 5

    # y axis
    draw_line(x, y, x, y - lineLength, col)
    draw_text(f"{yLabel} ({yUnit})", x - measure_text(f"{yLabel} ({yUnit})", fontSize) - 10, y - (lineLength // 2), fontSize, col)
    draw_text("Y", x - (measure_text("Y", 10) // 2), y + 2, 10, col)

    # x axis
    draw_line(x, y - lineLength, x + lineLength, y - lineLength, col)
    draw_text(f"{xLabel} ({xUnit})", x + (lineLength // 2) - (measure_text(f"{xLabel} ({xUnit})", fontSize) // 2), y - lineLength - 25, fontSize, col)
    draw_text("X", x + lineLength + (measure_text("X", 10) // 2), y - lineLength - 5, 10, col)

    # scales
    if (shouldDrawAllPoints): draw_text("0", x - measure_text("0", scaleFontSize), y - lineLength, scaleFontSize, col)
    #draw_text(f"{xScale}", x + lineLength - measure_text(f"{xScale}", scaleFontSize), y, scaleFontSize, col) # x
    #draw_text(f"{yScale}", x - measure_text(f"{yScale}", scaleFontSize) - 5, y - lineLength, scaleFontSize, col) # y

    return (x, y)

def addPlottedPoint(x : float, y : float) -> None:
    if (not (x, y) in dataPoints):
        dataPoints.append((x, y))

def graphPos(x : float, y : float, drawn : list[tuple[int, int]]) -> tuple[int, int]:
    global axisScale

    if (not shouldDrawAllPoints):
        z = axisScale[1]
        axisScale = (len(drawn), z)
        x = drawn.index((x, y))

    if (axisScale[0] == 0):
        siX = 0
    else:
        siX = lineLength / axisScale[0]

    if (axisScale[1] == 0):
        siY = 0
    else:
        siY = lineLength / axisScale[1]

    scaleIncrement = (siX, siY)

    return (originPos[0] + (x * scaleIncrement[0]), originPos[1] - lineLength + (y * scaleIncrement[1]))

def drawPoints(radius : float, col : Color, selCol : Color, drawn : list[tuple[int, int]]) -> None:
    for point in drawn:
        c = col
        if (dataPoints.index(point) == selectedIndex):
            c = selCol
        pos = graphPos(point[0], point[1], drawn)
        draw_circle(int(pos[0]), int(pos[1]), radius, c)

def drawAxisPosOfPoints(col : Color, drawn : list[tuple[int, int]]) -> None:
    for point in drawn:
        pos = graphPos(point[0], point[1], drawn)
        if (not shouldDrawAllPoints or (not point[0] == 0 and not point[0] == axisScale[0])):
            draw_text(f"{point[0]}", int(pos[0]) - measure_text(f"{point[0]}", 5) // 2, originPos[1] - lineLength - 15, 5, col) # x
        if (not shouldDrawAllPoints or (not point[1] == 0 and not point[0] == axisScale[1])):
            draw_text(f"{point[1]}", originPos[0] - measure_text(f"{point[1]}", 5) - 5, int(pos[1]) - measure_text(f"{point[1]}", 5) // 2, 5, col) # y

def drawLinesBetweenPoints(col : Color, drawn : list[tuple[int, int]]) -> None:
    lastPoint = graphPos(drawn[0][0], drawn[0][1], drawn)
    thisPoint = (0, 0)
    for index in range(len(drawn)):
        thisPoint = graphPos(drawn[index][0] , drawn[index][1], drawn)
        draw_line(int(lastPoint[0]), int(lastPoint[1]), int(thisPoint[0]), int(thisPoint[1]), col)
        lastPoint = thisPoint

def drawPointCoords(col : Color, drawn: list[tuple[int, int]]) -> None:
    global selectedIndex
    for point in drawn:
        pos = graphPos(point[0], point[1], drawn)
        if (circleCollide(get_mouse_position(), pos[0], pos[1], 5)):
            draw_text(f"({point[0]}{xUnit}, {point[1]}{yUnit})", int(get_mouse_position().x) - 20, int(get_mouse_position().y) - 10, 10, col)
            if (is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT)):
                selectedIndex = dataPoints.index(point)

def circleCollide(vec : Vector2, circleX : int, circleY : int, radius : float) -> bool:
    if (vec.x > circleX - radius and vec.x < circleX + radius):
        if (vec.y > circleY - radius and vec.y < circleY + radius):
            return True
    return False

def getHighest(tupleIndex : int, drawn: list[tuple[int, int]]) -> float:
    h = drawn[0][tupleIndex]
    for index in range(1, len(drawn)):
        if (drawn[index][tupleIndex] > h):
            h = drawn[index][tupleIndex]
    return h

def modifyAxisScales(drawn: list[tuple[int, int]]) -> None:
    return (getHighest(0, drawn), getHighest(1, drawn))


# main
if __name__ == "__main__":
    ####### WINDOW SETTINGS #########

    xLabel, yLabel = "Time", "Depth"
    xUnit, yUnit = "s", "m"
    windowSize = 800
    lineLength = windowSize - 200
    maxPoints = 15

    ################################

    cl = ConnectThread()
    pulledData = {'name': 'impROVise', 'number': '', 'time': 0, 'depth': 0, 'pressure': 0, 'temp': 0}

    # WINDOW
    init_window(windowSize, windowSize, "impROVise Float Data")

    # ready the improvise logo texture
    improviseLogo = load_texture("improvise.png")

    cl.daemon = True
    cl.start()

    drawn = []

    while not window_should_close(): # x = TIME, y = DEPTH
        begin_drawing()
        clear_background(BLACK)

        draw_text(f"Team Name: {pulledData['name']}", 20, 20, 20, WHITE)
        draw_text(f"Team Num.: {pulledData['number']}", 20, 40, 20, WHITE)
        draw_text(f"Time: {round(pulledData['time'])} s", 20, 60, 20, WHITE)
        draw_text(f"Depth: {round(pulledData['depth'], 2)} m", 20, 80, 20, WHITE)
        draw_text(f"Pressure: {round(pulledData['pressure'], 2)} Pa", 20, 100, 20, WHITE)
        draw_text(f"Water Temperature: {round(pulledData['temp'], 2)} °C", 20, 120, 20, WHITE)

        if (is_key_pressed(KeyboardKey.KEY_SPACE)):
            shouldDrawPoints = not shouldDrawPoints

        if (is_key_pressed(KeyboardKey.KEY_LEFT_CONTROL)):
            shouldConnect = not shouldConnect

        if (is_key_pressed(KeyboardKey.KEY_A)):
            shouldDrawAllPoints = not shouldDrawAllPoints


        draw_text(f"Drawing Points? <SPACE>: {shouldDrawPoints}", windowSize - measure_text(f"Drawing Points? <SPACE>: {shouldDrawPoints}", 10)- 20, 10, 10, WHITE)
        draw_text(f"Making Requests? <L-CTRL>: {shouldConnect}", windowSize - measure_text(f"Making Requests? <CTRL>: {shouldConnect}", 10) - 20, 20, 10, WHITE)
        if (shouldConnect): draw_text(f"Request Frequency: {interval}s", windowSize - measure_text(f"Request Frequency: {interval}s", 10) - 10, 30, 10, WHITE)
        draw_text(f"Drawing {len(drawn)} points ; <A> to Limit to {maxPoints}", windowSize - measure_text(f"Drawing {len(drawn)} points ; <A> to Limit to {maxPoints}", 10)- 20, 40, 10, WHITE)
        draw_text(f"FPS: {get_fps()}", windowSize - measure_text(f"FPS: {get_fps()}", 10)- 20, 50, 10, WHITE)

        draw_text(f"Time: {time.strftime('%m/%d/%Y, %H:%M:%S')}", windowSize - measure_text(f"Time: {time.strftime('%m/%d/%Y, %H:%M:%S')}", 18)- 20, 100, 18, WHITE)
        if (not selectedIndex == -1): draw_text(f"Selected: ({dataPoints[selectedIndex][0]}{xUnit}, {dataPoints[selectedIndex][1]}{yUnit})", windowSize - measure_text(f"Selected: ({dataPoints[selectedIndex][0]}{xUnit}, {dataPoints[selectedIndex][1]}{yUnit})", 18)- 20, 120, 18, WHITE)

        draw_texture_ex(improviseLogo, Vector2(((windowSize // 2) - improviseLogo.width * 0.15 // 2) + 20, 10), 0, 0.15, WHITE)

        # Graph
        addPlottedPoint(int(pulledData['time']), round(float(pulledData['depth']), 2))

        drawn = []
        if (not shouldDrawAllPoints):
            drawn = dataPoints[-maxPoints:]
        else:
            drawn = dataPoints

        originPos = drawAxes(100, windowSize - 20, axisScale[0], axisScale[1], WHITE)
        drawLinesBetweenPoints(RED, drawn)
        if (shouldDrawPoints): 
            drawPoints(5, GREEN, ORANGE, drawn)
        drawAxisPosOfPoints(WHITE, drawn)
        drawPointCoords(WHITE, drawn)
        axisScale = modifyAxisScales(drawn)

        end_drawing()
    close_window()
