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


def doc_summary(doc, limit=300):
    teaser = doc.get('teaser')
    if teaser:
        return teaser

    body = doc['body']
    if len(body) < limit:
        return body

    idx = body.rfind(' ')
    return body[:idx] + ' ...'
