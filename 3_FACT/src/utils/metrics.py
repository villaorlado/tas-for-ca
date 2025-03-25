from collections import OrderedDict
import numpy as np
from .utils import expand_frame_label, parse_label, easy_reduce

def segs_to_labels_start_end_time(seg_list, bg_class):
	seg_list = [ s for s in seg_list if s.action not in bg_class ]
	labels = [ p.action for p in seg_list ]
	start  = [ p.start for p in seg_list ]
	end    = [ p.end+1 for p in seg_list ]
	return labels, start, end


def f_score(pred_segs, gt_segs, overlap, bg_class=["background"]):

	p_label, p_start, p_end = segs_to_labels_start_end_time(pred_segs, bg_class)
	y_label, y_start, y_end = segs_to_labels_start_end_time(gt_segs, bg_class)

	tp = 0
	fp = 0

	hits = np.zeros(len(y_label))

	#print(f"len of p-label is {len(p_label)}")
	#print(f"len of y-label is {len(y_label)}")
	for j in range(len(p_label)):
		intersection = np.minimum(p_end[j], y_end) - np.maximum(p_start[j], y_start)
		union = np.maximum(p_end[j], y_end) - np.minimum(p_start[j], y_start)
		IoU = (1.0*intersection / union)*([p_label[j] == y_label[x] for x in range(len(y_label))])

		try: 
			idx = np.array(IoU).argmax()

			if IoU[idx] >= overlap and not hits[idx]:
				tp += 1
				hits[idx] = 1
			else:
				fp += 1
		except:
			pass

	fn = len(y_label) - sum(hits)

	return float(tp), float(fp), float(fn)


def _joint_metrics(gt_list, pred_list):
		
		M = OrderedDict()

		# framewise accuracy
		gt_ = np.concatenate(gt_list)
		pred_ = np.concatenate(pred_list)

		correct = (gt_ == pred_)
		fg_loc = np.array([ True if g != 0 else False for g in gt_ ])
		M['AccB'] = correct.mean() * 100 # accuracy including background frames
		M['Acc'] = correct[fg_loc].mean() * 100 # accuracy without background frames

		# F1-Score
		overlap = [.1, .25, .5]
		tp, fp, fn = np.zeros(3), np.zeros(3), np.zeros(3)

		for gt, pred in zip(gt_list, pred_list):
			gt_segs = parse_label(gt)
			pred_segs = parse_label(pred)
			for s in range(len(overlap)):
				tp1, fp1, fn1 = f_score(pred_segs, gt_segs, overlap[s], bg_class=0)
				tp[s] += tp1
				fp[s] += fp1
				fn[s] += fn1

		for s in range(len(overlap)):
			precision = tp[s] / float(tp[s]+fp[s]+1e-5)
			recall = tp[s] / float(tp[s]+fn[s]+1e-5)
			f1 = 2.0 * (precision*recall) / (precision+recall+1e-5)
			f1 = np.nan_to_num(f1)*100
			M['F1@%0.2f' % overlap[s]] = f1

		return M