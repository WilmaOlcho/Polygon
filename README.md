# Polygon class

This is my attempt to differentiate if the point is inside polygon or not.

After initialisation, the polygon is created by adding vertices using "add_node(int|float x, int|float y)" method.
When all vertices are added, we can close our polygon using "close()" method.

>The polygon is closed in few steps:
>
>1. Creating external edges.
>2. Connecting nodes with lines that are not intersecting with existing ones.
>3. Removing lines outside external edges.
>4. Dividing polygon into triangles which are easier to manage.

The most difficult is step 3. Every line except edges is judged if it is outside the closed shape. To do that, the point in the middle of each one is selected and checked if the polygon's nodes are turning around it at least one time.  
For every node, there is angle and direction calculated with three points given (n-node, checked point, n+1-node), with checked point as the vertice.  
If the direction is to the left in regards to cross product of the vectors based on given points, the angle is substracted from the result and added otherwise.  
|Angle| >= 360 means that there was at least one full rotation around the selected point and it is inside the polygon.  
The lines which halfpoint's windind number is 0 are removed, becouse those are outside the polygon.

Afer closing the polygon, it is possible to check every point if it is inside or outside the polygon using "point_in_polygon(int|float x, int|float y) method". The triangle which is having given point in the inside can be returned by "select_triangle(int|float x, int|float y)" method.

## Examples

    #create Polygon object
    p = Polygon()

    #add vertices to form a square
    p.add_node(1,1)
    p.add_node(5,1)
    p.add_node(5,5)
    p.add_node(1,5)

    #close polygon
    p.close()

On the polygon above we can check the points if these are inside or not:

    for i in range(10):
        for j in range(10):
            if p.point_in_polygon(i,j):
                print("x",end='')
            else:
                print("0",end='')
        print()

The output will be:

    0000000000
    0xxxxx0000
    0xxxxx0000
    0xxxxx0000
    0xxxxx0000
    0xxxxx0000
    0000000000
    0000000000
    0000000000
    0000000000

The polygons can be created independently:

    p2 = Polygon()
    p2.add_node(1,7)
    p2.add_node(12,7)
    p2.add_node(12,13)
    p2.close()

And displayed in the same terminal:

    polygons = [p,p2]
    for i in range(15):
        for j in range(15):
            if (i, j) in polygons:
                print("X",end='')
            else:
                print("_",end='')
        print()

The result will be:

    _______________
    _XXXXX_X_______
    _XXXXX_X_______
    _XXXXX_XX______
    _XXXXX_XX______
    _XXXXX_XXX_____
    _______XXX_____
    _______XXXX____
    _______XXXX____
    _______XXXXX___
    _______XXXXX___
    _______XXXXXX__
    _______XXXXXXX_
    _______________
    _______________

The main.py represents the example where the polygons can be drawn and checked using mouse.
The yellow triangle is the one where is the mouse cursor.

![Polygons drawn using a mouse](/images/polygons.png)

The main.py requires pygame to run
