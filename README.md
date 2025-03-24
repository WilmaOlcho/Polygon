# Polygon class

This is my attempt to differentiate if the point is inside polygon or not.

After initialisation, the polygon is created by adding vertices using "add_node(int|float x, int|float y)" method.
When all vertices are added, we can close our polygon using "close()" method.

At this moment, at first the edges od the polygon are created, then each node is connected to every other, where the line between those is not intersecting with any another line.

Next, the lines that are created outside the edges created in the beggining are removed and now the polygon is virtually divided into triangles.

In the end, the verticle where are only two lines connected to it is selected. This vertice is blacklisted for the next iteration, same for those two lines, and the three points given by those are added to the list of triangles.
This last operation is repeated for every each vertice that is connected with only two lines (except blacklisted ones).

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
