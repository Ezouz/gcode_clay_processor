# Use
`pip install -r requirements.txt`


# gcode_clay_processor


class Gcode initializated from a loaded gcode file : 

- first_part_comments_end is the index of last series of parsed lines that are comments in the gcode file.

- last_part_comments_start  is the index of last serie of line that are commented at the end of the opened file.

- layers is an array containing objects that have properties : start_index, end_index, height. 

the program delimitate differents layers (which are blocks of lines) when it finds a line starting with a G1 command and a Z coordinate, followed by at least 2 lines starting with a G1 command and not containing any Z but containing a E. The layer is composed by all the lines until the next occurence of a line starting with a G1 command and a Z coordinate.

the height variable contain the value of the Z coordinate mentioned just before.
the variable start_index is the line index of the first line of the layer that contain the instruction G1 and does not contains any Z coordinate.
the variable end_index is the line index of the last line of the layer that contain the instruction G1 and does not contains any Z coordinate.

- spiral is an array containing objects that have properties : start_index, end_index, height.
A spiral is composed by a serie of consecutives lines that starts with the instruction G1 and contains at least X or Y coordinates and must have a "Z" and "E". The end of a spiral is deterinated when encountering a line starting with a G92 or G91.
the height variable contain the value of the Z coordinate of the first line of the spiral.
the variable start_index is the line index of the first line of the spiral that contain the instruction G1.
the variable end_index is the line index of the last line of the spiral that contain the instruction G1.


    horizontal_movement_without_extrusion = {} # X || Y !Z height = z in the transition
    vertical_movement_without_extrusion = {} # Z !X !Y



i need a function in python to get a list of layers in a gcode file stored in a variable layers that is an array containing objects that have properties : start_index, end_index, height. 
The program delimitate differents layers (which are blocks of lines) when it finds a line starting with a G1 command and a Z coordinate, followed by at least 2 lines starting with a G1 command and not containing any Z but containing a E. The layer is composed by all the lines until the next occurence of a line starting with a G1 command and a Z coordinate.

the height variable contain the value of the Z coordinate mentioned just before.
the variable start_index is the line index of the first line of the layer that contain the instruction G1 and does not contains any Z coordinate.
the variable end_index is the line index of the last line of the layer that contain the instruction G1 and does not contains any Z coordinate.





///
TODO
dessin
: analyse image 
-> tracé ligne par ligne en zigzag
-> foncé = +- extrusion

dessin
:
-> conversion tracé vectoriel
-> mix de tracés

generation forme
: 
-> nuages de points (entrée, c4d ou generation)
-> relief (tri par ordonnées et slice, deduction tracé forme - ordre des points, floodfill)
-> remplissage grille de base

IA 
: 
-> remplissage de forme en tracé gcode
