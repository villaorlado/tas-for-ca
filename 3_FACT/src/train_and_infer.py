import csv
import json
import os
import random
from datetime import datetime
from pathlib import Path

import torch
from torch import optim

from .configs.default import get_cfg_defaults
from .models.blocks import FACT
from .models.loss import MatchCriterion
from .utils.dataset import DataLoader, create_dataset
from .utils.evaluate import Checkpoint
from .utils.train_tools import compute_null_weight, save_results


def evaluate(global_step, net, testloader):

    print("TESTING" + "~" * 10)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = Checkpoint(
        global_step + 1,
        bg_class=([] if net.cfg.eval_bg else testloader.dataset.bg_class),
    )
    net.eval()
    with torch.no_grad():
        for vnames, seq_list, train_label_list, eval_label_list in testloader:

            seq_list = [s.to(device) for s in seq_list]
            train_label_list = [s.to(device) for s in train_label_list]
            video_saves = net(seq_list, train_label_list)
            save_results(ckpt, vnames, eval_label_list, video_saves)

    net.train()
    ckpt.compute_metrics()

    return ckpt


def infer_with_new_dir(
    cfg_path: str,
    model_weights_path: str,
    eval_output_dir: str,
    dataset_name: str = None,
    thumbnails_dir: str = None,
    groundtruth_dir: str = None,
    video_list: list[str] = None,
):

    dataset_dict = {}
    dataset_dict[dataset_name] = (thumbnails_dir, groundtruth_dir, video_list)

    infer(cfg_path, model_weights_path, dataset_dict, eval_output_dir)


def infer_with_original_dataset(
    cfg_path: str, model_weights_path: str, eval_output_dir: str
):

    ####################################
    # Load configuration file

    if cfg_path is str:
        cfg_path = [cfg_path]

    cfg = get_cfg_defaults()
    cfg.merge_from_file(cfg_path)

    ####################################
    # Define dataset dictionary
    dataset_dict = {
        "train": (cfg.thumbnails_dir, cfg.groundtruth_dir, cfg.train_video_list),
        "test": (cfg.thumbnails_dir, cfg.groundtruth_dir, cfg.test_video_list),
    }

    ####################################
    # Run the inference

    infer(cfg_path, model_weights_path, dataset_dict, eval_output_dir)


def infer(
    cfg_path: str, model_weights_path: str, dataset_dict: dict, eval_output_dir: str
):

    ####################################
    # Run predictions

    for label, (thumbnails_dir, groundtruth_dir, video_list) in dataset_dict.items():

        ####################################
        # Load configuration file

        if cfg_path is str:
            cfg_path = [cfg_path]

        cfg = get_cfg_defaults()
        cfg.merge_from_file(cfg_path)

        cfg_update_list = [
            "eval_thumbnails_dir",
            thumbnails_dir,
            "eval_groundtruth_dir",
            groundtruth_dir,
            "eval_video_list",
            video_list,
            "eval_output_dir",
            eval_output_dir,
        ]
        cfg.merge_from_list(cfg_update_list)

        ####################################
        # Output files

        output_json_file = f"{cfg.eval_output_dir}/{label}.json"
        overwrite_output_json = True

        # Check if output file exists
        if (
            os.path.isfile(f"{output_json_file}") is True
            and overwrite_output_json is False
        ):
            raise FileExistsError("File already exists")

        with open(f"{output_json_file}", "w", encoding="utf-8") as file:
            json.dump({}, file)

        ####################################
        # Dataset

        dataset = create_dataset(
            cfg, cfg.eval_thumbnails_dir, cfg.eval_groundtruth_dir, cfg.eval_video_list
        )
        dataloader = DataLoader(
            dataset, batch_size=cfg.batch_size, shuffle=False)

        ####################################
        # Network

        net = FACT(cfg, dataset.input_dimension, dataset.nclasses)

        weights = torch.load(model_weights_path, map_location="cpu")
        net.load_state_dict(weights, strict=False)

        if cfg.Loss.nullw == -1:
            compute_null_weight(cfg, dataset)
        net.mcriterion = MatchCriterion(
            cfg, dataset.nclasses, dataset.bg_class)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        net.to(device)

        ####################################
        # Evaluate

        net.eval()
        ckpt = Checkpoint(
            -1,
            bg_class=([] if net.cfg.eval_bg else dataloader.dataset.bg_class),
            eval_edit=False,
        )
        video_results = {}
        with torch.no_grad():
            for vnames, seq_list, train_label_list, eval_label_list in dataloader:

                seq_list = [s.to(device) for s in seq_list]
                train_label_list = [s.to(device) for s in train_label_list]
                video_saves = net(seq_list, train_label_list)
                save_results(ckpt, vnames, eval_label_list, video_saves)

                # Save predictions
                for i, vname in enumerate(vnames):
                    local_results = {}
                    if groundtruth_dir is not None:
                        local_results["groundtruth"] = eval_label_list[i]
                    local_results["predictions"] = video_saves[i]["pred"].tolist()
                    video_results[vname] = local_results

        ####################################
        # Save predictions

        with open(f"{output_json_file}", "w", encoding="utf-8") as file:
            json.dump(video_results, file, indent=4)

        ####################################
        # Print metrics

        ckpt.compute_metrics()

        log_dict = {}
        string = ""
        for k, v in ckpt.metrics.items():
            string += "%s:%.1f, " % (k, v)
            log_dict[f"test-metric/{k}"] = v
        print(string)


def initialise_training(cfg_path: str, **kwargs):

    ####################################
    # Load configuration file

    if cfg_path is str:
        cfg_path = [cfg_path]

    cfg = get_cfg_defaults()
    cfg.merge_from_file(cfg_path)

    cfg_update_list = []
    for key, value in kwargs.items():
        cfg_update_list.append(key)
        cfg_update_list.append(value)

    cfg.merge_from_list(cfg_update_list)

    ####################################
    # Configurations handling

    if (cfg.train_video_list is None) != (cfg.test_video_list is None):
        raise ValueError(
            None,
            "Both 'train_video_list' and 'test_video_list' must be provided together.",
        )

    if cfg.train_video_list is None and cfg.test_video_list is None:

        # Get Video IDs
        groundtruth_files = os.listdir(cfg.groundtruth_dir)
        video_ids = [Path(video_id).stem for video_id in groundtruth_files]

        random.seed(2025)
        random.shuffle(video_ids)

        cfg.train_video_list = video_ids[: int(0.8 * len(video_ids))]
        cfg.test_video_list = video_ids[int(0.8 * len(video_ids)):]

    # Logging purposes
    if cfg.base_logdir is None:
        cfg.base_logdir = "log"

    if cfg.project_name is None:
        cfg.project_name = datetime.now().strftime("%Y%b%d_%H%Mh")

    cfg.logdir = f"{cfg.base_logdir}/{cfg.project_name}"

    ####################################
    # Logging

    # Define log directory
    os.makedirs(cfg.logdir, exist_ok=True)
    os.makedirs(f"{cfg.logdir}/model_weights", exist_ok=True)

    # Write metrics file
    train_metric_log_path = f"{cfg.logdir}/train_metrics.csv"
    if os.path.exists(train_metric_log_path):
        raise FileExistsError(
            None, f"train_metric_log_path exists at {train_metric_log_path}!"
        )

    test_metric_log_path = f"{cfg.logdir}/test_metrics.csv"
    if os.path.exists(test_metric_log_path):
        raise FileExistsError(
            None, f"test_metric_log_path exists at {test_metric_log_path}!"
        )

    # # Save configuration file
    # with open(f"{cfg.logdir}/config.yaml", "w") as f:
    # 	f.write(cfg.dump())

    ####################################
    # Dataset

    dataset = create_dataset(
        cfg, cfg.thumbnails_dir, cfg.groundtruth_dir, cfg.train_video_list
    )
    test_dataset = create_dataset(
        cfg, cfg.thumbnails_dir, cfg.groundtruth_dir, cfg.test_video_list
    )
    trainloader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True)
    testloader = DataLoader(
        test_dataset, batch_size=cfg.batch_size, shuffle=False)

    ####################################
    # Save configuration file

    cfg.merge_from_list(["nclasses", dataset.nclasses])

    # Write yaml file
    with open(f"{cfg.logdir}/log_config.yaml", "w", encoding="utf-8") as f:
        f.write(cfg.dump())

    ####################################
    # Network

    net = FACT(cfg, dataset.input_dimension, dataset.nclasses)

    if cfg.Loss.nullw == -1:
        compute_null_weight(cfg, dataset)
    net.mcriterion = MatchCriterion(cfg, dataset.nclasses, dataset.bg_class)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net.to(device)

    ####################################
    # Training parameters

    if cfg.optimizer == "SGD":
        optimizer = optim.SGD(
            net.parameters(),
            lr=cfg.lr,
            momentum=cfg.momentum,
            weight_decay=cfg.weight_decay,
        )
    elif cfg.optimizer == "Adam":
        optimizer = optim.Adam(
            net.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay
        )

    ####################################
    # Training

    net.train()
    start_epoch = 0
    ckpt = Checkpoint(
        -1,
        bg_class=([] if net.cfg.eval_bg else testloader.dataset.bg_class),
        eval_edit=False,
    )
    for epoch_nb in range(start_epoch, cfg.epoch):

        for vnames, seq_list, train_label_list, eval_label_list in trainloader:

            seq_list = [s.to(device) for s in seq_list]
            train_label_list = [s.to(device) for s in train_label_list]
            loss, video_saves = net(
                seq_list, train_label_list, compute_loss=True)
            loss.backward()

            if cfg.clip_grad_norm > 0:
                torch.nn.utils.clip_grad_norm_(
                    net.parameters(), cfg.clip_grad_norm)
            optimizer.step()

            save_results(ckpt, vnames, eval_label_list, video_saves)

        # print some progress information
        if (epoch_nb + 1) % cfg.aux.print_every == 0:

            ckpt.compute_metrics()
            ckpt.average_losses()

            train_log_dict = dict()
            train_log_dict["epoch_nb"] = epoch_nb

            string = "Iter%d, " % (epoch_nb + 1)
            _L = len(string)
            for k, v in ckpt.loss.items():
                train_log_dict[f"train-loss/{k}"] = v
                string += f"{k}:{v:.1f}, "
            print(string)

            string = " " * _L
            for k, v in ckpt.metrics.items():
                string += "%s:%.3f, " % (k, v)
                train_log_dict["train-metric/" + k] = v
            print(string)

            # Log metrics by writing to csv file
            if os.path.exists(train_metric_log_path) is False:
                with open(
                    train_metric_log_path, "w", newline="", encoding="utf-8"
                ) as f:
                    w = csv.DictWriter(f, train_log_dict.keys())
                    w.writeheader()

            with open(train_metric_log_path, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, train_log_dict.keys())
                w.writerow(train_log_dict)

        # Test and save model every x iterations
        if epoch_nb != 0 and (epoch_nb + 1) % cfg.aux.eval_every == 0:
            test_ckpt = evaluate(epoch_nb, net, testloader)
            net.save_model(
                f"{cfg.logdir}/model_weights/network_iter_{epoch_nb}.net")

            test_log_dict = {}
            test_log_dict["epoch_nb"] = epoch_nb

            string = ""
            for k, v in test_ckpt.metrics.items():
                string += "%s:%.1f, " % (k, v)
                test_log_dict[f"test-metric/{k}"] = v
            print(string)

            # Log metrics by writing to csv file
            if os.path.exists(test_metric_log_path) is False:
                with open(test_metric_log_path, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, test_log_dict.keys())
                    w.writeheader()

            with open(test_metric_log_path, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, test_log_dict.keys())
                w.writerow(test_log_dict)
