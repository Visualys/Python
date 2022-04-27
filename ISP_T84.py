import math
import lib_CNC3018

unit = 2.54 #1/10 inch
ep = (1/3 * unit) + 0.2
d = (2/3 * unit) + 0.2


debug = True

def xprint(txt):
    if debug:
        print(txt)
    else:
        CNC3018.send(txt)

def calc_alpha(P0, P1):
    return math.atan2(P1[1]-P0[1], P1[0]-P0[0])

def calc_A(P, alpha):
    global ep, d
    beta = math.asin(ep/d)
    return[P[0]+(math.cos(alpha+beta)*(d/2)), P[1]+(math.sin(alpha+beta)*(d/2))]

def calc_B(P, alpha):
    global ep, d
    beta = math.asin(ep/d)
    return [P[0]+(math.cos(alpha-beta)*(d/2)), P[1]+(math.sin(alpha-beta)*(d/2))]

def calc_I(Pp, P, Pn):
    global ep
    alpha1 = calc_alpha(Pp, P) - math.pi
    if alpha1 < 0:
        alpha1 += 2*math.pi
    alpha2 = calc_alpha(P, Pn)
    L = (ep/2) / math.sin(abs(alpha1-alpha2)/2)
    phi = (alpha1+alpha2)/2
    return [P[0]+L*math.cos(phi), P[1]+L*math.sin(phi)]

def calc_I2(Pp, P, Pn):
    global ep
    alpha1 = calc_alpha(Pp, P) - math.pi
    if alpha1 < 0:
        alpha1 += 2*math.pi
    alpha2 = calc_alpha(P, Pn)
    L = (ep/2) / math.sin(abs(alpha1-alpha2)/2)
    phi = (alpha1+alpha2)/2
    phi -= math.pi
    if phi < 0:
        phi += 2*math.pi
    return [P[0]+L*math.cos(phi), P[1]+L*math.sin(phi)]

def calc_anginf180(Pp, P, Pn):
    global ep, d
    alpha1 = calc_alpha(Pp, P) - math.pi
    if alpha1 < 0:
        alpha1 += 2*math.pi
    alpha2 = calc_alpha(P, Pn)
    theta = alpha2-alpha1
    if(theta > 0):
        return 1
    else:
        return 0
    
def trace(points):
    xprint("M3 S500")
    xprint("G1 F90")
    global ep, unit
    for pt in points:
        pts = []
        for p in pt:
            pts.append([p[0]*unit, p[1]*unit])
        if len(pts)==1:
            n = 0
            p = [pts[n][0]+d/2, pts[n][1]]
            c = [pts[n][0]-p[0], pts[n][1]-p[1]]
            xprint("G0 X%f Y%f" % (p[0], p[1]))
            xprint("G1 Z-0.2")
            xprint("G3 X%f Y%f I%f J%f" % (p[0], p[1], c[0], c[1]) )
            xprint("G0 Z2")
        else:
            for n in range(len(pts)):
                if n==0:
                    alpha = calc_alpha(pts[n], pts[n+1])
                    p = calc_A(pts[n], alpha)
                    xprint("G0 X%f Y%f" % (p[0], p[1]))
                    xprint("G1 Z-0.2")
                    c = [pts[n][0]-p[0], pts[n][1]-p[1]]
                    p = calc_B(pts[n], alpha)
                    xprint("G3 X%f Y%f I%f J%f" % (p[0], p[1], c[0], c[1]) )
                elif n==len(pts)-1:
                    alpha = (math.pi + calc_alpha(pts[n-1], pts[n])) % (2*math.pi)
                    p = calc_A(pts[n], alpha)
                    xprint("G1 X%f Y%f" % (p[0], p[1]))
                    c = [pts[n][0]-p[0], pts[n][1]-p[1]]
                    p = calc_B(pts[n], alpha)
                    xprint("G3 X%f Y%f I%f J%f" % (p[0], p[1], c[0], c[1]) )           
                else:
                    if(calc_anginf180(pts[n-1],pts[n],pts[n+1])):
                        p = calc_I(pts[n-1],pts[n],pts[n+1])
                        xprint("G1 X%f Y%f" % (p[0], p[1]) )
                    else:
                        p = calc_I2(pts[n-1],pts[n],pts[n+1])
                        xprint("G1 X%f Y%f" % (p[0], p[1]) )
                        
            for n in range(len(pts)):
                m = len(pts) - n-1
                if m==0:
                    alpha = calc_alpha(pts[m], pts[m+1])
                    p = calc_A(pts[m], alpha)
                    xprint("G1 X%f Y%f" % (p[0], p[1]))

                elif m==len(pts)-1:
                    do = "nothing"
                else:
                    if(calc_anginf180(pts[m-1],pts[m],pts[m+1])):
                        p = calc_I2(pts[m-1],pts[m],pts[m+1])
                        xprint("G1 X%f Y%f" % (p[0], p[1]) )
                    else:
                        p = calc_I(pts[m-1],pts[m],pts[m+1])
                        xprint("G1 X%f Y%f" % (p[0], p[1]) )
            xprint("G0 Z2")
    xprint("G0 Z10")
    xprint("M5")
    xprint("G0 X0Y0")

def perce(points):
    xprint("M3 S500")
    xprint("G1 F90")
    xprint("G0 Z5")
    for pts in points:
        for n in range(len(pts)):
            if n==0 or n==len(pts)-1:
                xprint("G0 X%f Y%f" % (pts[n][0]*unit, pts[n][1]*unit))
                xprint("G0 Z1")
                xprint("G1 Z-1.5 F150")
                xprint("G0 Z5")
    xprint("G0 Z10")
    xprint("G0 X0Y0M5")

def invert_points(points, offset_X, offset_Y):
    xmax=0
    for pt in points:
        for p in pt:
            if p[0]>xmax:
                xmax=p[0]
    offset_X += xmax + 1
    for pt in points:
        for p in pt:
            p[0]*=-1
            p[0]+=offset_X
            p[1]+=offset_Y

def detoure(pts):
    xprint("M3 S500")
    xprint("G1 F90")
    for n in range(len(pts)):
        if n==0:
            xprint("G0 X%f Y%f" % (pts[n][0]*unit, pts[n][1]*unit))
            xprint("G1 Z-1.5")
        else:         
            xprint("G1 X%f Y%f" % (pts[n][0]*unit, pts[n][1]*unit))
    xprint("G0 Z10")
    xprint("G0 X0Y0M5")
        
              
     
def main():
    points = []
    points.append([[2,4],[4,2],[8,2],[8,4]])    
    points.append([[2,5]])
    points.append([[2,6]])
    points.append([[2,7],[1,7],[1,3],[3,1],[9,1],[9,6]])
    points.append([[2,8]])
    points.append([[2,9]])
    points.append([[2,10],[3,11],[10,11],[10,8]])
    points.append([[5,4],[6,4],[6,7],[7,8],[9,8]])
    points.append([[5,5],[4,5],[4,3],[7,3],[7,6],[8,7],[9,7]])
    points.append([[5,6]])
    points.append([[5,7]])
    points.append([[5,8]])
    points.append([[5,9]])
    points.append([[5,10],[9,10]])
    points.append([[10,4],[11,4],[11,7],[10,7]])
    points.append([[10,5],[10,6]])
    points.append([[12,5],[12,9],[11,10]])                 
    invert_points(points, 0, 0)
#    trace(points)
#    perce(points)
    detoure([[0,0],[13,0],[13,12],[0,12],[0,0]])

debug = False
xprint("G92 X0Y0Z10")
main()
