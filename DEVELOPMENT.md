## Dev Functions:

```sh
cd functions
yarn install
```


```sh
# Load node v12
export NVM_DIR="$HOME/.nvm" [ -s "/usr/local/opt/nvm/nvm.sh" ] && . "/usr/local/opt/nvm/nvm.sh"
nvm use 12

# Start Firebase emulator
firebase emulators:start
```

## Dev Client Lib:

```sh
cd lib/client-js
yarn install
yarn link
yarn run dev
```

```sh
cd example/client
yarn install
yarn link fstq
yarn run dev
```

## Dev Worker:

