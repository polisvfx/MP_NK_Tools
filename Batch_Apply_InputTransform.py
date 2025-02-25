import nuke

def apply_input_transform():
    # Get the current color management
    colorMgmt = nuke.root()['colorManagement'].value()
    
    # Get all selected Read nodes
    selected_nodes = [n for n in nuke.selectedNodes() if n.Class() == "Read"]
    
    if not selected_nodes:
        nuke.message("Please select at least one Read node.")
        return
    
    # Get available input transforms based on color management
    input_transforms = []
    
    if colorMgmt == "OCIO":
        import PyOpenColorIO as OCIO
        try:
            # Get OCIO config
            config = OCIO.GetCurrentConfig()
            # Get all available input transforms
            input_transforms = [transform.name for transform in config.getInputTransforms()]
        except:
            nuke.message("Error accessing OCIO config")
            return
    else:
        # Nuke's built-in color management
        input_transforms = ["linear", "sRGB", "rec709", "Cineon", "Gamma1.8", "Gamma2.2", "Panalog", 
                          "REDLog", "ViperLog", "AlexaV3LogC", "PLogLin", "SLog", "SLog2", "SLog3"]
    
    # Create panel with dropdown
    p = nuke.Panel("Apply Input Transform")
    p.addEnumerationPulldown('Input Transform', ' '.join(input_transforms))
    
    if p.show():
        selected_transform = p.value("Input Transform")
        
        # Apply the selected transform to all selected Read nodes
        for node in selected_nodes:
            if colorMgmt == "OCIO":
                node['colorspace'].setValue(selected_transform)
            else:
                node['colorspace'].setValue(selected_transform)
        
        nuke.message(f"Applied {selected_transform} to {len(selected_nodes)} Read node(s)")

# Create the menu entry
# menubar = nuke.menu("Nuke")
# menu = menubar.addMenu("Utilities")
# menu.addCommand("Apply Input Transform to Reads", apply_input_transform)