class Gcode:
    def __init__(self, filename):
        self.first_part_comments_end = None
        self.last_part_comments_start = None
        self.layers = []
        self.spirals = []
        self.gcode_lines = []

        with open(filename, 'r') as f:
            lines = f.readlines()
            cleared_lines = []
            num_lines = len(lines)
            last_comment_index = -1
            
            # Find the index of the last series of comments at the beginning of the file
            for i, line in enumerate(lines):
                if line.startswith(';') or line.startswith('\n') or line.startswith(' '):
                    last_comment_index = i
                else:
                    self.first_part_comments_end = last_comment_index
                    break
            
            # Find the index of the last series of comments at the end of the file
            last_comment_index = -1
            for i in range(num_lines-1, -1, -1):
                if lines[i].startswith(';') or line.startswith('\n') or line.startswith(' '):
                    last_comment_index = i
                else:
                    self.last_part_comments_start = last_comment_index
                    break

            for i, line in enumerate(lines):
                if line.startswith(';') or line.startswith('\n') or line.startswith(' '):
                    pass
                else: 
                    cleared_lines.append(line)

            layers = []
            current_layer = None
            MCommands_nb = 0
            comments_nb = 0
            for i, line in enumerate(lines):
                # si le nombre de ligne de ce layer - comments est maj composé de M
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
            # remove incomplete layers or incorrect
            self.layers = [layer for layer in layers if layer['start_index'] != -1 and layer['end_index'] != -1 and layer['start_index'] != layer['end_index']]

            spirals = []
            start_index = 0
            end_index = 0
            height = None
            in_spiral = False
            end_spiral = False
            for i, line in enumerate(lines):
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
                            start_index = 0
                            spirals.append({'start_index': start_index, 'end_index': end_index, 'height': height})
                        pass
                elif in_spiral and (line.startswith('G92') or line.startswith('G91') or line.startswith('G90')):
                    end_spiral = True
         
            if in_spiral and end_spiral and start_index is not 0:
                spirals.append({'start_index': start_index, 'end_index': len(lines) - 1, 'height': height})
            # spirals.append({'start_index': start_index, 'end_index': end_index, 'height': height})
            self.spirals = spirals
