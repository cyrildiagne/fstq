import argparse
import time
import firebase_admin
import firebase_admin.firestore
from google.cloud import firestore
import sys

from .common import Collections, Status


@firestore.transactional
def _pull_items(transaction, query_ref, queued_ref, result_ref):
    # Retrieve docs from query
    docs = []
    query_results = query_ref.get(transaction=transaction)
    for doc in query_results:
        # print(doc.id)
        if not doc.exists:
            continue
        # Delete the document from queue.
        q_ref = queued_ref.document(doc.id)
        transaction.delete(q_ref)
        # Mark result_ref as processing.
        r_ref = result_ref.document(doc.id)
        transaction.update(r_ref, {'status': 'processing'})
        # add doc to docs
        docs.append(doc)
    return docs


def _start(queue, handler, max_batch_size, root_collection_name):

    # Limit to 250 to respect firestore's num transactions limit of 500
    # combining writes and deletes.
    # https://firebase.google.com/docs/firestore/manage-data/transactions
    if max_batch_size > 250:
        raise Exception('max_batch_size must be <= 250')

    # Initialize firebase admin.
    firebase_admin.initialize_app()

    # Initialize firestore client.
    db = firebase_admin.firestore.client()

    # A transaction used to pull batches of items atomically.
    transaction = db.transaction()

    # A batch to set a batch of results at once.
    batch = db.batch()

    # Ref to the current queue
    queue_col = db.collection(root_collection_name).document(queue)

    # Create a callback on_snapshot function to capture changes.
    def on_snapshot(docs):
        # Return if there is no new document to process.
        if len(docs) == 0:
            return

        # Process batch.
        # TODO: Handle failure
        tasks = [doc.to_dict()['payload'] for doc in docs]
        results = handler(tasks)

        # Save results.
        for i, result in enumerate(results):
            r_doc = queue_col.collection(Collections.RESULTS.value).document(
                docs[i].id)
            batch.update(
                r_doc, {
                    'task': tasks[i],
                    'result': result,
                    'status': Status.COMPLETE.value,
                    'dateComplete': firestore.SERVER_TIMESTAMP
                })
        # Commit updates.
        batch.commit()

    print(f'Listening for new tasks in queue: {queue}'
          f' (max_batch_size: {max_batch_size})')

    query_ref = queue_col.collection(Collections.QUEUED.value).order_by(
        'dateAdded', direction=firestore.Query.ASCENDING).limit(max_batch_size)

    queued_ref = queue_col.collection(Collections.QUEUED.value)
    result_ref = queue_col.collection(Collections.RESULTS.value)

    try:
        while True:
            sys.stdout.flush()
            # Pull items using a transaction to make sure no other worker
            # processes the same items.
            docs = _pull_items(transaction, query_ref, queued_ref, result_ref)
            if len(docs):
                on_snapshot(docs)
            else:
                time.sleep(1)
            # TODO: Inform that worker is still alive periodically.
    except KeyboardInterrupt:
        print()
        pass
    print('Closing...')


def process(worker_func):
    """The worker decorator. Can be used with @fstq.run."""
    parser = argparse.ArgumentParser(description='FSTQ Worker')
    parser.add_argument('--queue', help='Name of the queue to listen')
    parser.add_argument('--max_batch_size',
                        default=1,
                        type=int,
                        help='Max batch size')
    parser.add_argument('--root_collection_name',
                        default=Collections.ROOT.value,
                        help='Root collection name')
    args = parser.parse_args()
    # Start the worker
    _start(args.queue,
           worker_func,
           args.max_batch_size,
           root_collection_name=args.root_collection_name)
