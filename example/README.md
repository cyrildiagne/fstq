# FSTQ Example

## Start a client

- Create a file `client/src/firebase-config.js` that exports your firebase config.
- Run `yarn install`
- Run `yarn run dev`
- Navigate to [http://localhost:8080](http://localhost:8080)

## Start a worker

First setup the credentials.
- Create a service account for your worker with access to firestore
- Download an admin credential json
- `export GOOGLE_APPLICATION_CREDENTIALS=<path/to/credentials/json>`

Setup and launch the worker.
- `cd worker`
- `virtualenv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
