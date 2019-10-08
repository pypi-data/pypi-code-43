import pandas as pd
import torch.nn as nn
from torch import optim
from torch.optim.lr_scheduler import *
from tqdm import tqdm

from cframe.dataloader import *
from cframe.learner.tools import CyclicLR
from cframe.utils import *
from cframe.utils.fastprogress import *


class Learner(object):
	def __init__(self,
				 model,
				 loss,
				 metric,
				 dl_manager: DataloaderManager,
				 optimizer=None,
				 scheduler=None,
				 label='label'):
		self.model = model
		self.criteration = loss
		self.optimizer = optimizer
		self.scheduler = scheduler
		self.dl_manager = dl_manager
		self.train_dl = dl_manager.get_train_dl()
		self.valid_dl = dl_manager.get_valid_dl()
		self.test_dl = dl_manager.get_test_dl()

		self.writer = None
		self.label = label

		self.metric = metric

		if torch.cuda.is_available():
			self.device = 'cuda'
		else:
			self.device = 'cpu'

	def fit_one_cycle(self, t, base_lr, max_lr, multi=2, log_nth=None, show_batch_loss=False):
		self.optimizer = optim.SGD(self.model.parameters(), lr=base_lr)
		self.scheduler = CyclicLR(self.optimizer, base_lr, max_lr,
								  step_size_up=len(self.train_dl))
		num_epoches = int(t * multi * 2)
		self.train(num_epoches, log_nth, show_batch_loss)

	def train(self, num_epoches, log_nth=None, show_batch_loss=False):
		if log_nth is None:
			log_nth = len(self.train_dl)
		self.writer = SummaryWriter(*['train_loss', 'valid_loss', 'batch_loss', 'metric', 'lr'])
		iter_per_epoch = len(self.train_dl)
		n_iterations = num_epoches * iter_per_epoch

		mb = master_bar(range(num_epoches))
		mb.write(['train_loss', 'valid_loss', 'metric', 'lr'], table=True)
		mb.names = ['train_loss', 'valid_loss', 'batch_loss']

		train_loss_meter = AverageMeter()
		for epoch in mb:
			for i, data in enumerate(progress_bar(self.train_dl, parent=mb)):
				it = epoch * iter_per_epoch + i + 1
				# print(i, data)
				img = data['img']
				label = data[self.label]

				out = self.model(img)
				loss = self.criteration(out, label.to(self.device))

				self.optimizer.zero_grad()
				loss.backward()
				self.optimizer.step()
				if isinstance(self.scheduler, CyclicLR):
					self.scheduler.step()
				train_loss_meter.update(loss.data.cpu().item())
				self.writer.append(**dict(
					batch_loss=loss.data.cpu().item(),
					lr=self.optimizer.param_groups[0]['lr']
				))

				if it % log_nth == 0:
					self.writer.append(**dict(
						train_loss=train_loss_meter.avg,
					))
					train_loss_meter.reset()
					self.model.eval()
					with torch.no_grad():
						valid_loss = self._train_validate(mb, epoch, num_epoches, log_nth, show_batch_loss)
					if isinstance(self.scheduler, ReduceLROnPlateau):
						self.scheduler.step(valid_loss)
					else:
						self.scheduler.step()
					self.model.train()

	def _train_validate(self, mb, epoch, num_epoches, log_nth, show_batch_loss):
		valid_loss_meter = AverageMeter()
		valid_acc_meters = AverageMeter()
		for i, data in enumerate(self.valid_dl):
			img = data['img']
			label = data[self.label]
			out = self.model(img)

			loss = self.criteration(out, label.to(self.device))
			valid_loss_meter.update(loss.data.cpu().item())
			valid_acc_meters.update(self.metric(out.data.cpu().numpy(), label.data.cpu().numpy()))

		self.writer.append(**dict(
			valid_loss=valid_loss_meter.avg,
			metric=valid_acc_meters.avg
		))
		train_loss = self.writer.get('train_loss')
		valid_loss = self.writer.get('valid_loss')
		batch_loss = self.writer.get('batch_loss')
		lr = self.writer.get('lr')
		metric = self.writer.get('metric')

		# print(train_loss, valid_loss)
		mb.write(['%2.2f' % round(train_loss[-1], 2),
				  '%2.2f' % round(valid_loss[-1], 2),
				  '%2.2f %%' % round(metric[-1] * 100, 2),
				  '%.0e' % lr[-1]
				  ], table=True)
		log_iterations = [(item) * log_nth for item in range(1, len(valid_loss) + 1)]
		batch_iterations = [item for item in range(1, len(lr) + 1)]

		if show_batch_loss:
			loss_graph_node = [[log_iterations, train_loss],
							   [log_iterations, valid_loss], [batch_iterations, batch_loss]]
		else:
			loss_graph_node = [[log_iterations, train_loss], [log_iterations, valid_loss]]
		lr_graph_node = [batch_iterations, lr]
		mb.update_graph(loss_graphs=loss_graph_node, lr_graphs=lr_graph_node,
						x_bounds=[1, len(self.train_dl) * (num_epoches+1) + 1],
						y_bounds=[min(train_loss), max(valid_loss)],
						lr_bounds=[0, max(lr) + (1e-10)])
		return valid_loss_meter.avg

	def predict(self, **data):
		img = data['img']

		img = Image.open(img)
		img = np.array(img)
		ori_img = img

		img = self.dl_manager.pred_img_transform(img)

		self.model.eval()
		img = torch.unsqueeze(img, dim=0)
		out = self.model(img)
		self.model.train()

		out = out.data.cpu()
		preds = out[0].data.cpu().numpy()
		preds = np.transpose(preds, [1, 2, 0])

		if preds.shape[-1] == 1:
			preds = preds > 0.5
		else:
			preds = np.argmax(preds, axis=-1)

		preds = np.squeeze(preds)
		prob_preds = torch.squeeze(out)
		prob_preds = prob_preds.permute([0, 2, 3, 1])
		return ori_img, preds.astype(np.uint8), prob_preds

	def save(self, path):
		if type(self.model) == nn.DataParallel:
			para = self.model.module.state_dict()
		else:
			para = self.model.state_dict()
		torch.save(para, path)

	def test(self, phase='test'):
		dl = self.dl_manager.get_test_dl(phase=phase)
		items = []
		for i, data in tqdm(enumerate(dl)):
			img = data['img']
			fixation = data['fixation']
			name = data['name']

			outs = self.model(img)

			item = [name]
			for j, out in enumerate(outs):
				cur_acc = self._cal_jud_acc(out, fixation)
				item.append(cur_acc)
				item.append(np.average(out.data.cpu().numpy()))
			items.append(item)
		df = pd.DataFrame(items)
		return df

	def load(self, path, remove_module=False):
		para = torch.load(path, map_location='cpu')
		if remove_module:
			for k in list(para.keys()):
				if k.startswith('module'):
					new_k = k.replace('module.', '', 1)
					para[new_k] = para[k]
					del para[k]
		self.model.load_state_dict(para)
