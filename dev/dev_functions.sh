# Load node v12
export NVM_DIR="$HOME/.nvm" [ -s "/usr/local/opt/nvm/nvm.sh" ] && . "/usr/local/opt/nvm/nvm.sh"
nvm use 12

# Start Firebase emulator
firebase emulators:start