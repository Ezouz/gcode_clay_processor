import re
from datetime import datetime


class Gcode:

    def describeModifications(self):
        string = ""
        if len(self.modifications) > 0:
            string = "; Modifications done : \n"
            for modif in self.modifications:
                string += "; {}\n".format(modif.describe())
        return string
    
    def export(self):
        # current dateTime
        now = datetime.now()
        # convert to string
        date_time_str = now.strftime("%Y-%m-%d_%H:%M:%S")
        # Enregistrer les nouvelles lignes dans un nouveau fichier GCode
        new_file_name = self.name + "_modified_" + date_time_str
        with open('Generated_files/' + new_file_name, 'w') as new_file:
            new_file.writelines(self.describeModifications())
            new_file.writelines(["\n","\n", "; Beguinning of the modified file\n"])
            new_file.writelines(self.modified_gcode_lines)
        print("Le fichier GCode a été modifié et enregistré sous le nom : ", new_file_name)
        input("")

    def __init__(self, filename):
        self.name = None
        self.gcode_lines = []
        self.modifications = []
        self.modified_gcode_lines = []
        self.first_part_comments_end = None
        self.last_part_comments_start = None
        self.layers = []
        self.spirals = []
        self.max_height = 0.0

        if filename is not "" :
            with open(filename, 'r') as f:
                self.name = filename[11:]
                self.gcode_lines = f.readlines()

        self.initValues()

    def show(self):
        print('---------------------------------')
        print('Name : ', self.name)
        print('---------------------------------')
        print('Max height : ', self.max_height)
        print('---------------------------------')
        # print('Last line of the comments at the start of the doc : ')
        # print(self.first_part_comments_end)
        # print('---------------------------------')
        # print('First line of the comments at the end of the doc : ')
        # print(self.last_part_comments_start)
        # print('---------------------------------')
        # print('Layers : ')
        # for index, layer in enumerate(self.layers):
        #     print(layer, "\n")
        print('Number of layers : ', len(self.layers))
        print('---------------------------------')
        # print('Spirals : ')
        # for index, spiral in enumerate(self.spirals):
        #     print(spiral, "\n")
        print('Number of spirals : ', len(self.spirals))
        print('---------------------------------')

    def initValues(self):
        num_lines = len(self.gcode_lines)
        last_comment_index = -1
        
        # Find the index of the last series of comments at the beginning of the file
        for i, line in enumerate(self.gcode_lines):
            if line.startswith(';') or line.startswith('\n') or line.startswith(' '):
                last_comment_index = i
            else:
                self.first_part_comments_end = last_comment_index
                break
        
        # Find the index of the last series of comments at the end of the file
        last_comment_index = -1
        for i in range(num_lines-1, -1, -1):
            if self.gcode_lines[i].startswith(';') or line.startswith('\n') or line.startswith(' '):
                last_comment_index = i
            else:
                self.last_part_comments_start = last_comment_index
                break

        # Find the layers
        layers = []
        current_layer = None
        MCommands_nb = 0
        comments_nb = 0
        # Find the spirals
        spirals = []
        start_index = 0
        end_index = 0
        height = None
        in_spiral = False
        end_spiral = False

        for i, line in enumerate(self.gcode_lines):
            # Find max_height
            if 'Z' in line:
                height_match = re.search(r'Z(\d+\.\d+)', line)
                if height_match:
                    height = float(height_match.group(1))
                    if height > self.max_height:
                        self.max_height = height
            # Find the layers
            if line.startswith('M'):
                MCommands_nb += 1
            if line.startswith(';'):
                comments_nb += 1
                continue  # skip comments
            if line.startswith('G1'):
                if 'Z' in line:  # new layer
                    if current_layer is not None:
                        current_layer['end_index'] = i - 1
                        if (current_layer['end_index'] - current_layer['start_index'] - MCommands_nb - comments_nb) > 3 :
                            layers.append(current_layer)
                    z_value = float(line.split('Z')[1].split()[0])
                    current_layer = {'start_index': i, 'end_index': -1, 'height': z_value}
                elif current_layer is not None and 'Z' not in line: # and 'E' in line:  # continuing layer
                    comments_nb = 0
                    MCommands_nb = 0
                    current_layer['end_index'] = i
            # Find the spirals
            if line.startswith('G1') and 'Z' in line and 'E' in line and ('X' in line or 'Y' in line):
                if not in_spiral:
                    start_index = i
                    height = float(line.split('Z')[1].split()[0])
                    in_spiral = True
                else :
                    if end_spiral:
                        end_index = i
                        in_spiral = False
                        end_spiral = False
                        spirals.append({'start_index': start_index, 'end_index': end_index, 'height': height})
                        start_index = 0
                    pass
            elif in_spiral and (line.startswith('G92') or line.startswith('G91') or line.startswith('G90')):
                end_spiral = True
    
        if in_spiral and start_index is not 0:
            spirals.append({'start_index': start_index, 'end_index': len(self.gcode_lines) - 1, 'height': height})

        # remove incomplete layers or incorrect
        self.layers = [layer for layer in layers if layer['start_index'] != -1 and layer['end_index'] != -1 and layer['start_index'] != layer['end_index']]
        # spirals.append({'start_index': start_index, 'end_index': end_index, 'height': height})
        self.spirals = spirals
        self.modified_gcode_lines = self.gcode_lines

        # self.show()


# for i, line in enumerate(self.gcode_lines):
#     if line.startswith(';') or line.startswith('\n') or line.startswith(' '):
#         pass
#     else: 
#         cleared_lines.append(line)