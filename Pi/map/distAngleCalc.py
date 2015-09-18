import math

# distance formula
def distance(x1, y1, x2, y2) :
        return math.sqrt((int(x2)-int(x1))**2 + (int(y2)-int(y1))**2)

# returns the angle from point 1 to point 2,
# with respect to magnetic north
# angle returned in range -180 to 180
def calcAngle(x1, y1, x2, y2, northAt) :
        angle = 0
        xprime = x2 - x1
        yprime = y2 - y1

        if xprime == 0 or yprime == 0: 
                if x2 > x1 :
                        angle = 90
                elif x2 < x1 :
                        angle = 270
                elif y2 > y1 : 
                        angle = 0
                elif y2 < y1 :
                        angle = 180 
        # degree obtained via reverse tan2 inputs and add 360 if angle < 0
        else : 
                angle = math.degrees(math.atan2(xprime, yprime))
        
        if angle < 0 :
                angle += 360
        angle -= northAt
        
        if angle > 180 :
                angle -= 360
        elif angle <= -180 :
                angle += 360
        return angle
