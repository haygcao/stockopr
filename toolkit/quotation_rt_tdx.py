import time

from util import snapshot, ocr


def get_rt_quote_tdx():
    time.sleep(3)

    img = snapshot.snapshot2('')
    text = ocr.reg(img)

    d = [
        ('close', 'open'),
        ('change', 'high'),
        ('percent', 'low'),
        ('volume', 'qrr'),

    ]

    quote = {}

    rows = text.split('\n')
    for row in rows:
        if not row.strip():
            continue

        cols = row.split()

        quote.update({d[len(quote) // 2][0]: cols[0]})
        quote.update({d[len(quote) // 2][1]: cols[-1]})

        if len(quote) == 8:
            break
    return quote


if __name__ == '__main__':
    text = get_rt_quote_tdx()
    print(text)
