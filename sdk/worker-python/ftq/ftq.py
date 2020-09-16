import time
import firebase_admin
from firebase_admin import firestore

# Initialize firebase admin.
firebase_admin.initialize_app()

# Initialize firestore client.
db = firestore.client()

# A transaction used to pull batches of items atomically.
transaction = db.transaction()

# A batch to set a batch of results at once.
batch = db.batch()

worker_name = 'Default Worker'


@firestore.transactional
def pull_items(transaction, query_ref, queued_ref, result_ref):
    # Retrieve docs from query
    docs = []
    for doc in query_ref.get(transaction=transaction):
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


def init(name):
    global worker_name
    worker_name = name


def start(queue, handler, max_batch_size=1):
    # Limit to 250 to respect firestore's num transactions limit of 500
    # combining writes and deletes.
    # https://firebase.google.com/docs/firestore/manage-data/transactions
    if max_batch_size > 250:
        raise Exception('max_batch_size must be <= 250')

    queue_col = db.collection(u'queues').document(queue)

    # Create a callback on_snapshot function to capture changes.
    def on_snapshot(docs):
        # Return if there is no new document to process.
        if len(docs) == 0:
            return

        # Process batch.
        tasks = [doc.to_dict()['payload'] for doc in docs]
        results = handler(tasks)

        # Save results.
        for i, result in enumerate(results):
            r_doc = queue_col.collection('results').document(docs[i].id)
            batch.update(
                r_doc, {
                    'task': tasks[i],
                    'result': result,
                    'status': 'complete',
                    'dateComplete': firestore.SERVER_TIMESTAMP
                })
        # Commit updates.
        batch.commit()

    print(f'Listening for new tasks in queue: {queue}'
          f' (max_batch_size: {max_batch_size})')

    query_ref = queue_col.collection('queued').order_by(
        'dateAdded', direction=firestore.Query.ASCENDING).limit(max_batch_size)

    queued_ref = queue_col.collection('queued')
    result_ref = queue_col.collection('results')

    try:
        while True:
            # Pull items using a transaction to make sure no other worker
            # processes the same items.
            docs = pull_items(transaction, query_ref, queued_ref, result_ref)
            if len(docs):
                on_snapshot(docs)
            # TODO: inform that worker is still alive periodically.
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        pass
    print('Closing...')