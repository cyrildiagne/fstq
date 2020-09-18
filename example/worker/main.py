"""
A demo worker.

```
python main.py \
    --queue 'my-queue' \
    --max_batch_size 5
```
"""

import fstq


def reverse(text):
    return text[::-1]


@fstq.process
def process(batch):
    results = [reverse(item['text']) for item in batch]
    print(f'Processed {len(results)} items')
    return [{'text': t} for t in results]