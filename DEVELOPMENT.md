## Dev Functions:

Install the dependencies

```sh
cd functions
yarn install
```

Start the firebase emulator

```sh
# Load node v12
export NVM_DIR="$HOME/.nvm" [ -s "/usr/local/opt/nvm/nvm.sh" ] && . "/usr/local/opt/nvm/nvm.sh"
nvm use 12

# Start Firebase emulator
firebase emulators:start
```

## Dev Client Lib:

Install dependencies, link the lib and start the client lib

```sh
cd lib/client-js
yarn install
yarn link
yarn run dev
```

Link the lib and run the client example

```sh
cd example/client
yarn install
yarn link fstq
yarn run dev
```

## Dev Worker:

Install the worker lib as an editable package

```sh
pip install -e lib/worker-python
```

Point firebase_admin to the firestore emulator

```sh
export FIRESTORE_EMULATOR_HOST='localhost:8000'
```

Run the example

```sh
cd example/worker
python main.py
```

### With Docker:

```sh
cp -r ../../lib/worker-python .fstq
fstq run --queue 'my-queue' --credentials '/path/to/credentials.json'
rm -rf .fstq
```
