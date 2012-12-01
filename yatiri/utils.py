from progressbar import ProgressBar, Counter, Timer

PROGRESS_WIDGETS = [
    'Processed: ', Counter(), ' - ', Timer(),
]


def report_progress(it):
    pbar = ProgressBar(widgets=PROGRESS_WIDGETS)
    return pbar(it)

def report_elapsed(it):
    pbar = ProgressBar(widgets=[Timer()])
    return pbar(it)
