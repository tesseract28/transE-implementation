import os
import argparse

from roles import *
from models import *
from utils import bool_flag

parser = argparse.ArgumentParser(description='TransE model')

parser.add_argument("--optimizer", type=str, default="SGD",
                    help="Which optimizer to use?")
parser.add_argument("--nBatches", type=int, default=10,
                    help="Batch size")
parser.add_argument("--margin", type=int, default=1,
                    help="The margin between positive and negative samples in the max-margin loss")
parser.add_argument("--embedding_dim", type=int, default=100,
                    help="Entity and relations embedding size")
parser.add_argument("--p_norm", type=int, default=2,
                    help="The norm to use for the distance metric")
parser.add_argument("--lr", type=int, default=0.1,
                    help="Learning rate of theoptimizer")
parser.add_argument("--nEpochs", type=int, default=5,
                    help="Learning rate of the optimizer")
parser.add_argument("--eval_every", type=int, default=2,
                    help="Interval of epochs to evaluate the model?")
parser.add_argument("--sample_size", type=int, default=30,
                    help="No. of negative samples to compare to for MRR/MR/Hit@10")
parser.add_argument("--patience", type=int, default=10,
                    help="Early stopping patience")
parser.add_argument("--debug", type=bool_flag, default=True,
                    help="Run the code in debug mode?")

params = parser.parse_args()


DATA_PATH = os.path.join(os.path.dirname(__file__), 'data/FB15K237')
TRAIN_DATA_PATH = os.path.join(DATA_PATH, 'train2id.txt')
VALID_DATA_PATH = os.path.join(DATA_PATH, 'valid2id.txt')

train_data_sampler = DataSampler(TRAIN_DATA_PATH, params.debug)
valid_data_sampler = DataSampler(VALID_DATA_PATH)
transE = TransE(params)
trainer = Trainer(transE, train_data_sampler, params)
evaluator = Evaluator(transE, valid_data_sampler, params.sample_size)

batch_size = int(len(train_data_sampler.data) / params.nBatches)

print('Batch size = %d' % batch_size)

for e in range(params.nEpochs):
    print('Running epoch %d' % e)
    for b in range(params.nBatches):
        # print('Running batch %d' % b)
        trainer.one_step(batch_size)

    if (e + 1) % params.eval_every == 0:
        log_data = evaluator.get_log_data()
        print(log_data)
        to_continue = trainer.select_model(log_data)
        if not to_continue:
            break