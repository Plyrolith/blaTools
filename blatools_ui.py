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
                obj_clear.data = 'OBJECT'
                obj_clear.clear = True
        else:
            obj_init = row.operator('object.animation_data_init', icon='ANIM_DATA')
            obj_init.data = 'OBJECT'
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
                data_clear.data = 'DATA'
                data_clear.clear = True
        else:
            data_init = row.operator('object.animation_data_init', icon='ANIM_DATA')
            data_init.data = 'DATA'
            data_init.clear = False

class BLATOOLS_PT_PropertiesActionMaterial(bpy.types.Panel):
    """Material properties panel to select linked action"""
    bl_label = "Action"
    bl_idname = "MATERIAL_PT_actions"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.active_material

    def draw(self, context):
        mat = context.active_object.active_material
        layout = self.layout

        row = layout.row(align=True)
        if mat.animation_data:
            anim_data = mat.animation_data
            row.template_ID(anim_data, "action")
            if not anim_data.action:
                data_clear = row.operator('object.animation_data_init', text="Clear Material Animation", icon='X')
                data_clear.data = 'MATERIAL'
                data_clear.clear = False
        else:
            data_init = row.operator('object.animation_data_init', text="Initialize Material Animation Data", icon='ANIM_DATA')
            data_init.data = 'MATERIAL'
            data_init.clear = False
        
        row = layout.row(align=True)
        if mat.node_tree.animation_data:
            anim_data = mat.node_tree.animation_data
            row.template_ID(anim_data, "action")
            if not anim_data.action:
                data_clear = row.operator('object.animation_data_init', text="Clear Shader Animation", icon='X')
                data_clear.data = 'SHADER'
                data_clear.clear = False
        else:
            data_init = row.operator('object.animation_data_init', text="Initialize Shader Animation Data", icon='ANIM_DATA')
            data_init.data = 'SHADER'
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
                obj_clear.data = 'OBJECT'
                obj_clear.clear = True
        else:
            obj_init = row.operator('object.animation_data_init', text="Initialize Object Animation", icon='ANIM_DATA')
            obj_init.data = 'OBJECT'
            obj_init.clear = False
        
        # Data action
        if not context.active_object.type == 'EMPTY':
            row = layout.row(align=True)
            if obj.data.animation_data:
                row.template_ID(obj.data.animation_data, "action")
                if not obj.data.animation_data.action:
                    data_clear = row.operator('object.animation_data_init', text="Clear Data Animation", icon='X')
                    data_clear.data = 'DATA'
                    data_clear.clear = True
            else:
                data_init = row.operator('object.animation_data_init', text="Initialize Data Animation", icon='ANIM_DATA')
                data_init.data = 'DATA'
                data_init.clear = False

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
        row.operator('object.transform_paste', icon='GIZMO')

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

class BLATOOLS_PT_AnimationTools(bpy.types.Panel):

    bl_category = "blaTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Animation Tools"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 70

    def draw(self,context):
        layout = self.layout.row().operator('pose.fcurves_stepped', icon='IPO_CONSTANT')

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