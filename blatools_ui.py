import bpy

class BA_PT_pipeline_tools_anim_sceneprep(bpy.types.Panel):

    bl_category = "Animation Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Scene Preparation"
    bl_order = 10

    def draw(self,context):
        layout = self.layout
        row = layout.row(align=True)
        lock = row.operator('view3d.scene_objects_lock',text="Lock All Objects",icon='LOCKED')
        lock.lock = True
        unlock = row.operator('view3d.scene_objects_lock',text="",icon='UNLOCKED')
        unlock.lock = False
        row = layout.row()
        row.operator('view3d.hide_nonproxy_rigs',text="Hide Non-proxy Rigs",icon='GHOST_ENABLED')

class BA_PT_pipeline_tools_anim_performance_tools(bpy.types.Panel):

    bl_category = "Animation Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Performance Tools"
    bl_order = 20

    def draw(self,context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.prop(context.scene.render, 'use_simplify')
        row = box.row()
        row.prop(context.scene.render, 'simplify_subdivision',text="Subdiv")
        row.prop(context.scene.render, 'simplify_child_particles',text="Particles")
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

class BA_PT_pipeline_tools_anim_viewport_tools(bpy.types.Panel):

    bl_category = "Animation Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Viewport Tools"
    bl_order = 30

    def draw(self,context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Camera Tools")
        box = layout.box()
        row = box.row(align=True)
        passepartout_000 = row.operator('view3d.camera_passepartout_set',text="PP: 0%",icon='PIVOT_BOUNDBOX')
        passepartout_000.alpha = 0.0
        passepartout_050 = row.operator('view3d.camera_passepartout_set',text="50%",icon='CLIPUV_HLT')
        passepartout_050.alpha = 0.5
        passepartout_100 = row.operator('view3d.camera_passepartout_set',text="100%",icon='CLIPUV_DEHLT')
        passepartout_100.alpha = 1.0
        row = box.row()
        row.operator('view3d.camera_guides_set',text="Camera Guides",icon='CON_CAMERASOLVER')
        row = box.row()
        background_on = row.operator('view3d.camera_background_images',text="Show BG",icon='RESTRICT_VIEW_OFF')
        background_on.show_background_images = True
        background_off = row.operator('view3d.camera_background_images',text="Hide BG",icon='RESTRICT_VIEW_ON')
        background_off.show_background_images = False
        row = layout.row()
        row.label(text="Motionpaths")
        box = layout.box()
        row = box.row(align=False)
        row.operator('pose.motionpath_auto',text="Create",icon='TRACKING')
        row.operator('pose.motionpath_update',text="Update",icon='PHYSICS')
        row.operator('pose.motionpath_clear',text="Clear All",icon='PANEL_CLOSE')

class BA_PT_pipeline_tools_anim_viewport_alpha(bpy.types.Panel):

    bl_category = "Animation Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Viewport Alpha"
    bl_order = 40

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

class BA_PT_pipeline_tools_anim_selection_tools(bpy.types.Panel):

    bl_category = "Animation Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Selection Tools"
    bl_order = 50

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

class BA_PT_pipeline_tools_anim_selection_sets_options(bpy.types.Panel):

    bl_category = "Animation Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Selection Sets Options"
    bl_order = 60

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

class BA_PT_pipeline_tools_anim_selection_sets(bpy.types.Panel):

    bl_category = "Animation Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Selection Sets"
    bl_order = 70

    def draw(self,context):
        blatools = context.window_manager.blatools
        layout = self.layout      
        if 'blatools_selection_sets' in context.scene:
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
                    sel_set_select.deselect = False
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
                    sel_set_select.deselect = False
                    sel_set_select = row.operator('pose.selection_sets_select',text="",icon='SELECT_EXTEND')
                    sel_set_select.position = i
                    sel_set_select.clear = False
                    sel_set_select.deselect = False
                    sel_set_select = row.operator('pose.selection_sets_select',text="",icon='SELECT_SUBTRACT')
                    sel_set_select.position = i
                    sel_set_select.clear = False
                    sel_set_select.deselect = True