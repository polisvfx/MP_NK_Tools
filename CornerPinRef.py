"""Reference Frame buttons for CornerPin2D nodes.

The button commands are stored inside the .nk file together with the knobs,
so they keep working for anyone opening the script - even without this tool
installed. Keep the command strings self-contained (only `nuke`, no imports
from this module).
"""
import nuke

# Knob names are kept stable so existing .nk files stay compatible.
TAB_KNOB = 'ref_frame_tab'
BAKE_KNOB = 'remove_from_anim'
COPY_KNOB = 'copy_to_to_from'
# Read-only list of reference frames. A String_Knob (not Text_Knob) so undo restores it.
FRAMES_KNOB = 'ref_frames'
_OLD_INFO_KNOB = 'ref_frame_info'  # Text_Knob used by an earlier version

RESET_KNOB = 'reset_from'

_CMD_TEMPLATE = '''
n = nuke.thisNode()
f = int(nuke.frame())
%(vals)s
keyed = False
was_disabled = nuke.Undo.disabled()
if was_disabled:
    nuke.Undo.enable()
nuke.Undo.begin(%(undo)r)
try:
    for i, v in zip('1234', vals):
        k = n['from' + i]
%(write)s
    rk = n.knob(%(frames)r)
    if rk:
%(update_frames)s
finally:
    nuke.Undo.end()
    if was_disabled:
        nuke.Undo.disable()
'''

_VALS_FROM_TO = "vals = [n['to' + i].valueAt(f) for i in '1234']"

# CornerPin2D default 'from' = corners of the input format (root format if unconnected).
_VALS_DEFAULT = '''\
fmt = n.input(0).format() if n.input(0) else nuke.root().format()
w, h = fmt.width(), fmt.height()
vals = [(0, 0), (w, 0), (w, h), (0, h)]'''

# Frame list: replaced by the current frame, or extended when animated points were keyed.
_FRAMES_ADD = '''\
        frames = {f}
        if keyed:
            frames.update(int(s) for s in rk.value().replace(',', ' ').split()
                          if s.lstrip('-').isdigit())
        rk.setValue(', '.join(str(x) for x in sorted(frames)))'''

_FRAMES_CLEAR = "        rk.setValue('')"

# Bake: drop any 'from' animation and set the current-frame 'to' value as a static value.
_WRITE_STATIC = '''\
        k.clearAnimated()
        k.setValue(list(v))'''

# Copy: key animated channels at the current frame, set static channels directly.
_WRITE_KEY_IF_ANIMATED = '''\
        for c in (0, 1):
            if k.isAnimated(c):
                k.setValueAt(v[c], f, c)
                keyed = True
            else:
                k.setValue(v[c], c)'''

def _make_cmd(vals, write, update_frames, undo):
    return _CMD_TEMPLATE % {'vals': vals, 'write': write, 'update_frames': update_frames,
                            'undo': undo, 'frames': FRAMES_KNOB}


BAKE_FROM_CMD = _make_cmd(_VALS_FROM_TO, _WRITE_STATIC, _FRAMES_ADD, 'CornerPin: Bake Reference')
COPY_TO_FROM_CMD = _make_cmd(_VALS_FROM_TO, _WRITE_KEY_IF_ANIMATED, _FRAMES_ADD,
                             'CornerPin: Copy To -> From')
RESET_FROM_CMD = _make_cmd(_VALS_DEFAULT, _WRITE_STATIC, _FRAMES_CLEAR, 'CornerPin: Reset From')

# name: (label, command, tooltip, starts a new line)
_BUTTONS = {
    BAKE_KNOB: ('Bake Reference at Current Frame', BAKE_FROM_CMD,
                "Make the current frame the only reference frame: copy the 'to' points "
                "into the 'from' points and remove any 'from' animation.", True),
    COPY_KNOB: ('Set From = To at Current Frame', COPY_TO_FROM_CMD,
                "Copy the 'to' points at the current frame into the 'from' points. "
                "Animated 'from' points get a keyframe, static ones are set directly.", True),
    RESET_KNOB: ('Reset From to Default', RESET_FROM_CMD,
                 "Reset the 'from' points to the corners of the input format, remove their "
                 "animation and clear the reference frames.", False),
}

# Tab layout: two buttons, then the frames list with Reset on the same line.
_LAYOUT = (BAKE_KNOB, COPY_KNOB, FRAMES_KNOB, RESET_KNOB)


def _make_knob(name, frames_value=''):
    if name == FRAMES_KNOB:
        knob = nuke.String_Knob(FRAMES_KNOB, 'Reference frames', frames_value)
        knob.setFlag(nuke.DISABLED)
        knob.setTooltip('Frames used as reference. Bake resets this list, Set adds to it '
                        'when the from points are animated, Reset clears it.')
        return knob
    label, cmd, _, startline = _BUTTONS[name]
    knob = nuke.PyScript_Knob(name, label, cmd)
    if startline:
        knob.setFlag(nuke.STARTLINE)
    else:
        knob.clearFlag(nuke.STARTLINE)
    return knob


def _ensure_knobs(node):
    """Add the Reference Frame tab/knobs in layout order, or refresh the commands if they exist."""
    if not node.knob(TAB_KNOB):
        node.addKnob(nuke.Tab_Knob(TAB_KNOB, 'Reference Frame'))

    old_info = node.knob(_OLD_INFO_KNOB)
    if old_info is not None:
        node.removeKnob(old_info)

    # Knobs can only be appended, so if the layout is incomplete or out of order,
    # remove everything from the first misplaced knob on and re-add it in order.
    names = [k.name() for k in node.allKnobs()]
    positions = [names.index(k) if k in names else None for k in _LAYOUT]
    frames_value = node[FRAMES_KNOB].value() if node.knob(FRAMES_KNOB) else ''
    for i, pos in enumerate(positions):
        if pos is None or (i and positions[i - 1] is not None and pos < positions[i - 1]):
            for name in _LAYOUT[i:]:
                if node.knob(name) is not None:
                    node.removeKnob(node[name])
            break

    for name in _LAYOUT:
        knob = node.knob(name)
        if knob is None:
            node.addKnob(_make_knob(name, frames_value))
        elif name in _BUTTONS:
            label, cmd, tooltip, _ = _BUTTONS[name]
            if knob.value() != cmd:
                # Upgrade buttons saved by older versions of this tool.
                knob.setValue(cmd)
                knob.setLabel(label)
        if name in _BUTTONS:
            node[name].setTooltip(_BUTTONS[name][2])


def addCornerPinButtons():
    """onCreate callback: add Reference Frame buttons to the created CornerPin."""
    try:
        _ensure_knobs(nuke.thisNode())
    except Exception as e:
        nuke.tprint('CornerPinRef: could not add buttons: %s' % e)


def addToExistingCornerPins():
    """Add/refresh the buttons on every CornerPin2D in the current script."""
    for node in nuke.allNodes('CornerPin2D', recurseGroups=True):
        try:
            _ensure_knobs(node)
        except Exception as e:
            nuke.tprint('CornerPinRef: could not add buttons to %s: %s' % (node.name(), e))


nuke.addOnCreate(addCornerPinButtons, nodeClass='CornerPin2D')
