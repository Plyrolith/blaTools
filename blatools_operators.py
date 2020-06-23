import bpy

from . import blatools as bla

class BLATOOLS_OT_HideNonProxyRigs(bpy.types.Operator):
    """Temporarily Hide all non-Proxy Rigs"""
    bl_idname = 'view3d.hide_nonproxy_rigs'
    bl_label = "Hide non-Proxy Rigs"
    bl_options = {'UNDO'}
    
    hide: bpy.props.BoolProperty(name='Hide', default=True)

    @classmethod
    def poll(cls, context):
        return bpy.data.libraries

    def execute(self, context):
        bla.hide_noneproxy_rigs(context, self.hide)
        return {"FINISHED"}

class BLATOOLS_OT_CameraPassepartoutSet(bpy.types.Operator):
    """Set Passepartout of active camera"""
    bl_idname = 'view3d.camera_passepartout_set'
    bl_label = "Set Passepartout"
    bl_options = {'UNDO'}

    alpha: bpy.props.FloatProperty(default=1.0)

    @classmethod
    def poll(cls, context):
        return context.scene.camera

    def execute(self, context):
        bla.camera_passepartout_set(context, self.alpha)
        return {"FINISHED"}

class BLATOOLS_OT_TransformStore(bpy.types.Operator):
    """Store World Transforms for active Pose Bone or Object"""
    bl_idname = 'object.transform_store'
    bl_label = "Store Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    target: bpy.props.EnumProperty(
        name="Target",
        items=[
            ('STORE', "Store", "Store"),
            ('CURSOR', "Cursor", "Cursor"),
            ('EMPTY', "Empty", "Empty")
        ],
        default='STORE'
    )
    keyframes: bpy.props.BoolProperty(name="Follow Keyframes", default=False)
    range_min: bpy.props.IntProperty(name="Start", default=1)
    range_max: bpy.props.IntProperty(name="End", default=250)
    trail: bpy.props.BoolProperty(name="Create Trail", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone or context.active_object

    def execute(self, context):
        bla.transform_store(
            context,
            self.target,
            self.keyframes,
            self.range_min,
            self.range_max,
            self.trail
        )
        bla.ui_redraw()
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, 'target', expand=True)
        row = layout.row()
        row.prop(self, 'keyframes', icon='DECORATE_KEYFRAME', expand=True)
        if not self.target == 'EMPTY':
            row.enabled = False
        split = layout.split(align=True)
        row = split.row(align=True)
        row.prop(self, 'range_min')
        if not self.target == 'EMPTY' or not self.keyframes:
            row.enabled = False
        row = split.row(align=True)
        row.prop(self, 'range_max')
        if not self.target == 'EMPTY' or not self.keyframes:
            row.enabled = False
        row = layout.row(align=True)
        row.prop(self, 'trail')
        if not self.target == 'EMPTY' or not self.keyframes:
            row.enabled = False

class BLATOOLS_OT_TransformApply(bpy.types.Operator):
    """Apply World Transforms to active Pose Bone or Object"""
    bl_idname = 'object.transform_apply'
    bl_label = "Apply Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    source: bpy.props.EnumProperty(
        name="Source",
        items=[
            ('STORE', "Stored", "Stored"),
            ('CURSOR', "Cursor", "Cursor")
            #('SELECTION', "Selection", "Selection")
        ],
        default='STORE'
    )
    @classmethod
    def poll(cls, context):
        return context.active_pose_bone or context.active_object

    def execute(self, context):
        bla.transform_apply(context, self.source)
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, 'source', expand=True)

class BLATOOLS_OT_MotionpathAuto(bpy.types.Operator):
    """Automatically create motion path for bones or objects"""
    bl_idname = 'pose.motionpath_auto'
    bl_label = "Auto Motion Path"
    bl_options = {'REGISTER', 'UNDO'}

    use_tails: bpy.props.BoolProperty(name="Use Tails")
    use_preview_range: bpy.props.BoolProperty(name="Use Preview Range", default=True)

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones or context.selected_objects

    def execute(self, context):
        bla.motionpaths_auto(context, self.use_tails, self.use_preview_range)
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        if context.mode == 'POSE':
            layout.row().prop(self, 'use_tails')
        if context.scene.use_preview_range:
            layout.row().prop(self, 'use_preview_range')

class BLATOOLS_OT_SceneObjectsLock(bpy.types.Operator):
    """Lock all object transforms for current scene"""
    bl_idname = 'view3d.scene_objects_lock'
    bl_label = "Lock All Object Transforms (Current Scene)"
    bl_options = {'UNDO'}

    lock: bpy.props.BoolProperty(name='Lock', default=True)

    @classmethod
    def poll(cls, context):
        return context.scene.objects

    def execute(self, context):
        bla.scene_objects_lock(context.scene, self.lock)
        return {"FINISHED"}

class BLATOOLS_OT_AssetLevelSet(bpy.types.Operator):
    """Set detail level of linked assets"""
    bl_idname = 'view3d.asset_level_set'
    bl_label = "Set Asset Level"
    bl_options = {'UNDO'}

    asset_level: bpy.props.StringProperty(name="Asset Quality ('LOW', 'MID', 'HIGH')",default='LOW')
    selected: bpy.props.BoolProperty(name="Selected Only",default=True)

    @classmethod
    def poll(cls, context):
        return True
                
    def execute(self, context):
        bla.asset_level_set(context, self.asset_level, self.selected)
        return {"FINISHED"}

class BLATOOLS_OT_CollectionAlphaSelect(bpy.types.Operator):
    """Select collection for viewport alpha manipulation"""
    bl_idname = 'blatools.collection_alpha_select'
    bl_label = "Select Collection for Viewport Alpha"
    bl_options = {'INTERNAL', 'UNDO'}
    bl_property = "enum_collections"

    def collections(self, context):
        collections = []
        for i, c in enumerate(bla.collections_iterate(context.view_layer.layer_collection, excluded=False)):
            collections.append((c, c, c, 'GROUP', i))
        return collections

    enum_collections: bpy.props.EnumProperty(items=collections,default=None)

    @classmethod
    def poll(cls, context):
        return context.view_layer.layer_collection.children
                
    def execute(self, context):
        blatools = context.window_manager.blatools
        blatools.collection_alpha_collection = self.enum_collections
        bla.ui_redraw()
        return {"FINISHED"}
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class BLATOOLS_OT_CollectionAlphaReset(bpy.types.Operator):
    """Reset viewport alpha for all collections"""
    bl_idname = 'blatools.collection_alpha_reset'
    bl_label = "Reset All Collection Viewport Alphas"
    bl_options = {'INTERNAL','UNDO'}
                
    def execute(self, context):
        bla.collection_alpha_reset(context)
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetSelect(bpy.types.Operator):
    """Select bones from selection set"""
    bl_idname = 'pose.selection_sets_select'
    bl_label = "Select Selection Set Bones"
    bl_options = {'UNDO', 'REGISTER'}

    position: bpy.props.IntProperty(name="Position")
    select: bpy.props.BoolProperty(name="Select", default=True)
    clear: bpy.props.BoolProperty(name="New Selection", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'
                
    def execute(self, context):
        blatools = context.window_manager.blatools
        sel_set = bla.selection_sets_select(
            context,
            self.position,
            self.select,
            self.clear
        )
        if sel_set[1] and blatools.selection_sets_warnings:
            def draw(self, context):
                for bone in sel_set[1]:
                    self.layout.label(text=bone, icon='BONE_DATA')
            context.window_manager.popup_menu(draw, title="Bones not found:", icon='ERROR')
        if sel_set[0]:
            report = "Set '" + str(sel_set[0]) + "' selected!"
        else:
            report = "Selection set at position " + str(self.position) + " not found."
        self.report({'INFO'}, report)
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetList(bpy.types.Operator):
    """List bones from selection set"""
    bl_idname = 'blatools.selection_sets_list'
    bl_label = "List Selection Set Bones"
    bl_options = {'INTERNAL'}

    selection_set: bpy.props.StringProperty()
                
    def execute(self, context):
        bones = []
        for bone in dict(context.scene['blatools_selection_sets'][self.selection_set])['bones']:
            bones.append(dict(bone)['name'])
        def draw(self, context):
            for bone in bones:
                self.layout.label(text=bone, icon='BONE_DATA')
        context.window_manager.popup_menu(draw, title="Bones in Set:", icon='GROUP_BONE')
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetCreate(bpy.types.Operator):
    """Create selection set from selected bones"""
    bl_idname = 'blatools.selection_sets_create'
    bl_label = "Create Selection Set"
    bl_options = {'INTERNAL', 'UNDO'}

    selection_set: bpy.props.StringProperty()
    icon: bpy.props.StringProperty(default='BLANK1')

    @classmethod
    def poll(cls, context):
        blatools = context.window_manager.blatools
        if context.mode == 'POSE':
            if blatools.selection_sets_new_name:
                if 'blatools_selection_sets' in context.scene:
                    if not blatools.selection_sets_new_name in context.scene['blatools_selection_sets']:
                        return context.selected_pose_bones
                else:
                    return context.selected_pose_bones and context.active_bone
                
    def execute(self, context):
        if 'blatools_selection_sets' in context.scene:
            position = len(context.scene['blatools_selection_sets'])
        else:
            position = 0
        bla.selection_sets_create(context, self.selection_set, position, self.icon)
        bla.ui_redraw()
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetDelete(bpy.types.Operator):
    """Delete selection set"""
    bl_idname = 'blatools.selection_sets_delete'
    bl_label = "Delete Selection Set"
    bl_options = {'UNDO'}

    selection_set: bpy.props.StringProperty()
                
    def execute(self, context):
        bla.selection_sets_delete(context, self.selection_set)
        bla.ui_redraw()
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetIcon(bpy.types.Operator):
    """Set icon for new selection sets"""
    bl_idname = 'blatools.selection_sets_icon'
    bl_label = "Set Icon for New Selection Sets"
    bl_options = {'INTERNAL'}

    icon: bpy.props.StringProperty(default='BLANK1')

    def execute(self, context):
        blatools = context.window_manager.blatools
        blatools.new_icon = self.icon
        bla.ui_redraw()
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetFilter(bpy.types.Operator):
    """Set selection set filter object"""
    bl_idname = 'blatools.selection_sets_filter'
    bl_label = "Set Selection Set Filter"
    bl_options = {'INTERNAL'}
    bl_property = "enum_rigs"

    def rigs(self, context):
        rigs = [
            ('SOURCE', 'Source Rig', 'Source Rig', 'HEART', 0),
            ('ACTIVE', 'Active Rig', 'Active Rig', 'OUTLINER_OB_ARMATURE', 1),
            ('ALL', 'All Rigs', 'All Rigs', 'ORIENTATION_GLOBTL', 2)
        ]
        for i, obj in enumerate(context.scene.objects):
            if obj.type == 'ARMATURE':
                rigs.append((obj.name, obj.name, obj.name, 'ARMATURE_DATA', i + 3))
        return rigs

    enum_rigs: bpy.props.EnumProperty(items=rigs,default=None)

    def execute(self, context):
        blatools = context.window_manager.blatools
        blatools.selection_sets_filter_rig = self.enum_rigs
        bla.ui_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class BLATOOLS_OT_SelectionSetNameClear(bpy.types.Operator):
    """Clear new name field for selection sets"""
    bl_idname = 'blatools.selection_sets_name_clear'
    bl_label = "Clear Selection Set New Name Field"
    bl_options = {'INTERNAL'}
                
    def execute(self, context):
        blatools = context.window_manager.blatools
        blatools.selection_sets_new_name = ""
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetReorder(bpy.types.Operator):
    """Reorder selection set"""
    bl_idname = 'blatools.selection_sets_reorder'
    bl_label = "Reorder Selection Set"
    bl_options = {'INTERNAL', 'UNDO'}

    position: bpy.props.IntProperty()
    up: bpy.props.BoolProperty(default=True)
                
    def execute(self, context):
        bla.selection_sets_reorder(context, self.up, self.position)
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetUpdate(bpy.types.Operator):
    """Update selection set"""
    bl_idname = 'blatools.selection_sets_update'
    bl_label = "Update Selection Set"
    bl_options = {'UNDO'}

    selection_set: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            return context.selected_pose_bones
                
    def execute(self, context):
        position = dict(context.scene['blatools_selection_sets'][self.selection_set])['position']
        icon = dict(context.scene['blatools_selection_sets'][self.selection_set])['icon']
        bla.selection_sets_create(context, self.selection_set, position, icon)
        bla.ui_redraw()
        return {"FINISHED"}

class BLATOOLS_OT_SelectionSetUpdateIcon(bpy.types.Operator):
    """Update selection set icon"""
    bl_idname = 'blatools.selection_sets_update_icon'
    bl_label = "Update Selection Set Icon"
    bl_options = {'INTERNAL', 'UNDO'}

    selection_set: bpy.props.StringProperty()
                
    def execute(self, context):
        blatools = context.window_manager.blatools
        context.scene['blatools_selection_sets'][self.selection_set]['icon'] = blatools.selection_sets_icons
        bla.ui_redraw()
        return {"FINISHED"}

class BLATOOLS_OT_ArmaturesPoseToggle(bpy.types.Operator):
    """Toggle between active/all Armatures in Pose Mode"""
    bl_idname = 'pose.armatures_pose_toggle'
    bl_label = "Toggle Active/all Armatures"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        blatools = context.window_manager.blatools
        bla.armatures_pose_toggle(
            context,
            blatools.armature_toggle_selection,
            blatools.armature_toggle_hide
        )
        return {"FINISHED"}

class BLATOOLS_OT_CameraGuidesSet(bpy.types.Operator):
    """Set scene camera guides"""
    bl_idname = 'view3d.camera_guides_set'
    bl_label = "Set Scene Camera Guides"
    bl_options = {'UNDO'}
    bl_property = "enum_camguides"

    def camguides(self, context):
        cam = bla.camera_get(context)
        if cam:
            guides = [
                ('SHOW_COMPOSITION_CENTER', "Center", "Center", ('CHECKBOX_DEHLT' if not cam.show_composition_center else 'CHECKBOX_HLT'), 0),
                ('SHOW_COMPOSITION_CENTER_DIAGONAL', "Center Diagonal", "Center Diagonal", ('CHECKBOX_DEHLT' if not cam.show_composition_center_diagonal else 'CHECKBOX_HLT'), 1),
                ('SHOW_COMPOSITION_THIRDS', "Thirds", "Thirds", ('CHECKBOX_DEHLT' if not cam.show_composition_thirds else 'CHECKBOX_HLT'), 2),
                ('SHOW_COMPOSITION_GOLDEN', "Golden Ratio", "Golden Ratio", ('CHECKBOX_DEHLT' if not cam.show_composition_golden else 'CHECKBOX_HLT'), 3),
                ('SHOW_COMPOSITION_GOLDEN_TRIA_A', "Golden Triangle A", "Golden Triangle A", ('CHECKBOX_DEHLT' if not cam.show_composition_golden_tria_a else 'CHECKBOX_HLT'), 4),
                ('SHOW_COMPOSITION_GOLDEN_TRIA_B', "Golden Triangle B", "Golden Triangle B", ('CHECKBOX_DEHLT' if not cam.show_composition_golden_tria_b else 'CHECKBOX_HLT'), 5),
                ('SHOW_COMPOSITION_HARMONY_TRI_B', "Harmonious Triangle A", "Harmonious Triangle A", ('CHECKBOX_DEHLT' if not cam.show_composition_harmony_tri_b else 'CHECKBOX_HLT'), 6),
                ('SHOW_COMPOSITION_HARMONY_TRI_A', "Harmonious Triangle B", "Harmonious Triangle B", ('CHECKBOX_DEHLT' if not cam.show_composition_harmony_tri_a else 'CHECKBOX_HLT'), 7)
            ]
        else:
            guides = [("","","")]
        return guides
    
    enum_camguides: bpy.props.EnumProperty(name="Guides", items=camguides)

    @classmethod
    def poll(cls, context):
        return context.scene.camera

    def execute(self, context):
        bla.camera_guides_set(context, self.enum_camguides)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class BLATOOLS_OT_CameraBackgroundImages(bpy.types.Operator):
    """Set scene camera guides"""
    bl_idname = 'view3d.camera_background_images'
    bl_label = "Show/Hide Scene Camera Background Images"
    bl_options = {'UNDO', 'INTERNAL'}

    show_background_images: bpy.props.BoolProperty(name="Show Background Images", default=True)

    @classmethod
    def poll(cls, context):
        return bla.camera_get(context)

    def execute(self, context):
        bla.camera_get(context).show_background_images = self.show_background_images
        return {"FINISHED"}

class BLATOOLS_OT_OrientationParent(bpy.types.Operator):
    """Create custom orientation based on active object's/bone's parent"""
    bl_idname = 'pose.orientation_parent'
    bl_label = "Orientation to Parent"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            return context.active_pose_bone
        elif context.mode == 'OBJECT':
            return context.active_object

    def execute(self, context):
        bla.orientation_parent(context)
        return {"FINISHED"}

class BLATOOLS_OT_AnimationDataInitialize(bpy.types.Operator):
    """Initialize animation data for active object"""
    bl_idname = 'object.animation_data_init'
    bl_label = "Initialize Animation Data"
    bl_options = {'REGISTER', 'UNDO'}

    for_data: bpy.props.BoolProperty(name="Object Data", default=False)
    clear: bpy.props.BoolProperty(name="Clear", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if self.for_data:
            item = context.active_object.data
        else:
            item = context.active_object
        if self.clear:
            item.animation_data_clear()
        else:
            item.animation_data_create()
        return {"FINISHED"}