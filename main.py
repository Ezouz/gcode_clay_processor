from src.menu import menu_principal
from gcode_utils import gcode_class

def main():
    gcode_file_selected=""
    gcode_file_selected = menu_principal(gcode_file_selected)
    print(gcode_file_selected)
    gcode = gcode_class.Gcode(gcode_file_selected)
    # print(gcode.max_height)
    # print('---------------------------------')
    # print('gcode.first_part_comments_end')
    # print(gcode.first_part_comments_end)
    # print('---------------------------------')
    # print('gcode.last_part_comments_start')
    # print(gcode.last_part_comments_start)
    # print('---------------------------------')
    # print('gcode.layers')
    # for index, layer in enumerate(gcode.layers):
    #     print(layer, "\n")
    # print('number of layers : ', len(gcode.layers))
    # print('---------------------------------')
    # print('gcode.spirals')
    # for index, spiral in enumerate(gcode.spirals):
    #     print(spiral, "\n")
    # print('number of spirals : ', len(gcode.spirals))
    # print('---------------------------------')
    

# TODO
# select a file => create instance
# instances can be multiples
# 

if __name__=="__main__":
	main()
        