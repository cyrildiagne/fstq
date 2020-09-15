import ftq


def reverse(text):
    return text[::-1]


def process(items):
    # Reverse the `text` string of each item as an example.
    results = [reverse(item['text']) for item in items]
    print(f'Processed {len(results)} items.')
    return [{'text': t} for t in results]


# Start listening for new items in the queue.
ftq.start('my-queue', process)