import bpy

from . import blatools as bla

class blaToolsSettings(bpy.types.PropertyGroup):
    selection_sets_new_name: bpy.props.StringProperty(default="", name="Name")
    selection_sets_icons: bpy.props.EnumProperty(name="Icon",
        items=(
                ('BLANK1', "None", "None", 'BLANK1', 0),
                ('USER', "Torso", "Torso", 'USER', 1),
                ('VIEW_PAN', "Hand", "Hand", 'VIEW_PAN', 2),
                ('MOD_DYNAMICPAINT', "Foot", "Foot", 'MOD_DYNAMICPAINT', 3),
                ('COLORSET_01_VEC', "Red", "Red", 'COLORSET_01_VEC', 4),
                ('COLORSET_03_VEC', "Green", "Green", 'COLORSET_03_VEC', 5),
                ('COLORSET_04_VEC', "Blue", "Blue", 'COLORSET_04_VEC', 6),
                ('COLORSET_07_VEC', "Cyan", "Cyan", 'COLORSET_07_VEC', 7),
                ('COLORSET_11_VEC', "Magenta", "Magenta", 'COLORSET_11_VEC', 8),
                ('COLORSET_09_VEC', "Yellow", "Yellow", 'COLORSET_09_VEC', 9),
                ('COLORSET_10_VEC', "Black", "Black", 'COLORSET_10_VEC', 10)
            ),
        default='BLANK1')
    selection_sets_warnings: bpy.props.BoolProperty(default=True, name="Warnings")
    selection_sets_edit: bpy.props.BoolProperty(default=False, name="Edit")
    selection_sets_filter_rig: bpy.props.StringProperty(default='SOURCE', name="Filter")
    selection_sets_make_active: bpy.props.EnumProperty(name="Make Active",
        items=(
                ('NONE', "None", "Keep active bone", 'SELECT_SET', 0),
                ('SET', "Active Set Bone", "Apply active set bone", 'PIVOT_ACTIVE', 1),
            ),
        default='SET')
    collection_alpha_collection: bpy.props.StringProperty(name="Collection",default="")
    collection_alpha: bpy.props.FloatProperty(name="Collection Alpha",min=0.0, max=1.0, default=1.0, soft_min=0.0, soft_max=1.0, update=bla.collection_alpha_set)
    transform_tmp: bpy.props.FloatVectorProperty(
        name='Transform Store',
        description='Temporary Transform Matrix Storage',
        size=16
    )

bpy.utils.register_class(blaToolsSettings)
bpy.types.WindowManager.blatools = bpy.props.PointerProperty(type=blaToolsSettings, name="blaTools")