from yacs.config import CfgNode

cfg = CfgNode()

# basic parameters
cfg.thumbnails_dir = None
cfg.groundtruth_dir = None
cfg.train_video_list = None
cfg.test_video_list = None
cfg.base_logdir = None
cfg.logdir = None
cfg.project_name = None

# eval parameters
cfg.eval_thumbnails_dir = None
cfg.eval_groundtruth_dir = None
cfg.eval_video_list = None
cfg.eval_output_dir = None

# print parameters
cfg.aux = CfgNode()
cfg.aux.gpu = 1
cfg.aux.runid = 0  # the X-th run of this configuration
cfg.aux.eval_every = 10
cfg.aux.print_every = 1

# dataset
cfg.dataset = ""
cfg.sr = 1  # temporal down-sample rate
cfg.eval_bg = True  # if including background frame in evaluation
cfg.nclasses = 2

# training
cfg.batch_size = 4
cfg.optimizer = "SGD"
cfg.epoch = 2
cfg.lr = 0.1
cfg.lr_decay = -1
cfg.momentum = 0.009
cfg.weight_decay = 0.000
cfg.clip_grad_norm = 10.0

#########################
# model
cfg.FACT = FACT = CfgNode()
FACT.ntoken = 30
FACT.block = "iuUU"  # i - input block; u - update block; U - update block with temporal down/up-sample
FACT.trans = False  # if trans is available using training + testing
FACT.fpos = True
FACT.cmr = 0.3  # channel masking rate
FACT.mwt = 0.1  # weight for merging predictions from action/frame branch

# input block
cfg.Bi = Bi = CfgNode()
Bi.hid_dim = 512
Bi.dropout = 0.5

Bi.a = "sca"
Bi.a_nhead = 8
Bi.a_ffdim = 2048
Bi.a_layers = 6
Bi.a_dim = 512

Bi.f = "cnn"
Bi.f_layers = 10
Bi.f_ln = True
Bi.f_dim = 512
Bi.f_ngp = 4


# update block
cfg.Bu = Bu = CfgNode()
Bu.hid_dim = None
Bu.dropout = None

Bu.a = "sa"
Bu.a_nhead = None
Bu.a_ffdim = None
Bu.a_layers = 1
Bu.a_dim = None

Bu.f = None
Bu.f_layers = 5
Bu.f_ln = None
Bu.f_dim = None
Bu.f_ngp = None

# update block with temporal downsample and upsample
cfg.BU = BU = CfgNode()
BU.hid_dim = None
BU.dropout = None

BU.a = "sa"
BU.a_nhead = None
BU.a_ffdim = None
BU.a_layers = 1
BU.a_dim = None

BU.f = None
BU.f_layers = 5
BU.f_ln = None
BU.f_dim = None
BU.f_ngp = None

BU.s_layers = 1


#########################
# Loss
cfg.Loss = Loss = CfgNode()
Loss.pc = 1.0  # match weight for prob
Loss.a2fc = 1.0  # match weight for a2f_attn overlap
Loss.match = "o2o"  # one-to-one(o2o) or one-to-many(o2m)
Loss.bgw = 1.0  # weight for background class
Loss.nullw = (
    -1.0
)  # weight for null class in action token; -1 -> auto-compute from statistic
Loss.sw = 0.0  # weight for smoothing loss

#########################
# temporal masking
cfg.TM = TM = CfgNode()
TM.use = False
TM.t = 30
TM.p = 0.05
TM.m = 5
TM.inplace = True


def get_cfg_defaults():
    return cfg.clone()
