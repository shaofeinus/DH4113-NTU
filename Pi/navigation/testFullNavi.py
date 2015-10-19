import fullNavi

navi = fullNavi.fullNavi()
navi.generateFullPath("com1", 2, 1, 5)

x = int(raw_input("Enter x: "))
y = int(raw_input("Enter y: "))
heading = int(raw_input("Enter heading: "))
navi.updateCurLocation(x, y, heading)

count = 0
while(navi.fullNavigate() is False) :
    x = int(raw_input("Enter x: "))

    y = int(raw_input("Enter y: "))
    heading = int(raw_input("Enter heading: "))
    reroute = int(raw_input("Enter 1 to reroute: "))
    navi.updateCurLocation(x, y, heading)

    if reroute == 1 :
        navi.reroutePath()

