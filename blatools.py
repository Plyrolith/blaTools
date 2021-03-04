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

#########################
## TRAIL IN COLLECTION ##
#########################

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

    def fcurve_check(context, fcurve):
        obj = context.active_object
        if context.mode == 'POSE' and context.active_pose_bone:
            b = 'pose.bones["' + context.active_pose_bone.name + '"].'
            data_paths = (
                b + 'location',
                b + 'rotation_euler',
                b + 'rotation_quaternion',
                b + 'rotation_euler',
                b + 'rotation_axis_angle',
                b + 'scale'
            )
        else:
            data_paths = (
                'location',
                'rotation_euler',
                'scale'
            )
        return fcurve.data_path.endswith(data_paths)
    
    def empty(context, matrix, name, size=0.1):
        empty = bpy.data.objects.new('TRF-' + name, None)
        context.scene.collection.objects.link(empty)
        empty.matrix_world = matrix
        empty.empty_display_size = size
        empty["blatools_transform"] = 1
        empty["blatools_transform_object"] = context.active_object.name
        empty["blatools_transform_bone"] = context.active_pose_bone.name
        empty["blatools_transform_frame"] = context.scene.frame_current
        return empty

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
                if fcurve_check(context, fc):
                    for kp in fc.keyframe_points:
                        f = int(kp.co[0])
                        if f <= range_max and f >= range_min and f not in keys:
                            keys.append(kp.co[0])

            # Trail
            if trail:
                frame_current = scene.frame_current
                for f in keys:
                    scene.frame_set(f)
                    name_f = name + "_f" + str(int(f)).zfill(4)
                    empty(context, matrix(context), name_f)
                scene.frame_set(frame_current)

            # No Trail
            else:
                empty = empty(context, matrix(context), name)

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
            empty(context, matrix(context), name)

#####################################################
## OBJECT CONSTRAINTS? SELEKTOR, MULTI FRAME APPLY ##
#####################################################

def transform_paste(context, source):
    blatools = context.window_manager.blatools

    def apply(context, m):
        obj = context.active_object
        if context.mode == 'POSE' and context.active_pose_bone:
            b = context.active_pose_bone

            #######################################################
            ## To properly calculate the necessary transforms,   ##
            ## we need to figure out the current matrix provided ##
            ## by constraints and then add the difference only.  ##
            #######################################################

            # Object matrix
            matrix_obj = mathutils.Matrix(obj.matrix_world)
            
            # Parent bone matrix
            if b.parent:
                matrix_parent_loc = mathutils.Matrix(b.parent.bone.matrix_local)
                matrix_parent_abs = mathutils.Matrix(b.parent.matrix)
                matrix_parent = matrix_parent_abs @ matrix_parent_loc.inverted()
            else:
                matrix_parent = mathutils.Matrix()

            # Bone rest matrix
            matrix_loc = mathutils.Matrix(b.bone.matrix_local)
            matrix_loc.resize_4x4()

            # Current absolute pose transform matrix
            matrix = mathutils.Matrix(b.matrix)

            # Local bone transforms
            matrix_basis = mathutils.Matrix(b.matrix_basis)

            # Calculate ONLY transforms (+ parenting) in world
            matrix_transforms = matrix_loc @ matrix_basis

            # Calculate ONLY constraints matrix
            matrix_constraints = matrix @ matrix_transforms.inverted() @ matrix_parent.inverted()

            # Apply all matrices for new transforms
            b.matrix = matrix_constraints.inverted() @ matrix_obj.inverted() @ m

        else:
            ### NOT WORKING YET
            '''
            if obj.parent:
                p = obj.parent
                matrix_parent_obj = mathutils.Matrix(p.matrix_world)
                if obj.parent_type == 'BONE':
                    b = p.pose.bones[obj.parent_bone]
                    matrix_b_channel = mathutils.Matrix(b.matrix_channel)
                    matrix_parent = matrix_parent_obj @ matrix_b_channel
                else:
                    matrix_parent = matrix_parent_obj
            else:
                matrix_parent = mathutils.Matrix()

            # Object transforms
            matrix_world = mathutils.Matrix(obj.matrix_world)

            # Object transforms
            matrix_basis = mathutils.Matrix(obj.matrix_basis)

            # All but object transforms
            matrix_pre = matrix_world @ matrix_basis.inverted()

            # Parent inverse, constraints, object transforms
            matrix_local = mathutils.Matrix(obj.matrix_local)

            # Saved offset from parenting
            matrix_parent_inverse = mathutils.Matrix(obj.matrix_parent_inverse) 

            # Constraints ONLY
            matrix_constraints = matrix_local @ matrix_basis.inverted()

            # Apply all matrices for new transforms
            obj.matrix_basis = m @ matrix_pre.inverted() @ matrix_parent_inverse
            '''
            obj.matrix_world = m


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
