import time
import firebase_admin
from firebase_admin import firestore

# Initialize firebase admin.
firebase_admin.initialize_app()

# Initialize firestore client.
db = firestore.client()


def start(queue, handler):
    queue_col = db.collection(u'queues').document(queue)

    # Create a callback on_snapshot function to capture changes.
    def on_snapshot(doc_snapshot, changes, read_time):
        print(f'snapshot - {len(doc_snapshot)} - {len(changes)}')
        docs = [
            change.document for change in changes
            if change.type.name == 'ADDED'
        ]

        # Return if no new document has been added.
        if len(docs) == 0:
            return

        # Process batch.
        tasks = [doc.to_dict()['payload'] for doc in docs]
        results = handler(tasks)

        # Save results.
        for i, result in enumerate(results):
            id_ = docs[i].id
            try:
                doc = queue_col.collection('results').document(id_)
                doc.set(
                    {
                        'task': tasks[i],
                        'result': result,
                        'status': 'complete',
                        'dateComplete': firestore.SERVER_TIMESTAMP
                    },
                    merge=True)
            except Exception as e:
                print(e)

            # Remove queued document.
            queue_col.collection('queued').document(id_).delete()

    queue_col.collection('queued').on_snapshot(on_snapshot)

    print(f'Listening for new tasks in queue: {queue}')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        pass
    print('Closing...')