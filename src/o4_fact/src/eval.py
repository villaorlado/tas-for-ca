import torch
from tqdm import tqdm
from .configs.utils import get_cfg_defaults
from .utils.dataset import create_dataset, DataLoader
from .utils import utils
from .utils.evaluate import Checkpoint, Video
from .utils.train_tools import save_results
from .configs.utils import int2float_check, _get_var
import json
import os
import argparse
from .home import get_project_base
from .configs.utils import setup_cfg
from yacs.config import CfgNode


def read_args_json_file(args_json_file):

    # Read the json file
    with open(args_json_file, "r") as f:
        config_dict = json.load(f)
    json_cfg = CfgNode(config_dict)
    set_cfgs = json_cfg.aux.set_cfgs

    # Define the new cfg file
    cfg = CfgNode(json_cfg)

    # preprocess set_cfgs to convert int2float
    L = len(set_cfgs) if set_cfgs else 0
    new_set_cfgs = []
    for i in range(L//2):
        k = set_cfgs[i*2]
        v = set_cfgs[i*2+1]

        if not isinstance(k, list):
                k = [k]
        for k_ in k:
            tgt = _get_var(cfg, k_.split('.'))
            v_ = int2float_check(v, tgt)
            new_set_cfgs.extend([k_, v_])

    # update cfg
    cfg.merge_from_list(new_set_cfgs)

    return cfg


def get_preds(args_json_filepath:str):
    """
    [Arguments]
        args_json_filepath: path to the json file containing the arguments (in log folder)
        epoch: epoch number to load the model from
        output_json_filepath: path to the json file where the predictions will be saved

    [Returns]
        nothing. Saves the predictions to the {output_json_filepath}

    [Usage]
        python3 -m src.eval --args_json_filepath "args.json" --epoch 40 --output_json_filepath "preds.json"
    """

    # Read config file
    cfg = read_args_json_file(args_json_filepath)

    # Get dataset
    dataset, test_dataset = create_dataset(cfg)
    dataset_name = cfg.dataset

    # Load Model
    if dataset_name == 'epic-kitchens':
        from .models.blocks_SepVerbNoun import FACT
        model = FACT(cfg, dataset.input_dimension)
    else:
        from .models.blocks import FACT 
        model = FACT(cfg, dataset.input_dimension, dataset.nclasses)

    # Read Model weights
    weights = f'split1_network.iter-32.net'
    weights = torch.load(weights, map_location='cpu')
    if 'frame_pe.pe' in weights:
        del weights['frame_pe.pe']
    model.load_state_dict(weights, strict=False)
    model.eval()

    # Dataloaders
    train_loader = DataLoader(dataset, 1, shuffle=False)
    test_loader  = DataLoader(test_dataset, 1, shuffle=False)

    for loader in [train_loader, test_loader]:

        # Metrics
        ckpts = []
        ckpt = Checkpoint(-1, bg_class=([] if cfg.eval_bg else dataset.bg_class))

        # Storage variables
        all_results = {}

        # Generate predictions
        for vname, batch_seq, train_label_list, eval_label in tqdm(loader):
            seq_list = [ s for s in batch_seq ]
            train_label_list = [ s for s in train_label_list ]
            video_saves = model(seq_list, train_label_list)
            save_results(ckpt, vname, eval_label, video_saves)
            
            local_results = {}
            label_array = []
            pred_array = []
            
            for label, pred in zip(video_saves[0]['pred'], eval_label[0]):
                label_array.append(int(label))
                pred_array.append(int(pred))
                
            local_results["label"] = label_array
            local_results["pred"] = pred_array
            all_results[vname[0]] = local_results
        
        # Writing to sample.json
        json_object = json.dumps(all_results, indent=4)
        with open(f"new_sample.json", "w") as outfile:
            outfile.write(json_object)
        print(f"Saved predictions of epoch= to new_sample.json")
        
        # Metrics
        ckpt.compute_metrics()
        ckpts.append(ckpt)
        print(utils.easy_reduce([c.metrics for c in ckpts]))

            
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--args_json_filepath", type=str, help="path to the json file containing the arguments (in log folder)")
    parser.add_argument("--epoch", type=int, help="epoch number to load the model from")
    parser.add_argument("--output_json_filepath", type=str, help="path to the json file where the predictions will be saved")
    args = parser.parse_args()
    
    get_preds(args.args_json_filepath) #, args.epoch, args.output_json_filepath)