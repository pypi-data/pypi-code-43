from ioflow.corpus import get_corpus_processor
from ioflow.task_status import get_task_status
from ioflow.model_saver import get_model_saver
from ioflow.performance_metrics import get_performance_metrics
from ioflow.configure import read_configure

config = read_configure()

task_status = get_task_status(config)
# task_status.send_status(task_status.START)


# read data according configure
corpus_processor = get_corpus_processor(config)
corpus_processor.prepare()


performance_metrics = get_performance_metrics(config)
# performance_metrics.set_metrics('test_loss', evaluate_result['loss'])

model_saver = get_model_saver(config)
# model_saver.save_model(final_saved_model)

__all__ = [
    'config', 'task_status', 'corpus_processor',
    'performance_metrics', 'model_saver'
]
