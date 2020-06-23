import bpy

from . import blatools as bla

class BLATOOLS_PT_PropertiesActionObject(bpy.types.Panel):
    """Object properties panel to select linked action"""
    bl_label = "Action"
    bl_idname = "OBJECT_PT_actions"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        obj = context.active_object
        layout = self.layout

        row = layout.row(align=True)
        if obj.animation_data:
            row.template_ID(obj.animation_data, "action")
            if not obj.animation_data.action:
                obj_clear = row.operator('object.animation_data_init', text="Clear Animation Data", icon='X')
                obj_clear.for_data = False
                obj_clear.clear = True
        else:
            obj_init = row.operator('object.animation_data_init', icon='ANIM_DATA')
            obj_init.for_data = False
            obj_init.clear = False

class BLATOOLS_PT_PropertiesActionData(bpy.types.Panel):
    """Object Data properties panel to select linked action"""
    bl_label = "Action"
    bl_idname = "DATA_PT_actions"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return not context.active_object.type == 'EMPTY'

    def draw(self, context):
        data = context.active_object.data
        layout = self.layout

        row = layout.row(align=True)
        if data.animation_data:
            row.template_ID(data.animation_data, "action")
            if not data.animation_data.action:
                data_clear = row.operator('object.animation_data_init', text="Clear Animation Data", icon='X')
                data_clear.for_data = True
                data_clear.clear = True
        else:
            data_init = row.operator('object.animation_data_init', icon='ANIM_DATA')
            data_init.for_data = True
            data_init.clear = False

class BLATOOLS_PT_ItemActionsPanel(bpy.types.Panel):
    """Viewport Actions Panel"""
    bl_category = "Item"
    bl_label = "Actions"
    bl_idname = "BLATOOLS_PT_actions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 90

    @classmethod
    def poll(cls, context):
        return context.active_object

    def draw(self, context):
        obj = context.active_object
        layout = self.layout

        # Object action
        row = layout.row(align=True)
        if obj.animation_data:
            row.template_ID(obj.animation_data, "action")
            if not obj.animation_data.action:
                obj_clear = row.operator('object.animation_data_init', text="Clear Object Animation", icon='X')
                obj_clear.for_data = False
                obj_clear.clear = True
        else:
            obj_init = row.operator('object.animation_data_init', text="Initialize Object Animation", icon='ANIM_DATA')
            obj_init.for_data = False
            obj_init.clear = False
        
        # Data action
        if not context.active_object.type == 'EMPTY':
            row = layout.row(align=True)
            if obj.data.animation_data:
                row.template_ID(obj.data.animation_data, "action")
                if not obj.data.animation_data.action:
                    data_clear = row.operator('object.animation_data_init', text="Clear Object Animation", icon='X')
                    data_clear.for_data = True
                    data_clear.clear = True
            else:
                data_init = row.operator('object.animation_data_init', text="Initialize Data Animation", icon='ANIM_DATA')
                data_init.for_data = True
                data_init.clear = False

class BLATOOLS_PT_Sceneprep(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Scene Preparation"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 10

    def draw(self,context):
        layout = self.layout
        row = layout.row(align=True)
        lock = row.operator('view3d.scene_objects_lock', text="Lock All Objects", icon='LOCKED')
        lock.lock = True
        unlock = row.operator('view3d.scene_objects_lock', text="", icon='UNLOCKED')
        unlock.lock = False
        row = layout.row(align=True)
        hide = row.operator('view3d.hide_nonproxy_rigs', text="Hide Non-proxy Rigs", icon='GHOST_ENABLED')
        hide.hide = True
        unhide = row.operator('view3d.hide_nonproxy_rigs', text="", icon='GHOST_DISABLED')
        unhide.hide = False

class BLATOOLS_PT_PerformanceTools(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Performance Tools"
    bl_order = 20

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        simplify = context.scene.render.use_simplify
        s_icon = 'CHECKBOX_HLT' if simplify else 'CHECKBOX_DEHLT'
        split = row.split(align=True)
        split.prop(context.scene.render, 'use_simplify', text="Simplify", icon=s_icon, expand=True)
        split.prop(context.scene.render, 'simplify_subdivision', text="Subdiv", emboss=simplify)
        split.prop(context.scene.render, 'simplify_child_particles', text="Particles", emboss=simplify)
        if any(".high" in col.name or ".mid" in col.name or ".low" in col.name for col in bpy.data.collections):
            row = layout.row()
            row.label(text="Asset Quality (Selection/Global)")
            box = layout.box()
            row = box.row(align=True)
            low_sel = row.operator('view3d.asset_level_set',text="Low",icon='ALIASED')
            low_sel.asset_level = 'LOW'
            low_sel.selected = True
            mid_sel = row.operator('view3d.asset_level_set',text="Mid",icon='ANTIALIASED')
            mid_sel.asset_level = 'MID'
            mid_sel.selected = True
            high_sel = row.operator('view3d.asset_level_set',text="High",icon='MATERIAL')
            high_sel.asset_level = 'HIGH'
            high_sel.selected = True
            if not context.selected_objects:
                row.enabled = False
            row = box.row(align=True)
            low_all = row.operator('view3d.asset_level_set',text="Low",icon='SHADING_BBOX')
            low_all.asset_level = 'LOW'
            low_all.selected = False
            mid_all = row.operator('view3d.asset_level_set',text="Mid",icon='MATPLANE')
            mid_all.asset_level = 'MID'
            mid_all.selected = False
            high_all = row.operator('view3d.asset_level_set',text="High",icon='TEXTURE_DATA')
            high_all.asset_level = 'HIGH'
            high_all.selected = False

class BLATOOLS_PT_CameraTools(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera Tools"
    bl_order = 30
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return bla.camera_get(context)

    def draw(self,context):
        cam = bla.camera_get(context)
        layout = self.layout

        # Passepartout
        split = layout.split(align=True)

        # 0%
        row = split.row(align=True)
        passepartout_000 = row.operator(
            'view3d.camera_passepartout_set',
            text="PP: 0%",
            icon='PIVOT_BOUNDBOX'
        )
        passepartout_000.alpha = 0.0
        if cam.passepartout_alpha == 0.0:
            row.enabled = False

        # 50%
        row = split.row(align=True)
        passepartout_050 = row.operator(
            'view3d.camera_passepartout_set',
            text="50%", icon='CLIPUV_HLT'
        )
        passepartout_050.alpha = 0.5
        if cam.passepartout_alpha == 0.5:
            row.enabled = False

        # 100%
        row = split.row(align=True)
        passepartout_100 = row.operator(
            'view3d.camera_passepartout_set',
            text="100%",
            icon='CLIPUV_DEHLT'
        )
        passepartout_100.alpha = 1.0
        if cam.passepartout_alpha == 1.0:
            row.enabled = False

        # Camera guides
        layout.row().operator('view3d.camera_guides_set',text="Camera Guides",icon='CON_CAMERASOLVER')
        if len(cam.background_images) > 0:
            row = layout.row()
            bg_icon = 'RESTRICT_VIEW_OFF' if cam.show_background_images else 'RESTRICT_VIEW_ON'
            row.prop(cam, 'show_background_images', text="Show Background", icon=bg_icon, expand=True)

class BLATOOLS_PT_MotionPaths(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Motion Paths"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 40

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.operator('pose.motionpath_auto',text="Create",icon='TRACKING')
        if context.mode == 'POSE':
            row.operator('pose.paths_update',text="Update",icon='PHYSICS')
            row.operator('pose.paths_clear',text="Clear",icon='PANEL_CLOSE')
        else:
            row.operator('object.paths_update',text="Update",icon='PHYSICS')
            row.operator('object.paths_clear',text="Clear",icon='PANEL_CLOSE')

class BLATOOLS_PT_TransformHelpers(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Transform Helpers"
    bl_order = 50

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.operator('object.transform_store', icon='ORIENTATION_CURSOR')
        row.operator('object.transform_apply', icon='GIZMO')

class BLATOOLS_PT_ViewportAlpha(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Viewport Alpha"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 60

    def draw(self,context):
        blatools = context.window_manager.blatools
        layout = self.layout

        box = layout.box()
        row = box.row()
        if blatools.collection_alpha_collection:
            alpha_text = blatools.collection_alpha_collection
            alpha_icon = 'GROUP'
        else:
            alpha_text = "Select Collection"
            alpha_icon = 'DOWNARROW_HLT'
        row.operator('blatools.collection_alpha_select',text=alpha_text,icon=alpha_icon)
        row = box.row()
        row.prop(blatools, 'collection_alpha',slider=True)
        row = box.row()
        row.operator('blatools.collection_alpha_reset',text='Reset All Alphas',icon='HIDE_OFF')

class BLATOOLS_PT_SelectionTools(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Selection Tools"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 70

    def draw(self,context):
        blatools = context.window_manager.blatools
        layout = self.layout
        row = layout.row(align=True)
        row.operator('pose.armatures_pose_toggle',text="Toggle Armatures",icon='OUTLINER_DATA_ARMATURE')
        if blatools.armature_toggle_selection:
            selection_icon = 'RESTRICT_SELECT_OFF'
        else:
            selection_icon = 'RESTRICT_SELECT_ON'
        row.prop(blatools, 'armature_toggle_selection',text="",icon=selection_icon)
        if blatools.armature_toggle_hide:
            hide_icon = 'HIDE_ON'
        else:
            hide_icon = 'HIDE_OFF'
        row.prop(blatools, 'armature_toggle_hide',text="",icon=hide_icon)
        row = layout.row()
        row.operator('pose.orientation_parent',text="Parent Orientation",icon='ORIENTATION_LOCAL')

class BLATOOLS_PT_SelectionSetsOptions(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Selection Sets Options"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 80

    def draw(self,context):
        blatools = context.window_manager.blatools
        layout = self.layout
        row = layout.row(align=True)
        row.prop(blatools, 'selection_sets_new_name', text="New")
        row.operator('blatools.selection_sets_name_clear', text="", icon='X')
        row.emboss = 'NONE'
        row = layout.row()
        row.prop(blatools, 'selection_sets_icons')
        sel_set_create = row.operator('blatools.selection_sets_create',text="Create",icon='PLUS')
        sel_set_create.selection_set = blatools.selection_sets_new_name
        sel_set_create.icon = blatools.selection_sets_icons

        box = layout.box()
        row = box.row()
        row.prop(blatools, 'selection_sets_warnings', icon='ERROR')
        row.prop(blatools, 'selection_sets_edit', icon='GREASEPENCIL')
        row = box.row()
        filter_text = "Filter: "
        if blatools.selection_sets_filter_rig == 'ACTIVE':
            filter_text += "Active Rig"
            filter_icon = 'OUTLINER_OB_ARMATURE'
        elif blatools.selection_sets_filter_rig == 'ALL':
            filter_text += "All Rigs"
            filter_icon = 'ORIENTATION_GLOBAL'
        elif blatools.selection_sets_filter_rig == 'SOURCE':
            filter_text += "Source Rig"
            filter_icon = 'HEART'
        else:
            filter_text += blatools.selection_sets_filter_rig
            filter_icon = 'ARMATURE_DATA'
        row.operator('blatools.selection_sets_filter', text=filter_text, icon=filter_icon)
        row = box.row()
        row.prop(blatools, 'selection_sets_make_active', text="Activate")

class BLATOOLS_PT_SelectionSets(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Selection Sets"
    bl_order = 90

    @classmethod
    def poll(cls, context):
        return 'blatools_selection_sets' in context.scene

    def draw(self,context):
        blatools = context.window_manager.blatools
        layout = self.layout      
        length = len(context.scene['blatools_selection_sets'])
        sorted_sets = [None] * len(context.scene['blatools_selection_sets'])
        for sel_enum in context.scene['blatools_selection_sets']:
            sorted_sets[context.scene['blatools_selection_sets'][sel_enum]['position']] = sel_enum
        
        for sel_set in sorted_sets:
            i = dict(context.scene['blatools_selection_sets'][sel_set])['position']
            row = layout.row(align=True)
            sel_set_icon = dict(context.scene['blatools_selection_sets'][sel_set])['icon']
            if blatools.selection_sets_edit:
                sel_set_list = row.operator('blatools.selection_sets_list',text="", icon='INFO')
                sel_set_list.selection_set = sel_set
                sel_set_update_icon = row.operator('blatools.selection_sets_update_icon',text="", icon=sel_set_icon)
                sel_set_update_icon.selection_set = sel_set
                sel_set_select = row.operator('pose.selection_sets_select',text=sel_set)
                sel_set_select.position = i
                sel_set_select.clear = True
                sel_set_select.select = True
                if i + 1 < length:
                    sel_set_move_down = row.operator('blatools.selection_sets_reorder',text="", icon='SORT_ASC')
                    sel_set_move_down.up = False
                    sel_set_move_down.position = i
                if i > 0:
                    sel_set_move_up = row.operator('blatools.selection_sets_reorder',text="", icon='SORT_DESC')
                    sel_set_move_up.up = True
                    sel_set_move_up.position = i
                sel_set_update = row.operator('blatools.selection_sets_update',text="",icon='CON_ROTLIMIT')
                sel_set_update.selection_set = sel_set
                sel_set_delete = row.operator('blatools.selection_sets_delete',text="",icon='CANCEL')
                sel_set_delete.selection_set = sel_set
            else:
                sel_set_select = row.operator('pose.selection_sets_select',text=sel_set,icon=sel_set_icon)
                sel_set_select.position = i
                sel_set_select.clear = True
                sel_set_select.select = True
                sel_set_select = row.operator('pose.selection_sets_select',text="",icon='SELECT_EXTEND')
                sel_set_select.position = i
                sel_set_select.clear = False
                sel_set_select.select = True
                sel_set_select = row.operator('pose.selection_sets_select',text="",icon='SELECT_SUBTRACT')
                sel_set_select.position = i
                sel_set_select.clear = False
                sel_set_select.select = False