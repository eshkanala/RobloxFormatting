import bpy
import os



"""
This script must be run in Blender's scripting workspace. To use the script, follow these steps:

How to use the script, get the required part in the same rig workspace with the r15 rig and the part that we need to change add it in, and make sure all variables are labeled right: 


# --- User Configuration ---
    object_to_prepare = "MyHelmet"  # Your object's name
    rig_to_use = "R6" #Armature Name
    head_bone = "Head"  # Head bone name
    accessoryType = "Hat"
    attachmentName = "HatAttachment"
    decimation_ratio = 0.5  # Optional: Set to None for no decimation
    export_directory = ""  # Optional: Set export path
    
    # UV Unwrapping Method
    unwrap_method = 'SMART_PROJECT'  # 'SMART_PROJECT' or 'UNWRAP'

    # Texture Path (Optional) -  Set to None if you don't want to apply a texture
    texture_file_path = "" # Example: "C:/Textures/helmet_texture.png"
    
    #Material name
    materialName = "MyHelmetMaterial" # The name of the material in Blender.



"""
def prepare_for_roblox(object_name, accessory_type, attachment_name,
                      rig_name="Armature", head_bone_name="Head",
                      apply_scale=True, decimate_ratio=None,
                      export_path="",
                      uv_unwrap_method='SMART_PROJECT',  # Added UV unwrap method
                      texture_path=None,  # Added texture path
                      material_name="RobloxMaterial"):  # Added custom material name
    """
    Prepares a 3D model in Blender for Roblox, handling scaling,
    decimation, rigging, cage creation, basic UV unwrapping,
    basic texture handling, and FBX export.

    Args:
        object_name (str): The name of the object to prepare.
        accessory_type (str):  Roblox AccessoryType (e.g., "Hat", "Hair", "Accessory").
        attachment_name (str): The name of the attachment point (e.g., "HatAttachment").
        rig_name (str, optional): The name of the armature. Defaults to "Armature".
        head_bone_name (str, optional): The name of the head bone. Defaults to "Head".
        apply_scale (bool, optional): Whether to apply scale. Defaults to True.
        decimate_ratio (float, optional): Ratio for decimation (0.0-1.0). None for no decimation.
        export_path (str, optional): Path to export the FBX file. Defaults to the same
                                     directory as the blend file.
        uv_unwrap_method (str, optional): UV unwrap method ('SMART_PROJECT', 'UNWRAP').
                                          Defaults to 'SMART_PROJECT'.
        texture_path (str, optional): Path to the texture image.  None for no texture.
        material_name (str, optional): The name to assign to the created material

    Returns:
        bool: True if successful, False otherwise.
    """

    try:
        # --- 1. Setup and Validation ---
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            raise ValueError(f"Object '{object_name}' not found or is not a mesh.")

        rig = bpy.data.objects.get(rig_name)
        if not rig or rig.type != 'ARMATURE':
            raise ValueError(f"Rig '{rig_name}' not found or is not an armature.")

        if head_bone_name not in rig.data.bones:
            raise ValueError(f"Head bone '{head_bone_name}' not found in the armature.")

        head_bone = rig.data.bones[head_bone_name]
        scene = bpy.context.scene

        # --- 2. Object Mode Operations ---
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')
        if apply_scale:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # --- 3. Decimation (Optional) ---
        if decimate_ratio is not None:
            if not 0.0 <= decimate_ratio <= 1.0:
                raise ValueError("decimate_ratio must be between 0.0 and 1.0")

            decimate_mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_mod.ratio = decimate_ratio
            bpy.ops.object.modifier_apply(modifier="Decimate")

        # --- 4. UV Unwrapping ---
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        if uv_unwrap_method == 'SMART_PROJECT':
            bpy.ops.uv.smart_project()  # Simple and often good enough
        elif uv_unwrap_method == 'UNWRAP':
            bpy.ops.uv.unwrap()  # Basic unwrap
        # Add more unwrapping methods here if needed
        else:
             raise ValueError(f"Invalid uv_unwrap_method: {uv_unwrap_method}")

        bpy.ops.object.mode_set(mode='OBJECT')

        # --- 5. Basic Texture Handling ---
        if texture_path:
            # Check if texture file exists
            if not os.path.exists(texture_path):
                raise FileNotFoundError(f"Texture file not found: {texture_path}")

            # Create material (if it doesn't exist)
            mat = bpy.data.materials.get(material_name)
            if not mat:
                mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
            principled_bsdf = mat.node_tree.nodes["Principled BSDF"]

            # Create image texture node
            tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(texture_path)
            mat.node_tree.links.new(tex_image.outputs["Color"], principled_bsdf.inputs["Base Color"])

            # Assign material to object
            if len(obj.data.materials) > 0:
                obj.data.materials[0] = mat # Overwrite existing material
            else:
                obj.data.materials.append(mat) # Append the material

        # --- 6. Rigging ---
        # Parent to armature with empty groups
        obj.parent = rig
        obj.parent_type = 'OBJECT'
        bpy.ops.object.select_all(action='DESELECT')
        rig.select_set(True)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type='ARMATURE', keep_transform=False)
        bpy.ops.object.select_all(action='DESELECT')

        # Weight Painting
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')

        vg = obj.vertex_groups.get(head_bone_name)
        if vg is None:
            vg = obj.vertex_groups.new(name=head_bone_name)

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        vg.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')

        # --- 7. Cage Creation ---
        def create_cage(cage_name, scale_factor):
            """Creates a cage mesh (InnerCage or OuterCage)."""
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.duplicate()
            cage = bpy.context.active_object
            cage.name = cage_name
            cage.data.name = cage_name
            
            # Scale the Cage Mesh.
            bpy.context.view_layer.objects.active = cage
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
            bpy.ops.object.mode_set(mode='OBJECT')

            #Weight paint the Cage Mesh
            cage.parent = rig
            cage.parent_type = 'OBJECT'  # Ensure object parenting
            bpy.ops.object.select_all(action='DESELECT')
            rig.select_set(True)
            cage.select_set(True)
            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.parent_set(type='ARMATURE', keep_transform=False)
            
            bpy.context.view_layer.objects.active = cage
            vg_cage = cage.vertex_groups.get(head_bone_name)
            if vg_cage is None:
                vg_cage = cage.vertex_groups.new(name=head_bone_name)
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            vg_cage.add(range(len(cage.data.vertices)), 1.0, 'REPLACE')

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

        create_cage("InnerCage", 0.98)
        create_cage("OuterCage", 1.02)

        # --- 8. FBX Export ---
        if not export_path:
            export_path = os.path.dirname(bpy.data.filepath) + "/" + object_name + ".fbx"
        elif os.path.isdir(export_path):
            export_path = os.path.join(export_path, object_name + ".fbx")

        export_dir = os.path.dirname(export_path)
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        rig.select_set(True)
        bpy.data.objects['InnerCage'].select_set(True)
        bpy.data.objects['OuterCage'].select_set(True)


        bpy.ops.export_scene.fbx(
            filepath=export_path,
            use_selection=True,
            apply_scale_options='FBX_SCALE_UNITS',
            add_leaf_bones=False,
            use_armature_deform_only=False,
            bake_anim=False,
            axis_forward='-Z',
            axis_up='Y',
            use_mesh_modifiers = True,
            mesh_smooth_type='FACE',
        )

        print(f"Successfully exported to: {export_path}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # --- User Configuration ---
    object_to_prepare = "MyHelmet"  # Your object's name
    rig_to_use = "R6" #Armature Name
    head_bone = "Head"  # Head bone name
    accessoryType = "Hat"
    attachmentName = "HatAttachment"
    decimation_ratio = 0.5  # Optional: Set to None for no decimation
    export_directory = ""  # Optional: Set export path
    
    # UV Unwrapping Method
    unwrap_method = 'SMART_PROJECT'  # 'SMART_PROJECT' or 'UNWRAP'

    # Texture Path (Optional) -  Set to None if you don't want to apply a texture
    texture_file_path = "" # Example: "C:/Textures/helmet_texture.png"
    
    #Material name
    materialName = "MyHelmetMaterial" # The name of the material in Blender.

    # --- Run ---
    if prepare_for_roblox(object_to_prepare, accessoryType, attachmentName,
                         rig_to_use, head_bone,
                         apply_scale=True, decimate_ratio=decimation_ratio,
                         export_path=export_directory,
                         uv_unwrap_method=unwrap_method,
                         texture_path=texture_file_path,
                         material_name = materialName):
        print("Preparation complete!")
    else:
        print("Preparation failed.")