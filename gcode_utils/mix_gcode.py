import re
from gcode_utils import scan_repertoire, Gcode, Modification

def change_base(object):
    print(f"Le fichier gcode sélectionné est : {object.name}\n")
    print("\n")
    print(object.describeModifications())

    gcode_vase = Gcode("")
    gcode_vase.name = object.name
    gcode_vase.gcode_lines = object.modified_gcode_lines
    gcode_vase.initValues()
    print(f"Fichier pour le vase :\n")
    gcode_vase.show()

    print(f"Selectionnez le fichier pour la base :\n")
    file_selected=scan_repertoire()
    gcode_base = Gcode(file_selected)
    print(f"Fichier pour la base :\n")
    gcode_base.show()

    # handle
    # if (len(object.spirals) == 0):
        
    spiral_start = min(gcode_vase.spirals, key=lambda x:x['height'])['height']

    index = None
    diff_min = float('inf')
    for i, d in enumerate(gcode_base.layers):
        if d['height'] < spiral_start:
            diff = abs(spiral_start - d['height'])
            if diff < diff_min:
                diff_min = diff
                index = i

    new_lines = []

    #ecrire la base jusqu'a l'index indiqué
    for i, line in enumerate(gcode_base.modified_gcode_lines):
        if i < gcode_base.layers[index]['end_index']:
            new_lines.append(line)
        else:
            break

    new_lines.append("; END OF THE PASTED BASE\n")
    new_lines.append("; logicaly add a G92 E0\n")
    new_lines.append("G92 E0\n")

    for i, line in enumerate(gcode_vase.modified_gcode_lines):
        if i >= gcode_vase.spirals[0]['start_index']:
            if 'Z' in line:
                match = re.search(r'Z(\d+\.\d+)', line)
                if match:
                    z_value = float(match.group(1))
                    new_z_value = z_value - diff_min
                    new_lines.append(re.sub(r'Z(\d+\.\d+)', f'Z{new_z_value:.3f}', line))
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

    params = []
    params.append({'key': 'Base file used for the vase spirals', 'value': gcode_vase.name})
    params.append({'key': 'File selected for the base layers', 'value': gcode_base.name})
    params.append({'key': 'original spiral Z values lowered of', 'value': "{:.2f}".format(diff_min)})
    params.append({'key': 'line index original file for base transition :', 'value': gcode_base.layers[index]['end_index']})
    params.append({'key': 'line index original file for base transition :', 'value': gcode_vase.spirals[0]['start_index']})
    modif = Modification("Paste base layers from another gcode", params)
    object.modifications.append(modif)
    object.modified_gcode_lines = new_lines
    return object