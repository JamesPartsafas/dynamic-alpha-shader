bl_info = {
    "name": "Caruncle Generator",
    "author": "James Partsafas",
    "version": "1, 0",
    "blender": (2, 90, 1),
    "location": "View3D > Search > Caruncle Generator",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh"
}


import bpy
from bpy.props import FloatVectorProperty
from bpy.props import FloatProperty
from math import radians


class CaruncleGenerator(bpy.types.Operator):
    bl_idname = "object.new_caruncle"
    bl_label = "Caruncle Generator"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    #Create properties to accept user input
    
    base_color : bpy.props.FloatVectorProperty(
        name = "Base Color",
        description = "The base color.",
        size = 4,
        default = (0.042, 0.016, 0.015, 1.000),
        min = 0.000
        )
        
    specular : FloatProperty(
        name = "Specularity",
        description = "The specularity of the caruncle.",
        default = 0.600,
        min = 0.000
        )
        
    roughness : FloatProperty(
        name = "Roughness",
        description = "The roughness of the caruncle.",
        default = 0.400,
        min = 0.000
        )
    
    vector_multiplication = bpy.props.FloatVectorProperty(
        name = "Shading Falloff",
        description = "Determines how smoothly the shading drops off. Lower values have smoother shading. Higher values cut off abruptly. Changes in X value produce most visible results.",
        size = 3,
        default = (0.400, 0.000, 0.200),
        min = 0.000
        )
        
    vector_mapping_location = bpy.props.FloatVectorProperty(
        name = "Base Shading Offset",
        description = "Determines the base distance to the center of the eye. Changes in X value produce most visible results",
        size = 3,
        default = (-12.0, 0.0, 0.0)
        )
        
    vector_mapping_rotation = bpy.props.FloatVectorProperty(
        name = "Base Caruncle Rotation",
        description = "Determines the orientation of the caruncle. Changes in Y value produce most visible results.",
        size = 3,
        default = (0.0, radians(63.0), 0.0)
        )
    
    solid_coloring : FloatProperty(
        name = "Constant Coloring",
        description = "The base, constant coloring of the caruncle. 0 is recommended.",
        default = 0.0,
        min = 0.0
        )
    
    drop_off_multiplication : FloatProperty(
        name = "Drop-Off Modifier",
        description = "Determines the width of the transition area of the caruncle when shading.",
        default = 0.800,
        min = 0.000
        )
    
    initial_darkness_intensity = bpy.props.FloatVectorProperty(
        name = "Initial Darkness Intensity",
        description = "Determines the initial darkness of the caruncle",
        size = 4,
        default = (0.0, 0.0, 0.0, 1.0),
        min = 0.0
        )
        
    ending_darkness_intensity = bpy.props.FloatVectorProperty(
        name = "Ending Darkness Intensity",
        description = "Determines the darkness of the caruncle near the center of the eye",
        size = 4,
        default = (0.117, 0.117, 0.117, 1.000),
        min = 0.000
        )
        
    multiply_final : FloatProperty(
        name = "Final Scaling",
        description = "Determines the final intensity of the caruncle.",
        default = 1.900,
        min = 0.000
        )
    

    def execute(self, context):
        
        
        #Create Empty for pupil position reference

        bpy.ops.object.empty_add()
        center = bpy.context.active_object
        center.name = 'Eye Center'
        bpy.ops.transform.resize(value = (0.1, 0.1, 0.1))


        #Create Empty for fixed position reference

        bpy.ops.object.empty_add()
        extreme = bpy.context.active_object
        extreme.name = 'Eye Extreme Position'
        bpy.ops.transform.resize(value = (0.1, 0.1, 0.1))
        bpy.ops.transform.translate(value = (0.2, 0.2, 0.2))


        #Create caruncle object with subdivision and shrinkwrap modifiers

        bpy.ops.mesh.primitive_plane_add()
        caruncle = bpy.context.active_object
        caruncle.name = 'Caruncle'

        bpy.ops.object.shade_smooth()

        bpy.ops.transform.resize(value = (0.35, 0.2, 0.2))
        caruncle.rotation_euler[0] += radians(90)


        caruncle.modifiers.new("Caruncle_Subdivision", 'SUBSURF')
        caruncle.modifiers["Caruncle_Subdivision"].subdivision_type = 'CATMULL_CLARK'
        caruncle.modifiers["Caruncle_Subdivision"].levels = 2
        caruncle.modifiers["Caruncle_Subdivision"].render_levels = 2
        caruncle.modifiers["Caruncle_Subdivision"].show_only_control_edges = True


        caruncle.modifiers.new("Caruncle_Wrap", 'SHRINKWRAP')
        caruncle.modifiers["Caruncle_Wrap"].wrap_method = 'NEAREST_SURFACEPOINT'
        caruncle.modifiers["Caruncle_Wrap"].wrap_mode = 'ON_SURFACE'
        caruncle.modifiers["Caruncle_Wrap"].offset = 0.002


        #Create caruncle material

        caruncle_mat = bpy.data.materials.new(name = "Caruncle Material")
        caruncle.data.materials.append(caruncle_mat)

        caruncle_mat.use_nodes = True
        nodes = caruncle_mat.node_tree.nodes

        links = caruncle_mat.node_tree.links


        #Vectors between Empty objects multiplied by a constant
        #to track position of pupil relative to a fixed point

        node_extreme_position = nodes.new(type = 'ShaderNodeTexCoord')
        caruncle_mat.node_tree.nodes["Texture Coordinate"].object = extreme
        node_extreme_position.location = (-2300.0, 100.0)

        node_center_position = nodes.new(type = 'ShaderNodeTexCoord')
        caruncle_mat.node_tree.nodes["Texture Coordinate.001"].object = center
        node_center_position.location = (-2300.0, -175.0)


        node_vector_addition = nodes.new(type = 'ShaderNodeVectorMath')
        node_vector_addition.location = (-2070.0, -175.0)


        node_vector_multiplication = nodes.new(type = 'ShaderNodeVectorMath')
        caruncle_mat.node_tree.nodes["Vector Math.001"].operation = 'MULTIPLY'
        node_vector_multiplication.inputs[1].default_value = self.vector_multiplication
        node_vector_multiplication.location = (-1840.0, -175.0)


        links.new(node_extreme_position.outputs[3], node_vector_addition.inputs[0])
        links.new(node_center_position.outputs[3], node_vector_addition.inputs[1])

        links.new(node_vector_addition.outputs[0], node_vector_multiplication.inputs[0])


        #Vector Mapping with known coordinates

        node_vector_map = nodes.new(type = 'ShaderNodeMapping')
        caruncle_mat.node_tree.nodes["Mapping"].vector_type = 'POINT'
        node_vector_map.inputs[1].default_value = self.vector_mapping_location
        node_vector_map.inputs[2].default_value = self.vector_mapping_rotation
        node_vector_map.location = (-1610.0, 0.0)

        links.new(node_extreme_position.outputs[3], node_vector_map.inputs[0])
        links.new(node_vector_multiplication.outputs[0], node_vector_map.inputs[3])


        #Gradient texturing of caruncle mesh

        node_gradient_texture = nodes.new(type = 'ShaderNodeTexGradient')
        caruncle_mat.node_tree.nodes["Gradient Texture"].gradient_type = 'DIAGONAL'
        node_gradient_texture.location = (-1380.0, 0.0)

        links.new(node_vector_map.outputs[0], node_gradient_texture.inputs[0])


        node_solid_coloring = nodes.new(type = 'ShaderNodeMath')
        caruncle_mat.node_tree.nodes["Math"].operation = 'ADD'
        caruncle_mat.node_tree.nodes["Math"].use_clamp = False
        node_solid_coloring.inputs[1].default_value = self.solid_coloring
        node_solid_coloring.location = (-1150.0, 0.0)

        links.new(node_gradient_texture.outputs[0], node_solid_coloring.inputs[0])


        node_mult_intensity = nodes.new(type = 'ShaderNodeMath')
        caruncle_mat.node_tree.nodes["Math.001"].operation = 'MULTIPLY'
        caruncle_mat.node_tree.nodes["Math.001"].use_clamp = False
        node_mult_intensity.inputs[1].default_value = self.drop_off_multiplication
        node_mult_intensity.location = (-920.0, 0.0)

        links.new(node_solid_coloring.outputs[0], node_mult_intensity.inputs[0])


        #Color ramp and shading adjustment

        node_color_ramp = nodes.new(type = 'ShaderNodeValToRGB')
        caruncle_mat.node_tree.nodes["ColorRamp"].color_ramp.color_mode = 'RGB'
        caruncle_mat.node_tree.nodes["ColorRamp"].color_ramp.interpolation = 'LINEAR'
        node_color_ramp.location = (-690.0, 0.0)

        caruncle_mat.node_tree.nodes["ColorRamp"].color_ramp.elements[0].position = 0.000
        caruncle_mat.node_tree.nodes["ColorRamp"].color_ramp.elements[0].color = self.initial_darkness_intensity

        caruncle_mat.node_tree.nodes["ColorRamp"].color_ramp.elements[1].position = 1.000
        caruncle_mat.node_tree.nodes["ColorRamp"].color_ramp.elements[1].color = self.ending_darkness_intensity


        links.new(node_color_ramp.inputs[0], node_mult_intensity.outputs[0])


        #Convert gradient data to monochrome and apply final intensity scaling

        node_rgb_to_bw = nodes.new(type = 'ShaderNodeRGBToBW')
        node_rgb_to_bw.location = (-410.0, 0.0)

        links.new(node_rgb_to_bw.inputs[0], node_color_ramp.outputs[0])


        node_multiply_final = nodes.new(type = 'ShaderNodeMath')
        caruncle_mat.node_tree.nodes["Math.002"].operation = 'MULTIPLY'
        caruncle_mat.node_tree.nodes["Math.002"].use_clamp = False
        node_multiply_final.inputs[1].default_value = self.multiply_final
        node_multiply_final.location = (-230.0, 0.0)

        links.new(node_multiply_final.inputs[0], node_rgb_to_bw.outputs[0])


        #Final color and alpha

        node_principled_bsdf = nodes.get('Principled BSDF')
        node_principled_bsdf.inputs[0].default_value = self.base_color
        node_principled_bsdf.inputs[5].default_value = self.specular
        node_principled_bsdf.inputs[7].default_value = self.roughness

        links.new(node_principled_bsdf.inputs[18], node_multiply_final.outputs[0])


        material_output = nodes.get("Material Output")

        links.new(node_principled_bsdf.outputs[0], material_output.inputs[0])
      
        
        return {'FINISHED'}
    
    
    #Create space for user input
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


def register():
    bpy.utils.register_class(CaruncleGenerator)


def unregister():
    bpy.utils.unregister_class(CaruncleGenerator)


if __name__ == "__main__":
    register()


    # test call
    
    bpy.ops.object.new_caruncle()
