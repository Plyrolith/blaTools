import bpy
import copy
import re
import unicodedata
import mathutils

def ui_redraw():
    """Forces blender to redraw its UI.
    Returns: None.
    """
    for screen in bpy.data.screens:
        for area in screen.areas:
            area.tag_redraw()

def string_clean(string, dot=False):
    """Cleans a string, replacing all special characters with underscores.
    Also attempts to replace local special characters with simplified standard ones
    and removes double underscores.
    Returns: String.
    """
    tmpstring = ""
    for char in string.replace("ß","ss"):
        desc = unicodedata.name(char)
        cutoff = desc.find(' WITH ')
        if cutoff != -1:
            desc = desc[:cutoff]
            try:
                char = unicodedata.lookup(desc)
            except KeyError:
                pass  # removing "WITH ..." produced an invalid name
        tmpstring += char
    if dot:
        allowed = '[^A-Za-z0-9.]+'
    else:
        allowed = '[^A-Za-z0-9]+'
    tmpstring = re.sub(allowed, '_', tmpstring).lower().lstrip("_").rstrip("_")
    return re.sub('\_\_+', '*', tmpstring)

def hide_noneproxy_rigs(context, hide=True):
    for obj in context.scene.objects:
        if obj.type == 'ARMATURE':
            if obj.library:
                obj.hide_viewport = hide

def camera_get(context):
    space = context.space_data
    if space.use_local_camera and space.camera and space.camera.type == 'CAMERA':
        cam = space.camera.data
    elif context.scene.camera:
        cam = context.scene.camera.data
    else:
        cam = None
    return cam

def camera_passepartout_set(context, alpha):
    cam = camera_get(context)
    cam.show_passepartout = True
    cam.passepartout_alpha = alpha

def camera_guides_set(context, guide):
    cam = camera_get(context)
    if guide == 'SHOW_COMPOSITION_CENTER':
        if cam.show_composition_center:
            cam.show_composition_center = False
        else:
            cam.show_composition_center = True
    elif guide == 'SHOW_COMPOSITION_CENTER_DIAGONAL':
        if cam.show_composition_center_diagonal:
            cam.show_composition_center_diagonal = False
        else:
            cam.show_composition_center_diagonal = True
    elif guide == 'SHOW_COMPOSITION_THIRDS':
        if cam.show_composition_thirds:
            cam.show_composition_thirds = False
        else:
            cam.show_composition_thirds = True
    elif guide == 'SHOW_COMPOSITION_GOLDEN':
        if cam.show_composition_golden:
            cam.show_composition_golden = False
        else:
            cam.show_composition_golden = True
    elif guide == 'SHOW_COMPOSITION_GOLDEN_TRIA_A':
        if cam.show_composition_golden_tria_a:
            cam.show_composition_golden_tria_a = False
        else:
            cam.show_composition_golden_tria_a = True
    elif guide == 'SHOW_COMPOSITION_GOLDEN_TRIA_B':
        if cam.show_composition_golden_tria_b:
            cam.show_composition_golden_tria_b = False
        else:
            cam.show_composition_golden_tria_b = True
    elif guide == 'SHOW_COMPOSITION_HARMONY_TRI_B':
        if cam.show_composition_harmony_tri_b:
            cam.show_composition_harmony_tri_b = False
        else:
            cam.show_composition_harmony_tri_b = True
    elif guide == 'SHOW_COMPOSITION_HARMONY_TRI_A':
        if cam.show_composition_harmony_tri_a:
            cam.show_composition_harmony_tri_a = False
        else:
            cam.show_composition_harmony_tri_a = True

def motionpaths_auto(context, use_tails=False, use_preview_range=True):
    if use_preview_range and context.scene.use_preview_range:
        start = context.scene.frame_preview_start
        end = context.scene.frame_preview_end
    else:
        start = context.scene.frame_start
        end = context.scene.frame_end
    if context.mode == 'POSE':
        bpy.ops.pose.paths_calculate(
            start_frame=start,
            end_frame=end,
            bake_location='TAILS' if use_tails else 'HEADS'
        )
    else:
        bpy.ops.object.paths_calculate(
            start_frame=start,
            end_frame=end
        )

################################
## FCURVE CHECK FOR BONE NAME ##
################################

def transform_store(
            context,
            target='CURSOR',
            keyframes=False,
            range_min=1,
            range_max=250,
            trail=False
        ):
    blatools = context.window_manager.blatools
    scene = context.scene
    obj = context.active_object
    name = obj.name
    if context.mode == 'POSE' and context.active_pose_bone:
        name += "_" + context.active_pose_bone.name

    def matrix(context):
        obj = context.active_object
        matrix_obj = mathutils.Matrix(obj.matrix_world)
        if context.mode == 'POSE' and context.active_pose_bone:
            return matrix_obj @ context.active_pose_bone.matrix
        else:
            return matrix_obj

    # Copy
    if target == 'STORE':
        index = 0
        for v in matrix(context):
            for f in v:
                blatools.transform_tmp[index] = f
                index += 1

    # Cursor
    if target == 'CURSOR':
        scene.cursor.matrix = matrix(context)
    
    # Empty
    elif target == 'EMPTY':

        # Keyframes
        keys = []
        if keyframes and hasattr(obj.animation_data, 'action') and obj.animation_data.action:
            action = obj.animation_data.action
            keys = []
            for fc in action.fcurves:
                if fc.data_path.endswith('location') or fc.data_path.endswith('rotation') or fc.data_path.endswith('scale'):
                    for kp in fc.keyframe_points:
                        f = int(kp.co[0])
                        if f <= range_max and f >= range_min and f not in keys:
                            keys.append(kp.co[0])

            # Trail
            if trail:
                frame_current = scene.frame_current
                for f in keys:
                    scene.frame_set(f)
                    empty = bpy.data.objects.new('TRF-' + name + "_f" + str(int(f)).zfill(4), None)
                    scene.collection.objects.link(empty)
                    empty.matrix_world = matrix(context)
                    empty["blatools_transform"] = 1
                scene.frame_set(frame_current)

            # No Trail
            else:
                empty = bpy.data.objects.new('TRF-' + name, None)
                scene.collection.objects.link(empty)
                empty["blatools_transform"] = 1

                # Keyframes Action
                if len(keys) > 1:
                    group = 'Object Transforms'
                    frame_current = scene.frame_current
                    for f in keys:
                        scene.frame_set(f)
                        empty.matrix_world = matrix(context)
                        empty.keyframe_insert('location', frame=f, group=group)
                        empty.keyframe_insert('rotation_euler', frame=f, group=group)
                        empty.keyframe_insert('scale', frame=f, group=group)
                    scene.frame_set(frame_current)
            
        # Simple empty
        else:
            empty = bpy.data.objects.new('TRF-' + name, None)
            scene.collection.objects.link(empty)
            empty.matrix_world = matrix(context)

#####################################################
## OBJECT CONSTRAINTS? SELEKTOR, MULTI FRAME APPLY ##
#####################################################

def transform_apply(context, source):
    blatools = context.window_manager.blatools

    def apply(context, m):
        if context.mode == 'POSE' and context.active_pose_bone:
            b = context.active_pose_bone

            # Object matrix
            matrix_obj = mathutils.Matrix(context.active_object.matrix_world)

            # Bone rest matrix
            matrix_orig = mathutils.Matrix(b.bone.matrix_local)
            matrix_orig.resize_4x4()

            # Current absolute pose transform matrix
            matrix = mathutils.Matrix(b.matrix)

            # Local bone transforms
            matrix_basis = mathutils.Matrix(b.matrix_basis)

            # Calculate ONLY transforms (+ parenting) in world
            matrix_transforms = matrix_orig @ matrix_basis

            # Calculate ONLY constraints matrix
            matrix_constraints = matrix @ matrix_transforms.inverted()

            # Apply all matrices for new transforms
            m_applied = matrix_constraints.inverted() @ matrix_obj.inverted() @ m

            context.active_pose_bone.matrix = m_applied
        else:
            context.active_object.matrix_world = m

    # Store
    if source == 'STORE':
        m = mathutils.Matrix()
        t = blatools.transform_tmp
        c = 0
        while c < 16:
            col = int(c / 4)
            row = int(c % 4)
            m[col][row] = t[c]
            c += 1
        apply(context, m)

    # Cursor
    elif source == 'CURSOR':
        apply(context, context.scene.cursor.matrix) 

def scene_objects_lock(scene, lock=True):
    for obj in scene.objects:
        obj.lock_location[0] = lock
        obj.lock_location[1] = lock
        obj.lock_location[2] = lock
        obj.lock_rotation_w = lock
        obj.lock_rotation[0] = lock
        obj.lock_rotation[1] = lock
        obj.lock_rotation[2] = lock
        obj.lock_scale[0] = lock
        obj.lock_scale[1] = lock
        obj.lock_scale[2] = lock

def asset_level_set(context, asset_level, selected=True):

    def collections_exclude(collection, name, exclude=True, collections=[]):
        for child in collection.children:
            if child.name == name:
                child.exclude = exclude
            if child.children:
                collections = (collections_exclude(child, name, exclude, collections))
        return collections
    
    collections_low = []
    collections_mid = []
    collections_high = []
    if selected:
        for obj in context.selected_objects:
            if obj.proxy:
                obj = obj.proxy
            if obj.library:
                lib = obj.library.name
                for collection in bpy.data.collections:
                    if collection.library:
                        if collection.library.name == lib:
                            col = collection.name
                            if col.endswith(".low"):
                                collections_low.append(col.replace(".low",""))
                            if col.endswith(".mid"):
                                collections_mid.append(col.replace(".mid",""))
                            if col.endswith(".high"):
                                collections_high.append(col.replace(".high",""))
    else:
        collections = collections_iterate(context.view_layer.layer_collection, excluded=False)
        for col in collections:
            #if bpy.data.collections[col].library:
            if col.endswith(".low"):
                collections_low.append(col.replace(".low",""))
            if col.endswith(".mid"):
                collections_mid.append(col.replace(".mid",""))
            if col.endswith(".high"):
                collections_high.append(col.replace(".high",""))

    lay_col = bpy.context.view_layer.layer_collection

    if asset_level == 'LOW':
        for mid in collections_mid:
            if mid in collections_low:
                collections_exclude(lay_col,mid+".mid",True)
                collections_exclude(lay_col,mid+".low",False)
        for high in collections_high:
            if high in collections_low:
                collections_exclude(lay_col,high+".high",True)
                collections_exclude(lay_col,high+".low",False)
            elif high in collections_mid:
                collections_exclude(lay_col,high+".high",True)
                collections_exclude(lay_col,high+".mid",False)
    if asset_level == 'MID':
        for low in collections_low:
            if low in collections_mid:
                collections_exclude(lay_col,low+".low",True)
                collections_exclude(lay_col,low+".mid",False)
        for high in collections_high:
            if high in collections_mid:
                collections_exclude(lay_col,high+".high",True)
                collections_exclude(lay_col,high+".mid",False)
            elif high in collections_low:
                collections_exclude(lay_col,high+".high",True)
                collections_exclude(lay_col,high+".low",False)
    if asset_level == 'HIGH':
        for low in collections_low:
            if low in collections_high:
                collections_exclude(lay_col,low+".low",True)
                collections_exclude(lay_col,low+".high",False)
            elif low in collections_mid:
                collections_exclude(lay_col,low+".low",True)
                collections_exclude(lay_col,low+".mid",False)
        for mid in collections_mid:
            if mid in collections_high:
                collections_exclude(lay_col,mid+".mid",True)
                collections_exclude(lay_col,mid+".high",False)

def selection_sets_select(context, position, select=True, clear=False):
    blatools = context.window_manager.blatools
    missing_list = []
    set_used = None
    for sel_set in context.scene['blatools_selection_sets']:
        if context.scene['blatools_selection_sets'][sel_set]['position'] == position:
            set_used = context.scene['blatools_selection_sets'][sel_set]
            break
    if clear:
        bpy.ops.pose.select_all(action='DESELECT')
    if blatools.selection_sets_filter_rig == 'ALL':
        armatures = []
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                armatures.append(obj.data)
    elif blatools.selection_sets_filter_rig == 'ACTIVE':
        armatures = [bpy.context.active_object.data]
    elif blatools.selection_sets_filter_rig == 'SOURCE':
        if set_used and 'source' in set_used and set_used['source'] in context.scene.objects:
            obj = bpy.data.objects[set_used['source']]
            if obj not in context.selected_objects and context.mode == 'POSE':
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(state=True)
                bpy.ops.object.mode_set(mode='POSE')
            armatures = [obj.data]
        else:
            armatures = [bpy.context.active_object.data]
    else:
        armatures = [bpy.data.objects[blatools.selection_sets_filter_rig].data]

    if set_used:
        for arma in armatures:
            for bone in set_used['bones']:
                bone_name = dict(bone)['name']
                if bone_name in arma.bones:
                    arma.bones[bone_name].select = select
                    if select and blatools.selection_sets_make_active == 'SET' and dict(bone)['active']:
                        arma.bones.active = arma.bones[bone_name]
                else:
                    missing_list.append(arma.name + ": " + bone_name)
    return [ set_used['name'], missing_list ]

def selection_sets_create(context, selection_set, position, icon):
    if 'blatools_selection_sets' not in context.scene:
        context.scene['blatools_selection_sets'] = {}
    bones = []
    if context.active_pose_bone:
        active_name = context.active_pose_bone.name
    else:
        active_name = context.selected_pose_bones[0].name
    for bone in context.selected_pose_bones:
        if bone.name not in (b['name'] for b in bones):
            if bone.name == active_name:
                active = True
            else:
                active = False
            bones.append({
                'name': bone.name,
                'active': active
            })

    context.scene['blatools_selection_sets'][selection_set] = {
        'name': selection_set,
        'icon': icon,
        'source': context.active_object.name,
        'position': position,
        'bones': bones,
    }

def selection_sets_delete(context, selection_set):
    position = context.scene['blatools_selection_sets'][selection_set]['position']
    for sel_set in context.scene['blatools_selection_sets']:
        if dict(context.scene['blatools_selection_sets'][sel_set])['position'] > position:
            context.scene['blatools_selection_sets'][sel_set]['position'] -= 1
    del context.scene['blatools_selection_sets'][selection_set]
    if not context.scene['blatools_selection_sets']:
        del context.scene['blatools_selection_sets']

def selection_sets_reorder(context, up, position):
    for name in dict(context.scene['blatools_selection_sets']):
        if context.scene['blatools_selection_sets'][name]['position'] == position:
            if up:
                context.scene['blatools_selection_sets'][name]['position'] = position - 1
            else:
                context.scene['blatools_selection_sets'][name]['position'] = position + 1
        elif up and context.scene['blatools_selection_sets'][name]['position'] == position - 1:
            context.scene['blatools_selection_sets'][name]['position'] = position
        elif not up and context.scene['blatools_selection_sets'][name]['position'] == position + 1:
            context.scene['blatools_selection_sets'][name]['position'] = position

def armatures_pose_toggle(context,selection=True,hide=True):
    blatools = context.window_manager.blatools
    obj_act = context.view_layer.objects.active
    bpy.ops.object.mode_set(mode='OBJECT')
    if 'armature_toggle_list' not in blatools:
        blatools['armature_toggle_list'] = [obj.name for obj in context.selected_objects]
    if len(context.selected_objects) > 1:
        arma_list = []
        if selection:
            objects = context.selected_objects
        else:
            objects = context.scene.objects
        for obj in objects:
            if obj.type == 'ARMATURE':
                if not obj.library:
                    arma_list.append(obj.name)
                    obj.select_set(state=False)
                    if hide:
                        obj.hide_viewport=True
        blatools['armature_toggle_list'] = arma_list
        obj_act.hide_viewport=False
        obj_act.select_set(state=True)
    else:
        for obj in context.scene.objects:
            if obj.name in blatools['armature_toggle_list']:
                obj.hide_viewport=False
                obj.select_set(state=True)
    bpy.ops.object.mode_set(mode='POSE')

def collection_alpha_reset(context):
    blatools = context.window_manager.blatools
    blatools.collection_alpha = 1.0
    for mat in bpy.data.materials:
        if mat.name.endswith("_blatools_alpha"):
            bpy.data.materials.remove(mat)
    for obj in bpy.data.objects:
        if "blatools_alpha_tmp" in obj:
            obj.color[3] = obj["blatools_alpha_tmp"]
            del obj["blatools_alpha_tmp"]
        if "blatools_image_tmp" in obj:
            obj.use_empty_image_alpha = obj["blatools_image_tmp"]
            del obj["blatools_image_tmp"]
    for mat in bpy.data.materials:
        if mat.is_grease_pencil:
            if "blatools_stroke_tmp" in mat:
                mat.grease_pencil.color[3] = mat["blatools_stroke_tmp"]
                del mat["blatools_stroke_tmp"]
            if "blatools_fill_tmp" in mat:
                mat.grease_pencil.fill_color[3] = mat["blatools_fill_tmp"]
                del mat["blatools_fill_tmp"]
        else:
            if "blatools_alpha_tmp" in mat:
                mat.diffuse_color[3] = mat["blatools_alpha_tmp"]
                del mat["blatools_alpha_tmp"]

def collection_alpha_set(self, context):
    blatools = context.window_manager.blatools
    collection = blatools.collection_alpha_collection
    ghostmat = collection + '_blatools_alpha'
    if not ghostmat in bpy.data.materials:
        bpy.data.materials.new(ghostmat)
    bpy.data.materials[ghostmat].diffuse_color[3] = blatools.collection_alpha
    if collection:
        for obj in bpy.data.collections[collection].all_objects:
            if not 'blatools_alpha_tmp' in obj:
                obj['blatools_alpha_tmp'] = obj.color[3]
            obj.color[3] = blatools.collection_alpha
            if obj.material_slots:
                for slot in obj.material_slots:
                    if slot.material:
                        mat = slot.material
                        if mat is not bpy.data.materials[ghostmat]:
                            if mat.is_grease_pencil:
                                if not 'blatools_stroke_tmp' in mat:
                                    mat['blatools_stroke_tmp'] = mat.grease_pencil.color[3]
                                if not 'blatools_fill_tmp' in mat:
                                    mat['blatools_stroke_tmp'] = mat.grease_pencil.fill_color[3]
                                mat.grease_pencil.color[3] = blatools.collection_alpha
                                mat.grease_pencil.fill_color[3] = blatools.collection_alpha
                            else:
                                if not 'blatools_alpha_tmp' in mat:
                                    mat['blatools_alpha_tmp'] = mat.diffuse_color[3]
                                mat.diffuse_color[3] = blatools.collection_alpha
                    else:
                        try:
                            slot.material = bpy.data.materials[ghostmat]
                        except:
                            None
            else:
                if obj.type is not 'GPENCIL':
                    try:
                        obj.data.materials.append(bpy.data.materials[ghostmat])
                    except:
                        None
            if obj.type == 'EMPTY':
                if obj.empty_display_type == 'IMAGE':
                    if not 'blatools_image_tmp' in obj:
                        obj['blatools_image_tmp'] = obj.use_empty_image_alpha
                    obj.use_empty_image_alpha = True

def collections_iterate(collection, excluded=True, collections=[]):
    if not excluded and not collection.exclude:
        for child in collection.children:
            if child.name not in collections:
                collections.append(child.name)
            if child.children:
                collections = (collections_iterate(child, excluded, collections))
    return collections

def orientation_parent(context):
    '''Create Parent Transform Orientation'''
    # Delete old parent transform
    if context.scene.transform_orientation_slots[0].type.startswith("Parent of "):
        bpy.ops.transform.delete_orientation()

    # Set tool transform to default
    context.scene.transform_orientation_slots[1].type = 'DEFAULT'
    context.scene.transform_orientation_slots[2].type = 'DEFAULT'
    context.scene.transform_orientation_slots[3].type = 'DEFAULT'

    # Parent transform for bones
    active_obj = context.active_object
    if context.mode == 'POSE':
        active = context.active_pose_bone
        if active.parent:

            # Save armature/bone settings
            layers_vis = [layer for layer in active_obj.data.layers]
            for i in range(32):
                active_obj.data.layers[i] = True
            selection = context.selected_pose_bones
            bpy.ops.pose.select_all(action='DESELECT')
            parent_pose = active.parent
            parent_data = active_obj.data.bones[parent_pose.name]
            parent_data_hide = parent_data.hide
            parent_data.hide = False
            parent_data_hide_select = parent_data.hide_select
            parent_data.hide_select = False

            # Make parent active/selected
            parent_data.select = True
            active_obj.data.bones.active = parent_data

            # Create orientation
            bpy.ops.transform.create_orientation(
                name="Parent of " + active.name,
                use=True,
                overwrite=True
            )

            # Restore settings
            bpy.ops.pose.select_all(action='DESELECT')
            active_obj.data.bones.active = active_obj.data.bones[active.name]
            parent_data.hide = parent_data_hide
            parent_data.hide_select = parent_data_hide_select
            for i, layer in enumerate(layers_vis):
                active_obj.data.layers[i] = layer
            for sel in selection:
                active_obj.data.bones[sel.name].select = True

        # If no parent is available, use the armature object's transforms
        else:
            bpy.ops.object.mode_set(mode='OBJECT')
            selection = context.selected_objects
            bpy.ops.object.select_all(action='DESELECT')
            active_obj.select_set(True)

            # Create orientation
            bpy.ops.transform.create_orientation(
                name="Parent of " + active.name,
                use=True,
                overwrite=True
            )

            # Restore settings
            bpy.ops.object.select_all(action='DESELECT')
            for sel in selection:
                sel.select_set(True)
            bpy.ops.object.mode_set(mode='POSE')


    # Parent transform for objects
    elif context.mode == 'OBJECT':

        # Save object settings
        if active_obj.parent:
            parent = active_obj.parent
            selection = context.selected_objects
            parent_hide_viewport = parent.hide_viewport
            parent.hide_viewport = False
            parent_hide_select = parent.hide_select
            parent.hide_select = False

            # Make parent active/selected
            bpy.ops.object.select_all(action='DESELECT')
            parent.select_set(True)
            context.view_layer.objects.active = parent

            # Create orientation
            bpy.ops.transform.create_orientation(
                name="Parent of " + active_obj.name,
                use=True,
                overwrite=True
            )

            # Restore settings
            bpy.ops.object.select_all(action='DESELECT')
            parent.hide_viewport = parent_hide_viewport
            parent.hide_select = parent_hide_select
            for sel in selection:
                sel.select_set(True)
            context.view_layer.objects.active = active_obj
        
        else:
            context.scene.transform_orientation_slots[0].type = 'GLOBAL'
