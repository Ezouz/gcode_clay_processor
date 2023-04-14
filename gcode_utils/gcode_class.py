
# to determinate solid layers start_index and end_index must b differents
def get_layers(gcode):
    layers = []
    current_layer = None
    for i, line in enumerate(gcode):
        if line.startswith(';'):
            continue  # skip comments
        if line.startswith('G1'):
            if 'Z' in line:  # new layer
                if current_layer is not None:
                    current_layer['end_index'] = i - 1
                    layers.append(current_layer)
                z_value = float(line.split('Z')[1].split()[0])
                current_layer = {'start_index': -1, 'end_index': -1, 'height': z_value}
            elif current_layer is not None and current_layer['start_index'] == -1:  # start of layer
                current_layer['start_index'] = i
            elif current_layer is not None and 'Z' not in line:  # continuing layer
                current_layer['end_index'] = i
    if current_layer is not None:  # add last layer if not already added
        current_layer['end_index'] = len(gcode) - 1
        layers.append(current_layer)
    # remove incomplete layers
    layers = [layer for layer in layers if layer['start_index'] != -1 and layer['end_index'] != -1]
    return layers

def get_spirals(gcode):
    spirals = []
    start_index = 0
    end_index = 0
    height = None
    in_spiral = False
    
    for i, line in enumerate(gcode):
        if line.startswith('G1') and 'Z' in line and 'E' in line and ('X' in line or 'Y' in line):
            if not in_spiral:
                start_index = i
                height = float(line.split('Z')[1].split()[0])
                in_spiral = True
        elif in_spiral and (line.startswith('G92') or line.startswith('G91') or line.startswith('G90')):
            end_index = i - 1
            spirals.append({'start_index': start_index, 'end_index': end_index, 'height': height})
            in_spiral = False
        elif in_spiral and line.startswith('G1') and 'Z' in line and 'E' in line and ('X' in line or 'Y' in line):
            pass
        elif in_spiral and line.startswith('G1') and 'E0' in line:
            end_index = i
            spirals.append({'start_index': start_index, 'end_index': end_index, 'height': height})
            in_spiral = False
    return spirals


class Gcode:
    def __init__(self, filename):
        self.first_part_comments_end = None
        self.last_part_comments_start = None
        self.layers = []
        self.spirals = []
        self.gcode_lines = []
        
        with open(filename, 'r') as f:
            self.gcode_lines = f.readlines()
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

            self.layers = get_layers(self.gcode_lines)
            self.spirals = get_spirals(self.gcode_lines)
