from . import table
from fstq.common import Collections, Metrics

import firebase_admin
import firebase_admin.firestore


def snapshot(db, queue: str):
    # Ref to the current queue.
    queue_col = db.collection(Collections.ROOT).document(queue)
    # Ref to the current queue.
    metrics_doc = queue_col.collection(
        Collections.METADATA).document('metrics')
    metrics = metrics_doc.get().to_dict()
    # Print result.
    output = table.render(
        queue, {
            'Queued': f'{metrics[Metrics.NUM_QUEUED]} items',
            'Processed': f'{metrics[Metrics.NUM_PROCESSED]} items',
            'Failed': f'{metrics[Metrics.NUM_FAILED]} items',
        }, 50)
    print(output)
