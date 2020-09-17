"""
A demo worker.

```
python main.py \
    --queue 'my-queue' \
    --max_batch_size 5
```
"""

import fstq


@fstq.process
def process(batch):
    # Reverse the `text` string of each item as an example worload.
    results = [item['text'][::-1] for item in batch]
    print(f'Processed {len(results)} items')
    return [{'text': t} for t in results]