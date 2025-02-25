import nuke
# Only import GUI-dependent scripts when in GUI mode
if nuke.GUI:
    # Your GUI-dependent imports
    import CornerPinRef
    import Batch_Apply_InputTransform
    # Add any other GUI-dependent imports her