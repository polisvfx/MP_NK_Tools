import nuke

def addCornerPinButtons():
    """Add Reference Frame buttons to a CornerPin node"""
    try:
        cornerPin = nuke.thisNode()
        
        # Add Reference Frame tab if it doesn't exist
        if not cornerPin.knob('ref_frame_tab'):
            tab = nuke.Tab_Knob('ref_frame_tab', 'Reference Frame')
            cornerPin.addKnob(tab)

        # Add Remove Animation button if it doesn't exist
        if not cornerPin.knob('remove_from_anim'):
            remove_anim_btn = nuke.PyScript_Knob('remove_from_anim', 'Remove From Animation')
            remove_anim_btn.setCommand('''
n = nuke.thisNode()
frame = nuke.frame()
for point in ['from1', 'from2', 'from3', 'from4']:
    k = n[point]
    x = k.getValueAt(frame)[0]
    y = k.getValueAt(frame)[1]
    k.clearAnimated()
    k.setValue([x, y])
''')
            cornerPin.addKnob(remove_anim_btn)

        # Add Copy To->From button if it doesn't exist
        if not cornerPin.knob('copy_to_to_from'):
            copy_btn = nuke.PyScript_Knob('copy_to_to_from', 'Copy Current To -> From')
            copy_btn.setCommand('''
n = nuke.thisNode()
frame = nuke.frame()
for i in ['1', '2', '3', '4']:
    to_val = n['to' + i].getValueAt(frame)
    n['from' + i].setValue(to_val)
''')
            cornerPin.addKnob(copy_btn)
    except:
        pass

# Function to add to existing/pasted nodes
def addToExistingCornerPins():
    for node in nuke.allNodes('CornerPin2D'):
        try:
            # Add Reference Frame tab if it doesn't exist
            if not node.knob('ref_frame_tab'):
                tab = nuke.Tab_Knob('ref_frame_tab', 'Reference Frame')
                node.addKnob(tab)

            # Add Remove Animation button if it doesn't exist
            if not node.knob('remove_from_anim'):
                remove_anim_btn = nuke.PyScript_Knob('remove_from_anim', 'Remove From Animation')
                remove_anim_btn.setCommand('''
n = nuke.thisNode()
frame = nuke.frame()
for point in ['from1', 'from2', 'from3', 'from4']:
    k = n[point]
    x = k.getValueAt(frame)[0]
    y = k.getValueAt(frame)[1]
    k.clearAnimated()
    k.setValue([x, y])
''')
                node.addKnob(remove_anim_btn)

            # Add Copy To->From button if it doesn't exist
            if not node.knob('copy_to_to_from'):
                copy_btn = nuke.PyScript_Knob('copy_to_to_from', 'Copy Current To -> From')
                copy_btn.setCommand('''
n = nuke.thisNode()
frame = nuke.frame()
for i in ['1', '2', '3', '4']:
    to_val = n['to' + i].getValueAt(frame)
    n['from' + i].setValue(to_val)
''')
                node.addKnob(copy_btn)
        except:
            pass

# Add the callback for new nodes
nuke.addOnCreate(addCornerPinButtons, nodeClass='CornerPin2D')

# Create menu item
#menubar = nuke.menu('Nuke')
#edit_menu = menubar.findItem('Edit')
#if not edit_menu:
#    edit_menu = menubar.addMenu('Edit')
#edit_menu.addCommand('Add Reference Buttons to CornerPins', addToExistingCornerPins)

# Run once when Nuke starts
# addToExistingCornerPins()