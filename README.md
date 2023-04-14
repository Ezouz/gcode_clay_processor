# gcode_clay_processor




class Gcode initializated from a loaded gcode file : 

- first_part_comments_end is the index of last series of parsed lines that are comments in the gcode file.

- last_part_comments_start  is the index of last serie of line that are commented at the end of the opened file.

- layers is an array containing objects that have properties : start_index, end_index, height. 
a layer is composed by a serie of consecutives lines that starts with the instruction G1 and does not contains any Z coordinate. 
the program delimitate differents layers (which are blocks of lines) when it finds a line starting with a G1 command and a Z coordinate, followed by at least 2 lines starting with a G1 command and not containing any Z. the start of a layer is the line without Z following the one with one Z (ignoring lignes starting by a M instruction or a comment). The layer is composed by all the lines without Z following one with a Z.
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
