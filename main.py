import subprocess, datetime, cv2
import os, os.path as osp

import streamlit as st
from utils import *
state = st.session_state
init(state)

#####################################
## STATE VARS
if 'vroot' not in state:
    state.vfolder = vfolder = osp.join(os.getcwd(),"vid")
if 'vids' not in state:
    state.vids = [f for f in os.listdir(vfolder) if osp.isfile(osp.join(vfolder, f))]
if 'sel_vname' not in state:
    state.sel_vname = state.vids[0] if state.vids else ""
if 'sel_vpath' not in state:
    state.sel_vpath = osp.join(vfolder, state.sel_vname) if state.vids else ""
if 'sure_del' not in state: state.sure_del = False
if 'done_del' not in state: state.done_del = False
if 'prep_cut' not in state: state.prep_cut = False
if 'exec_cut' not in state: state.exec_cut = False
if 'done_cut' not in state: state.done_cut = False
if 'fps' not in state: state.fps = 24 #st.number_input('FPS', min_value=1, value=24)
if 'sel_lbs_ids' not in state: state.sel_lbs_ids = []
#####################################


st.title('XDV vid maker')


## SIDE BAR VID SEL
with st.sidebar:
    option = st.selectbox( 'VID SELECTION', ('all', 'original' , 'cut'))
    get_vids(option)
    #state.vids = [f for f in os.listdir(state.vfolder) if osp.isfile(osp.join(state.vfolder, f))]
    state.sel_vname = st.radio(f'ORIGINAL', state.vids )#, index=0 if state.done_cut else state.vids.index(state.sel_vname) if state.sel_vname in state.vids else 0)
    state.sel_vpath = osp.join(state.vfolder, state.sel_vname)
    

## VPLAYER
vdata = open(state.sel_vpath, 'rb')
vbytes = vdata.read()
st.video(vbytes)


## DEL
if st.button('DEL'): state.sure_del = not state.sure_del  
if state.sure_del:
    st.write(f"deleting {state.sel_vpath}")
    if st.button('SURE ?'): 
        del_file(state.sel_vpath)
if state.done_del: 
    st.success(f"{state.sel_vpath} removed")
    state_upd()


## TIMERS
st.header("START TIME")
state.ss = st.text_input(' hh-mm-ss', '00-00-00').replace(" ","").replace(":","-")
st.header("END TIME")
state.t = st.text_input('hh-mm-ss', '00-00-00').replace(" ","").replace(":","-")


## LABELS
d = { 'FIGHT': 'B1', 'SHOOT': 'B2', 'RIOT': 'B4', 'ABUSE': 'B5', 'CARACC': 'B6','EXPLOS': 'G'}
#st.text(str(d).replace("'","").replace("{","").replace("}",""))
st.header("LABELS")
sel_lbs = st.multiselect('1 to 3 labels', list(d.keys()))
sel_lbs_ids = [d[lbl] for lbl in sel_lbs]
sel_lbs_ids.sort()
if 0 < len(sel_lbs_ids) < 3:
    while len(sel_lbs_ids) < 3: sel_lbs_ids.append("0")
state.sel_lbs_ids = sel_lbs_ids

get_newvid_name()
st.write(state.new_vname)


st.header("CUT")
if st.button('prepare'): state.prep_cut = not state.prep_cut 
if state.prep_cut:
    
    if len(sel_lbs_ids) != 3:
        st.error("sel at the min 1 class")
        state.prep_cut = False
        
    elif osp.isfile(state.new_vpath):
        st.error(f"{state.new_vpath} already exists")
        state.prep_cut = False 

    else:
        cmd = cut_video()
        st.write(f'CMD: {cmd}')

    if st.button('execute'): state.exec_cut = True
    if state.exec_cut:
        cmd = cut_video(dr=False)
        
        # Get the video's metadata
        #cap = cv2.VideoCapture(sel_vpath)
        #fps = cap.get(cv2.CAP_PROP_FPS)
        #frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        #duration = frame_count / fps
        #cap.release()
        #st.write(f"{fps} {frame_count} {duration}")
        
if state.done_cut:
    #st.success(f'CUT DON 4 {state.new_vname}')
    state_upd()
