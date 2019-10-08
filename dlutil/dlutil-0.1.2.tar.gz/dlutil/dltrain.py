import torch
import os
import shutil
import time
import json
import torch
import torch.nn as nn
from tensorboardX import SummaryWriter
from tqdm import trange


__all__ = ['Checkpoint', 'DlModel', 'Listener']


class Checkpoint:
    def __init__(self, model_dir, ckpt_name=None, max_to_keep=5, device=None):
        self.model_dir = model_dir
        self.ckpt_name = 'model' if ckpt_name is None else ckpt_name
        self.max_to_keep = max_to_keep
        self.device = device
        os.makedirs(self.model_dir, exist_ok=True)
        self.ck_index_path = f'{self.model_dir}/checkpoints'
        self.ck_index_dict = None
        self.pre_trained = False
        if os.path.exists(self.ck_index_path):
            self._read_checkpoints_index()
            self.pre_trained = True
        else:
            self.ck_index_dict = {'cursor': '', 'all_ckpt_paths': []}

    def _read_checkpoints_index(self):
        self.ck_index_dict = json.load(
            open(self.ck_index_path, encoding='utf-8'))

    def _write_checkpoints_index(self):
        json.dump(self.ck_index_dict, open(self.ck_index_path, 'w'),
                  ensure_ascii=False, indent=4)

    @property
    def has_pre_trained_models(self):
        return self.pre_trained

    @property
    def latest_checkpoint(self):
        return self.ck_index_dict['cursor']

    @property
    def all_checkpoints(self):
        return self.ck_index_dict['all_ckpt_paths']

    def load_state_dict_from_latest_checkpoint(self):
        model_path = f'{self.model_dir}/{self.latest_checkpoint}'
        state_dict, global_step = self.load_state_dict(model_path, self.device)
        return state_dict, global_step

    @classmethod
    def load_state_dict(cls, model_path, device=None):
        map_location = 'cpu' if device is None else f'cuda:{device}'
        state_dict, global_step = torch.load(
            model_path, map_location=map_location)
        return state_dict, global_step

    def reset(self):
        self.ck_index_dict = {'cursor': '', 'all_ckpt_paths': []}

    def save(self, model, global_step, given_index=None):
        '''given_index: Can be steps or epochs. If not to be defined, it will be time string.
        '''
        all_ckpt_paths = self.ck_index_dict['all_ckpt_paths']
        if given_index is None:
            given_index = str(int(time.time() * 10))[-8:]
        else:
            given_index = f'{given_index}-{str(int(time.time() * 10))[-8:]}'
        model_name = f'{self.ckpt_name}-{given_index}.pt'
        if model_name in all_ckpt_paths:
            raise ValueError(
                f'Model name "{model_name}" cannot be duplicated.')
        if len(all_ckpt_paths) >= self.max_to_keep:
            all_ckpt_paths.remove(all_ckpt_paths[0])
        all_ckpt_paths.append(model_name)
        self.ck_index_dict['cursor'] = model_name
        ckpt_path = f'{self.model_dir}/{model_name}'
        torch.save((model.state_dict(), global_step), ckpt_path)
        self._write_checkpoints_index()


class DlModel:
    def __init__(self, model: nn.Module, ckpt: Checkpoint):
        self._model = model
        self.ckpt = ckpt
        self.model_dir = self.ckpt.model_dir
        self.device = self.ckpt.device
        self.global_step = 0

    def reset(self):
        shutil.rmtree(self.model_dir)
        os.makedirs(self.model_dir, exist_ok=True)
        self.ckpt.reset()
        self.global_step = 0

    @property
    def model(self):
        return self._model

    def train(self, gntr, loss_func, optimizer, num_epochs, metrics=None, listeners=None, summ_steps=100, from_scratch=True):
        if not from_scratch:
            state_dict, global_step = self.ckpt.load_state_dict_from_latest_checkpoint()
            self._model.load_state_dict(state_dict)
            self.global_step = global_step
        else:
            self.reset()
        summ_writer = SummaryWriter(logdir=f'{self.model_dir}/train')
        dstr, steps_per_epoch = gntr
        if listeners:
            for l in listeners:
                l.begin(self.model_dir, self._model, self.device)
        epoch = self.global_step // steps_per_epoch
        for _ in range(num_epochs):
            progress_desc = f'Epoch {epoch + 1}'
            dstr_iter = iter(dstr)
            self._model.train()
            for _ in trange(steps_per_epoch, desc=progress_desc):
                bxs, bys = next(dstr_iter)
                if self.device is not None:
                    bxs = [bx.cuda(self.device) for bx in bxs]
                    if type(bys) in (list, tuple):
                        bys = [by.cuda(self.device) for by in bys]
                    else:
                        bys = bys.cuda(self.device)
                by_ = self._model(bxs)
                loss = loss_func(by_, bys)
                if self.global_step == 0:
                    summ_writer.add_scalar(
                        'train/loss', loss, self.global_step)
                    if metrics is not None:
                        for metric in metrics:
                            metric.reset()
                            metric.update(bys, by_)
                            summ_writer.add_scalar(
                                f'train/{metric.name}', metric.result, self.global_step)
                    summ_writer.flush()
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                self.global_step += 1
                if self.global_step % summ_steps == 0:
                    summ_writer.add_scalar(
                        'train/loss', loss, self.global_step)
                    if metrics is not None:
                        for metric in metrics:
                            metric.reset()
                            metric.update(bys, by_)
                            summ_writer.add_scalar(
                                f'train/{metric.name}', metric.result, self.global_step)
                    summ_writer.flush()
            epoch = self.global_step // steps_per_epoch
            self.ckpt.save(self._model, self.global_step, given_index=epoch)
            if listeners:
                self._model.eval()
                for l in listeners:
                    l.run(epoch)
        summ_writer.close()
        if listeners:
            for l in listeners:
                l.close()


class Listener:
    def __init__(self, run_name, data_gn, metrics):
        self.run_name = run_name
        self.dsgn, self.steps_per_epoch = data_gn
        self.metrics = metrics

    def begin(self, model_dir, model, device):
        self.model_dir = model_dir
        self.model = model
        self.device = device
        self.summ_writer = SummaryWriter(
            logdir=f'{self.model_dir}/{self.run_name}')

    def run(self, epoch):
        progress_desc = f'{self.run_name} evaluation {epoch}'
        ds_iter = iter(self.dsgn)
        for metric in self.metrics:
            metric.reset()
        for _ in trange(self.steps_per_epoch, desc=progress_desc):
            bxs, bys = next(ds_iter)
            if self.device is not None:
                bxs = [bx.cuda(self.device) for bx in bxs]
                if type(bys) in (list, tuple):
                    bys = [by.cuda(self.device) for by in bys]
                else:
                    bys = bys.cuda(self.device)
            by_ = self.model(bxs)
            for metric in self.metrics:
                metric.update(bys, by_)
        for metric in self.metrics:
            result = metric.result
            print(f'{metric.name}: {result}')
            self.summ_writer.add_scalar(f'{metric.name}', result, epoch)
        self.summ_writer.flush()

    def close(self):
        self.summ_writer.close()
