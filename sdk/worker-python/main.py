"""
A demo worker.

```
python main.py \
    --queue 'my-queue' \
    --max_batch_size 5
```
"""
import fstq


@fstq.run
def process(items):
    # Reverse the `text` string of each item as an example worload.
    results = [item['text'][::-1] for item in items]
    print(f'Processed {len(results)} items')
    return [{'text': t} for t in results]