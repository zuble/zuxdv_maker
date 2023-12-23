import subprocess, datetime, cv2
import os, os.path as osp

import streamlit as st

state=None
def init(s):
    global state
    state = s

def state_upd():
    state.sure_del = False
    state.done_del = False
    state.prep_cut = False
    state.exec_cut = False
    state.done_cut = False
    st.experimental_rerun()


def del_file(f):
    if osp.exists(f):
        os.remove(f)
        state.done_del = True
        state.sure_del = False
    else: st.error(f"File not found: {f}")


def get_vids(option):
    try:
        if option == "all":
            state.vids = [f for f in os.listdir(state.vfolder) if osp.isfile(osp.join(state.vfolder, f))]
        elif option == "original":
            state.vids = [f for f in os.listdir(state.vfolder) if ( osp.isfile(osp.join(state.vfolder, f)) and "_label_" not in f)]
        elif option == "cut":
            state.vids = [f for f in os.listdir(state.vfolder) if ( osp.isfile(osp.join(state.vfolder, f)) and "_label_" in f)]
    except: st.error("NO VIDEOS IN VFOLDER")        
    state.sel_vname = state.vids[0] if state.vids else ""


def get_newvid_name():
    state.new_vname = f"{state.sel_vname[:-4]}__##{state.ss}_{state.t}_label_{'-'.join(state.sel_lbs_ids)}.mp4"
    state.new_vpath = osp.join(state.vfolder, state.new_vname)


def ffprobe_from_mp4(data,printt=False,only_aud_sr=False,only_vid_fps=False):
    ##https://trac.ffmpeg.org/wiki/FFprobeTips#FrameRate
    out,out2=[],[]
    for i in range(len(data)):
        
        ## aud stuff
        output = subprocess.check_output('ffprobe -hide_banner -v error -select_streams a:0 -show_entries stream=codec_name,channels,sample_rate,bit_rate -of default=noprint_wrappers=1 -of compact=p=0:nk=1 '+str('"'+data[i]+'"'), shell=True)
        output = str(output).replace("\\n","").replace("b","").replace("'","").splitlines()[0]
        out.append(output)
        
        ## vid fps
        output2 = subprocess.check_output('ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=noprint_wrappers=1:nokey=1 '+str('"'+data[i]+'"'), shell=True)
        output2 = str(output2).replace("\\n","").replace("b","").replace("'","").replace("/1","")
        out2.append(output2)
        
        if printt: print(output,output2)
    
    if only_aud_sr:     return int(str(out[0]).split('|')[1])
    elif only_vid_fps:  return int(out2[0])
    else:               return out,out2


def cut_video(dr=True):
    
    ip = state.sel_vpath
    op = state.new_vpath
    ss = state.ss.replace('-',':')
    t = state.t.replace('-',':') 
    #fps

    print('IN\n',osp.basename(ip))
    #print(ffprobe_from_mp4([ip], only_vid_fps=False),'\n')
    
    ## CMD1
    cmd = (f"ffmpeg -ss {ss} -i {ip} -t {t} "
        f"-c:v copy -c:a copy {op}")
    print("\n",cmd)

    if not dr: 
        try:
            #subprocess.run(cmd, shell=True, check=True)
            os.system(cmd)
            state.done_cut = True
        except subprocess.CalledProcessError as e:
            st.error(f"An error occurred: {e}")
        finally:
            state.exec_cut = False
            state.prep_cut = False
            
    return f"ffmpeg -ss {ss} -i {ip} -t {t} -c:v copy -c:a copy {op}"

    ## Run FFmpeg command
    #cmd = (
    #    f"ffmpeg -ss {start_time} -to {end_time} -i {input_path} "
    #    f"-r {frame_rate} -c:v libx264 -preset fast -crf 22 -c:a aac {output_full_path}"
    #)
    #subprocess.run(cmd, shell=True)
    #return output_full_path