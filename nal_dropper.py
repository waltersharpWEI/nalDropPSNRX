#created on 2022/06/22, 11:50 (UTC+8)
#The nal dropper will take a exp config json file as input
#create a group of dropped h264 files
#Then compute the PSNR of each of them
import json
import os
import logging
import random
from pathlib import Path
from nal_assembler import nal_assemble

#input, the original manifest, the dropped manifest path, and loss rate
#output, 0 if ok, 1 if fail
#side-effect, generate a dropped manifest file for use of assemling
def manifest_dropper(manifest_path, dropped_manifest_path, loss_rate=0):
    logging.debug(nal_path+" "+manifest_path+" "+dropped_manifest_path+" "+str(loss_rate))
    with open(manifest_path,'r') as f1:
        nal_list = json.load(f1)
        #the nal_list after random dropping s.t. loss rate
        d_nal_list = []
        for nal in nal_list:
            logging.debug(nal)
            dice = random.randint(0, 100)
            #the frame is p frame, subject to the lossy attack
            #with probability loss_rate this happens
            if nal['type'] == 1 and dice < loss_rate:
                logging.debug("dropping frame "+str(nal["nal_no"]))
            else:
                d_nal_list.append(nal)
        #write the dropped nal list to the target path
        #print(d_nal_list)
        jsonStr = json.dumps(d_nal_list)
        with open(dropped_manifest_path, 'w') as f2:
            f2.write(jsonStr)
    return 0

#TODO:stub
def nal_dropper(nal_path,tmp_drop_manifest_path,tmp_drop_video_path):
    logging.debug(nal_path+" "+tmp_drop_manifest_path+" "+tmp_drop_video_path)
    logging.debug("Reassempling the video from manifest " + tmp_drop_manifest_path)
    nal_assemble(nal_path,tmp_drop_manifest_path,tmp_drop_video_path)
    logging.debug("The dropped video is putted to " + tmp_drop_video_path)
    return 0

# TODO:stub
def psnr_computer(origin_video_path, tmp_drop_video_path, psnr_log_path):
    #print(origin_video_path+" "+ tmp_drop_video_path+" "+ psnr_log_path)
    cmd = "ffmpeg -i "+origin_video_path+" -i "+tmp_drop_video_path+" -lavfi psnr=\"stats_file="+psnr_log_path+"\" -f null -"
    logging.debug(cmd)
    os.system(cmd)
    return 0

if __name__=="__main__":
    logging.basicConfig(level=logging.WARNING)
    config_path = "../nalDropPSNR2/exp_config.json"
    with open(config_path) as f1:
        jconfig = json.load(f1)
        video_types = jconfig["video_types"]
        for video_type in video_types:
            video_type_path = os.path.join(jconfig["origin_path"],video_type)
            nal_path = os.path.join(video_type_path,"nals")
            manifest_path = os.path.join(video_type_path,"manifest/manifest.json")
            tmp_root = jconfig["tmp_path"]
            tmp_path = os.path.join(tmp_root,video_type)
            tmp_manifest_path = os.path.join(tmp_path,"drop_manifest")
            Path(tmp_manifest_path).mkdir(parents=True, exist_ok=True)
            tmp_video_path = os.path.join(tmp_path, "drop_video")
            Path(tmp_video_path).mkdir(parents=True, exist_ok=True)
            tmp_psnr_path = os.path.join(tmp_path, "psnr_log")
            Path(tmp_psnr_path).mkdir(parents=True, exist_ok=True)
            loss_rate_list = jconfig["loss_rate"]
            origin_video_name = "s2_GOF0_"+video_type+".h264"
            for loss_rate in loss_rate_list:
                tmp_drop_manifest_path = os.path.join(tmp_manifest_path,str(loss_rate)+".json")
                manifest_dropper(manifest_path, tmp_drop_manifest_path, loss_rate)
                tmp_drop_video_path = os.path.join(tmp_video_path,str(loss_rate)+".h264")
                nal_dropper(nal_path, tmp_drop_manifest_path, tmp_drop_video_path)
                origin_video_path = os.path.join(video_type_path, origin_video_name)
                psnr_log_path = os.path.join(tmp_psnr_path,str(loss_rate)+".log")
                psnr_log_path=psnr_log_path.replace("\\","/")
                psnr_computer(origin_video_path, tmp_drop_video_path, psnr_log_path)
