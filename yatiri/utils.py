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
    teaser = doc.get('teaser', '')
    body = doc.get('body', '')

    if teaser and len(teaser) > 200:
        target = teaser
    else:
        target = body

    firstnl = target.find('\n')
    if target[:firstnl].count(' ') < 15:
        target = target[firstnl:].strip()

    if len(target) > limit:
        idx = target.rfind(' ', 200, 300)
        if idx == -1:
            idx == 300
        target = target[:idx].strip() + ' ...'

    return nl2br(target)


def doc_image(doc):
    images = doc.get('images')
    if images:
        # TODO: improve me
        url = images[0]
    else:
        url = "/static/img/260x180.gif"
    return '<img class="media-object" src="{}" />'.format(url)


def nl2br(text):
    return text.replace('\n', '<br />')
