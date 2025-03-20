import bpy
import os

def convert_glb_to_obj(glb_filepath, obj_filepath):
    """
    Converts a GLB file to an OBJ file using Blender's Python API (bpy).

    Args:
        glb_filepath: The full path to the input GLB file.
        obj_filepath: The full path to the output OBJ file (where it will be saved).
    """
    try:
        # Clear existing objects in the scene (important for repeated use)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        # Import the GLB file
        bpy.ops.import_scene.gltf(filepath=glb_filepath)

        # Select all imported objects
        bpy.ops.object.select_all(action='SELECT')

        # Export as OBJ
        bpy.ops.export_scene.obj(
            filepath=obj_filepath,
            use_selection=True,  # Only export selected objects
            use_animation=False,  # Don't export animation data
            use_materials=True,  # Export materials (important!)
            use_triangles=True, # Convert to triangles
            use_normals=True,
            use_uvs = True,
            path_mode='COPY' #Make sure materials are embedded correctly
        )

        print(f"Successfully converted '{glb_filepath}' to '{obj_filepath}'")
        return True

    except Exception as e:
        print(f"Error converting '{glb_filepath}': {e}")
        return False



def batch_convert_glb_to_obj(input_folder, output_folder):
    """
    Converts all GLB files in a folder to OBJ files in another folder.

    Args:
        input_folder: The path to the folder containing the GLB files.
        output_folder: The path to the folder where the OBJ files will be saved.
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".glb"):
            glb_path = os.path.join(input_folder, filename)
            obj_filename = os.path.splitext(filename)[0] + ".obj"  # Change extension to .obj
            obj_path = os.path.join(output_folder, obj_filename)
            convert_glb_to_obj(glb_path, obj_path)


# --- Example Usage ---

# 1. Single File Conversion:
# Make sure to replace these paths with your actual file paths!
# glb_file = "path/to/your/input.glb"
# obj_file = "path/to/your/output.obj"
# convert_glb_to_obj(glb_file, obj_file)


# 2. Batch Conversion (from a folder):
# Replace with your folder paths!
input_directory = "path/to/your/glb_folder"
output_directory = "path/to/your/obj_folder"
batch_convert_glb_to_obj(input_directory, output_directory)


# --- How to Run this Script ---
# 1. Open Blender.
# 2. Go to the "Scripting" tab.
# 3. Create a new text file (or open an existing one).
# 4. Paste this code into the text editor.
# 5. Modify the example usage section (at the bottom) to use your file/folder paths:
#    -  Uncomment either the single file conversion or the batch conversion section.
#    -  Replace the placeholder paths with the actual paths to your files/folders.
# 6. Press Alt+P (or click "Run Script") to execute the script.
# 7.  Check the System Console (Window -> Toggle System Console) for output messages (success or errors).
# 8.  The converted OBJ files will be saved in the specified output location.

# ---Important Notes and Explanations ---

# *  **Blender's Python Environment:** This script MUST be run *within* Blender's Python environment, not from your system's Python interpreter.  See the previous responses for details on how to find Blender's Python version.
# *  **Error Handling:** The `try...except` block handles potential errors during the conversion process and prints error messages to the console.  This is good practice for any script.
# * **Clearing the Scene:** `bpy.ops.object.select_all(action='SELECT')` and `bpy.ops.object.delete(use_global=False)` are important.  They clear any existing objects from the Blender scene before importing the GLB.  This prevents objects from previous conversions from being included in the output.
# * **Import/Export Options:**
#     *  `use_selection=True`:  Ensures that only the imported GLB objects are exported.
#     *   `use_animation=False`: We usually don't need animation data for static meshes.
#     *  `use_materials=True`: This is *very important* for preserving the materials (colors, textures) from the GLB.
#     *   `use_triangles = True`: Ensures the OBJ file contains triangles instead of N-gons, which is more compatible
#     * `use_normals=True`, `use_uvs = True`
# *  **Batch Conversion:** The `batch_convert_glb_to_obj` function iterates through all files in a given folder, checks if they have a `.glb` extension (case-insensitively), and then calls the `convert_glb_to_obj` function for each GLB file.
# * **os.makedirs:**  The batch function also has a check to see if the output directory exists.  If the directory doesn't exist, it will create that directory.
# *  **File Paths:**  Always use *full, absolute file paths* for both the input and output files/folders.  Relative paths can be problematic, especially when running scripts within Blender.
# * **path_mode='COPY':** Copies textures and other data and saves them relative to the .blend file.