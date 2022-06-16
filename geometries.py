# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Wed Apr  8 17:09:42 2020

@author: Timothe
"""

import sys, os, warnings
from math import sin, cos, radians, pi, sqrt
from statistics import mean


import _dependancies as _deps

try :
    from shapely.geometry import LineString
except ImportError as e :
    LineString = _deps.default_placeholder("shapely",e)
    _deps.dep_miss_warning(LineString)

try :
    import numpy as np
except ImportError as e :
    np = _deps.default_placeholder("numpy",e)
    _deps.dep_miss_warning(np)


# try :
#     from shapely.geometry import LineString
# except (ImportError, FileNotFoundError) as e:
#     warnings.warn(f"Shapely import failed Either not installed or some .dll files mising. You won't be able to use Trajectory_Window function. Original error : {e}")
#     LineString = e


#from matplotlib.collections import LineCollection # UNUSED

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("__filename__"))))
#print(os.path.dirname(os.path.dirname(os.path.abspath("__name__"))))
#from LibUtils import database_IO

    #TODO: Change the "removenan" method for the traces splicesArray, inside the Ufunctions
    #TODO: Remove the function that are desprecated and regroup the ones using numpy inside the else to be able to put the other ones outside.

class UPoint():
    """
    Upoint class is used to create an uniformized way of storing 2D points data. It can be used with other objects of that library to calculate basic geomety.

    Attributes:
        vec np.array : a numpy array of two values containing the x,y coordinates. x and y methods are just wrapper to access the values stored there.
        x scalar : returns x coordinate of the current point.
        y scalar : returns y coordinate of the current point.
        isnan bool : returns True if either x or y coordinates of the current point are np.nan. False otherwise

    """
    @property
    def x(self):
        return self.vec[0]

    @property
    def y(self):
        return self.vec[1]

    @property
    def isnan(self):
        if np.isnan(self.x) or np.isnan(self.y) :
            return True
        return False

    @property
    def plt(self):
        return ( self.x , self.y, 'o' )

    def __init__(self,x,y=None):
        """
        Contructor for Upoint class. (2D space point)

        Args:
            x (scalar / np.array): x coordinate of the point if an int is given for y.
                If no y coordinate argument is given, x is expected to be a 2 value arraylike with first index as x and second index as y.
            y (scalar): y coordinate of the point or None, if x and y coords are given in an array like structure as fisrt argument. Defaults to None.

        Returns:
            UPoint : An instance of the class
        """
        if y is not None :
            if isinstance( x , (int,np.integer , float, np.floating)) and  isinstance( y , (int,np.integer , float, np.floating)) :
                self.vec = np.array([x,y])
            else :
                raise TypeError("data not understood - with two parameters to UPoint, they are expected to both be real numbers")
        else :
            if isinstance(x,(np.ndarray,list)):
                self.vec = np.array(x)
            elif isinstance(x, UPoint):
                self.vec = np.array(x.vec)
            else :
                raise TypeError("data not understood : Must be either an ndarray, an UPoint, or two real numbers")

    def distance(self,point):
        """
        Euclidian distance between the current point instance, and another point instance passed as first argument.

        Args:
            point (UPoint): the point to calculate distance relative to the current UPoint instance.

        Returns:
            dist (int float): the distance, in the same unit as the coordinate system used for both UPoints.

        """
        dist = sqrt( (  point.x - self.x  )**2 + (  point.y - self.y  )**2 )
        return dist

    def toline(self,point):
        return ULine(self,point)

    def dot(self,point):
        """
        Performs the dot vector product of the object holding this point and another Upoint object given as argument.

        Args:
            point (UPoint): The other Upoint object to perform dot product..

        Returns:
            scalar: The result of the dot product of the two points.

        """
        return np.dot(self.vec,point.vec)

    def project(self, distance, angle):
        distance = - distance
        rads = pi/2 - radians(-angle)
        return UPoint( self.x + distance*cos(rads), self.y + distance*sin(rads) )

    def angle(self, pointB, pointC = None):
        return UGetAngle( self , pointB,  pointC )

    def __str__(self):
        return "UPoint:\nx :" + str(self.x) + "\ty :" + str(self.y) + "\n"

    def __repr__(self):
        return self.__str__()



class ULine():
    """
    The purpose of the class is to make "readable" and to fix a convention for x and y array dimensions on points, lines and array of lines.
    Thus, the most easy to acess value is by .x and .y properties, or A and B for points.
    If acessing array is necessary, for speed purposes, you can get the values by calling specific properties.
    For Upoints, you can call .vec ( as vector ).
    The returned array has x on index 0 and y on index 1
    For Ulines, you can call .seg ( as segment ).
    The returned array has 2 dimensions, first is point A, second is point B.
    In each dimension you have an arrya containing x and y as in vec.
    For UlineCollection you can call .array, or acess slices by directly indexing the class object.
    The array has 3 dimensions, and their content is described in the method dim_names
    """
    def __init__(self,A,B = None):

        if B is not None :
            if isinstance(A, UPoint) and isinstance(B, UPoint):
                self.seg = np.stack([ A.vec , B.vec ])
            else :
                raise Exception("data not understood - with two parameters to ULine, they are expected to both be a UPoint")
        else :
            if isinstance(A,(np.ndarray,list)):
                self.seg = np.array(A)
            elif isinstance(A, ULine):
                self.seg = np.array(A.seg) 
            else :
                raise Exception("data not understood : Must be either an ndarray, an Uline or two Upoints")


    @property
    def X(self):
        return np.array([self.A.x,self.B.x])

    @property
    def Y(self):
        return np.array([self.A.y,self.B.y])

    @property
    def A(self):
        return UPoint(self.seg[0,:])

    @property
    def B(self):
        return UPoint(self.seg[1,:])

    @property
    def length(self):
        return self.A.distance(self.B)

    def angle(self,item = None,snapto = 'B'):

        if item is None :
            return UGetAngle(self.A , self.B)

        elif isinstance(item, UPoint):
            return UGetAngle(self.A , self.B, item)

        elif isinstance(item, ULine):
            return UGetAngle( self.A , self.B,  item.jump( self.B ).A )

    @property
    def swap(self):
        return ULine(self.B,self.A)

    @property
    def isnan(self):
        if self.A.isnan or self.B.isnan :
            return True
        return False

    def shift(self,point):
        return self.seg + point.vec

    def jump(self,point,snapto = 'B'):
        jumpvec = eval( f"self.{snapto}.vec - point.vec" )
        return ULine( self.seg - jumpvec )

    def __str__(self):
        return "ULine:\nA :" + self.A.__str__().replace('UPoint:\n', '') + "B :" + self.B.__str__().replace('UPoint:\n', '')

    def __repr__(self):
        return self.__str__()

    @property
    def plt(self):
        return ( self.X , self.Y, 'o-' )

class UPointCollection():

    def __init__(self,items_list,Y=None):
        if Y is None :
            if isinstance(items_list, np.ndarray):
                self.collection = []
                for i in range(items_list.shape[0]):
                    self.collection.append( UPoint( items_list[i,0] , items_list[i,1] ) )
            else:
                self.collection = items_list
        else :
            self.collection = []
            for i in range(len(items_list)):
                self.collection.append( UPoint( items_list[i] , Y[i] ) )
                
    
    def __len__(self):
        return len(self.collection)
            
                
    def dist_time(self):
        variation = []
        for index in range(len(self.collection)-1):
            variation.append( self.collection[index].distance( self.collection[index+1] ) )
        return variation

    def append(self,point):
        self.collection.append(point)

    @property
    def Xs(self):
        return np.array(self.array[:,0])

    @property
    def Ys(self):
        return np.array(self.array[:,1])

    @property
    def array(self):
        """Dimension 0 : Time
        Dimension 1 : coord x or y
        """
        veclist = []
        for point in self.collection:
            veclist.append( point.vec )

        return np.array(veclist)

    def to_line_collection(self,**kwargs):
        from matplotlib.collections import LineCollection 
        #linelist = []
        points = self.array.reshape(-1, 1, 2)
        segments= np.concatenate([points[:-1], points[1:]], axis=1)
        
        # for index in range(len(self.collection)-1):
        #     linelist.append( [ self.collection[index].vec ,  self.collection[index+1].vec  ] )
        # arr = np.array(linelist)
        # if kwargs.get("removenans", False) :
        #     arr = removenans(arr)
        return LineCollection( segments ), segments

    def __getitem__(self, index):
        if isinstance(index,slice):
            return UPointCollection(self.collection[index])
        elif isinstance(index , int):
            return self.collection[index]

    def __str__(self):
        string = ''
        for index , point in enumerate(self.collection):
            string = string + str(index) + " :" + point.__str__().replace('UPoint:\n', '')
        return "UPointCollection :\n" + string

    def __repr__(self):
        return self.__str__()

    @property
    def plt(self):
        return self.array.T

class ULineCollection():

    #define the main variabl as a list of Ulines , and compute the temporal vector by stacking segs, should be fast, and not called so often, so not a problem

    def __init__(self,items_list):

        if isinstance(items_list , list):
            self.collection = items_list
        elif isinstance(items_list ,np.ndarray):
            if len(items_list.shape) == 1 :
                self.collection = items_list.tolist()
            elif len(items_list.shape) == 2 and np.min(items_list.shape) == 0:
                self.collection = items_list.flatten().tolist()
            elif len(items_list.shape) == 2 :
                self.collection = []
                for index in range(items_list.shape[0]):
                    self.collection.append( ULine( UPoint ( items_list[index,0:2] ) , UPoint ( items_list[index,2:4] ) ) )
            else :
                raise Exception("Can't use a multiple dimension array yet with ULineCollection. For now, use 1D array or list of lines. Integration for ndim array of coordinates will be included later if necessary")

    def append(self,line):
        self.collection.append(line)

    @property
    def As(self):
        Alist = []
        for line in self.collection:
            Alist.append( line.A )

        return UPointCollection(Alist)

    @property
    def Bs(self):
        Blist = []
        for line in self.collection:
            Blist.append( line.B )

        return UPointCollection(Blist)

    @property
    def array(self):
        """Dimension 0 : Time
        Dimension 1 : Point A or B
        Dimension 2 : coord x or y
        """
        seglist = []
        for line in self.collection:
            seglist.append( line.seg )
        return np.array(seglist)


    def isnan(self,mode = 'all'):
        if mode == 'any':
            mode = True
        elif mode == 'all':
            mode = False
        else :
            raise Exception("ULineCollection isnan mode not understood")
        found = 0
        for line in self.collection :
            if line.isnan:
                if mode :
                    return True
                else :
                    found = found + 1
        if found == len(self.collection):
            return True
        return False

    @property
    def shape(self):
        return self.array.shape

    @property
    def dim_names(self):
        return ["time","A/B","x/y"]

    def __str__(self):
        string = ''
        for index , line in enumerate(self.collection):
            string = string + str(index) + " :" + line.__str__().replace('ULine:\n', '')
        return "ULineCollection :\n" + string

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):

        if isinstance(index,slice):
            return ULineCollection(self.collection[index])
        elif isinstance(index,int):
            return self.collection[index]
        #return getattr(cls, x)

    def __setitem__(self,index,data):
        self.collection[index[0]].seg[index[1],index[2]] = data

    def angles(self,**kwargs):
        angles = []
        for line in self.collection:
            angles.append( line.angle() )
        angles = np.array(angles)
        if kwargs.get("removenans", False):
            angles = removenans(angles)
        return angles

    def dist_tracker(self):
        """calculate distances between trackers all along the collection
        """
        distances = []
        for line in self.collection:
            distances.append( line.length )
        return np.array(distances)

    def dist_time(self,tracker = 'both', **kwargs):
        """calculate distances between a trackers to a point in time and the next all along the collection ( 2 dimensions, one for each tracker )
        """
        variation = []
        for index in range(len(self.collection)-1):
            variation.append( [ self.collection[index].A.distance( self.collection[index+1].A ) , self.collection[index].B.distance( self.collection[index+1].B ) ] )
        variation = np.array(variation)
        if tracker == 'A':
            variation =  variation[:,0]
        elif tracker == 'B':
            variation =  variation[:,1]
        if kwargs.get("removenans", False):
            variation = removenans(variation)
        return variation


def UGetAngle(A,B, C = None):
    """Takes two UPoints and calculate direction vectors from the two points and a conventionnal [0,-1] vector
    Then calculates the determinant and the dot product of the two vectors,
    and then compute arc tangent of the resulting vectors.
    Formula : θ = atan2( ∥u×v∥ , u∙v ) https://www.jwwalker.com/pages/angle-between-vectors.html
    Returns angles in degrees, and as a convention , if used with classic indexed image array values,
    when oriented up, a line returns 0 degree (compared to convention). When tilting from that position
    to the right gives positive angles ,and when tilting left, give negative angles.
    cf schema :
      -45°   0°   +45°
        \    |    /
         \   |   /
    """
    if A.isnan or B.isnan :
        return np.nan

    if C is None :
        C = UPoint( *( B.vec + np.array([0, -1]) ) )
    else :
        if C.isnan :
            return np.nan

    v0 = A.vec - B.vec #direction vectors from points vectors
    v1 = C.vec - B.vec #direction vectors from points vectors

    angle = np.math.atan2( np.linalg.det([v0,v1]), np.dot(v0,v1) ) # In radians. Create the determinant and the dot product of the two vectors,
    #then compute arc tangent of the two resulting vectors. Formula : θ = atan2( ∥u×v∥ , u∙v ) https://www.jwwalker.com/pages/angle-between-vectors.html
    return -np.degrees(angle)

def removenans(array):
    """
    Deprecated. Better use the dunction designed in

    Args:
        array (TYPE): DESCRIPTION.

    Returns:
        array (TYPE): DESCRIPTION.

    """

    array = np.squeeze(array)

    axis = len(np.shape(array))

    if axis == 1:
        array = array[~np.isnan(array)]
    if axis == 2:
        array = array[ ~np.isnan(array).any(axis=1) , : ]
    if axis == 3:
        array = array[ ~np.isnan(array).any(axis=(1,2)) , : , : ]
    return array

def UChgtVar(a,b,teta, x,y) :
    """ a,b = la translation subie par le repère;teta = l'angle en degré de la
    rotation subie par le repère; coord = dans l'ancien repère, matrice de [x,y]
    a transposer dans le nouveau repère
    Retourne les coordonnées correspondantes dans le nouveau repère, avant
    rotation et translation"""

    tetar=teta*pi/180
    oldcoord=[]
    xy = cos(tetar) * x-sin(tetar) * y+a , sin(tetar) * x+cos(tetar) * y+b

    return xy

def orth_change(PointCollec, Unoseneckline, sym = False, frameShape = (500,250,None)):
    if sym :
        sym_mult = -1
    else :
        sym_mult = 1

    newPointCollec = []
    for Point in PointCollec.collection:
        nx, ny = UChgtVar(0,0  , Unoseneckline.angle(), sym_mult * Point.x, Point.y - frameShape[1]) #cancels the rotation ( shift to get coordinates around the middle of y )

        corra = Unoseneckline.A.x
        coorb = Unoseneckline.A.y - frameShape[1]

        nx, ny = UChgtVar(corra,coorb  ,0, nx, ny + frameShape[1]) # translation to get at the old coordinates

        newPointCollec.append( UPoint(nx,ny) )

    return UPointCollection( newPointCollec )

    #########################



    # def AngleWrapper(coordf,coordb):
    #     """
    #     /!\ Deprecated, do not use, prefer using Unified geometry classes
    #     Parameters
    #     ----------
    #     coordf : array like
    #         DESCRIPTION.
    #     coordb : array like
    #         DESCRIPTION.

    #     Returns
    #     -------
    #     listAngle : TYPE
    #         DESCRIPTION.

    #     """

    #     listAngle = []

    #     for UI in range(coordf.shape[0]):
    #         angle = get_angle(coordf[UI,:],coordb[UI,:])
    #         listAngle.append(angle)

    #     return listAngle

    # def get_angle(p0, p1=np.array([0,0]), p2=None):
    #     """
    #     /!\ Deprecated, do not use, prefer using Unified geometry classes
    #     Parameters
    #     ----------
    #     p0 : [x,y] numpy array
    #         Point
    #     p1 : [x,y] numpy array , optional
    #         DESCRIPTION. The default is np.array([0,0]).
    #     p2 : TYPE, optional
    #         DESCRIPTION. The default is None.

    #     Returns
    #     -------
    #     TYPE
    #         DESCRIPTION.

    #     """
    #     if np.isnan(p0[0]) :
    #         return np.nan
    #     if p2 is None:
    #         p2 = p1 + np.array([0, -1])
    #     v0 = np.array(p0) - np.array(p1)
    #     v1 = np.array(p2) - np.array(p1)

    #     angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))
    #     return -np.degrees(angle)


def Corner_detection(Centroid,Contour):

    DistList = []
    for I in range(np.shape(Contour)[0]):
        dist = Distance(Centroid[0],Centroid[1],Contour[I,0],Contour[I,1])
        DistList.append(dist)
    Difflist = np.diff(DistList,n=1)
    return DistList,Difflist

def Distance(x1,y1,x2,y2):
    dist = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

def Distances(A,B):
    if A.shape == B.shape:
        if np.min(A.shape) == 1 and A.ndim <= 2:
            A = A.flatten()
            B = B.flatten()
        dists = []

        if A.ndim == 2 :
            for Pointidx in range(A.shape[0]) :
                dists.append( Distance( A[Pointidx,0]  , A[Pointidx,1]  , B[Pointidx,0]  , B[Pointidx,1]  ) )
        elif A.ndim == 1:
            for Pointidx in range(A.shape[0]-1) :
                dists.append( Distance( A[Pointidx]  , B[Pointidx]  , A[Pointidx+1]  , B[Pointidx+1]  ) )
        else :
            raise ValueError("Too many dimensions. Max : 2D array")
        return dists
    else:
        raise ValueError("Cannot compute distances for arrays of points A and B of different shapes")

def Means(A,B):#aray must be dimension  time : dimension 2 of size 2 x, y values that requirers to be meaned with other arrays
    if A.shape == B.shape:
        coordlist = []
        for i in range(A.shape[0]):

            Xmean = mean( [A[i,0], B[i,0]] )
            Ymean = mean( [A[i,1], B[i,1]] )
            coordlist.append([Xmean, Ymean])
        return coordlist

    else:
        raise ValueError("Cannot compute means for arrays of points A and B of different shapes")








def Trajectory_Window(Trajectory,window,height = None, **kwargs):
    from extern import empty_df
    """
    Functions that take a trajectory and returns a dataframe with the coordinates at wich the trajectory crossed a window, described by two points.

    Todo:
        Move that function to the analysis package. It's use is not general enough to be put inside Utils package. Or make it mode general and useable easily with UGeometry toolkit.

    Args:
        Trajectory (TYPE): DESCRIPTION.
        window (TYPE): DESCRIPTION.
        height (TYPE, optional): DESCRIPTION. Defaults to None.
        **kwargs (TYPE): DESCRIPTION.

    Returns:
        pd.dataframe None : The dataframe with the coordinates where the trajectories crossed.
    """
    if isinstance(LineString,ImportError):
        raise LineString("Shapely must be installed in order to use this function")

    start = kwargs.get("start", 0)

    outdict = kwargs.get("data", empty_df(columns=['time','x','y','w_label',"w_h"], dtypes=[int,float,float,str,int]) )

    FRAMEINDEX = outdict.shape[0]

    if start == -1 :
        if FRAMEINDEX > 0:
            start = outdict.iloc[outdict.shape[0]-1]["time"]
        else :
            start = 0

    ##window = [x1,y1,x2,y2,x3,y3...]
    ##or
    ##window = [x1,x2]

    if height is not None :
        #TODO
        koord = [ (window[0],height) , (window[1],height) ]
    else :
        koord = [ (window[0],window[2]) , (window[1],window[3])]
        height = window[1]

    shWindow = LineString(koord)

    for index in range(start,Trajectory.shape[0]-1):
        if not np.isnan(Trajectory[index,0]) and not np.isnan(Trajectory[index+1,0]):

            smalist =  [ (Trajectory[index,0],Trajectory[index,1]) , (Trajectory[index+1,0],Trajectory[index+1,1]) ]

            segment = LineString(smalist)
            intersects = shWindow.intersection(segment)

            if not intersects.is_empty :
                if intersects.geom_type == "Point":
                    #print(intersects.x, intersects.y)
                    intersx = intersects.x
                    intersy = intersects.y
                else :
                    #print(intersects[0].x, intersects[0].y)
                    intersx = intersects[0].x
                    intersy = intersects[0].y


                #print(f"crossed for line1 trial {inde x} at frame {smali} ")
                outdict.at[FRAMEINDEX,"w_h"] = int(height)
                outdict.at[FRAMEINDEX,"w_label"] = str(koord)
                outdict.at[FRAMEINDEX,"time"] = index
                outdict.at[FRAMEINDEX,"x"] = intersx
                outdict.at[FRAMEINDEX,"y"] = intersy
                return outdict.astype({'time': 'int', 'x': 'float', 'y': 'float', 'w_label': 'str', 'w_h': 'int'})

    return outdict.astype({'time': 'int', 'x': 'float', 'y': 'float', 'w_label': 'str', 'w_h': 'int'})