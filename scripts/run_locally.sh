# export GOOGLE_APPLICATION_CREDENTIALS='/path/to/worker/credentials.json'
# docker build . -t fstq-demo
# docker run -rm \
#     -v $GOOGLE_APPLICATION_CREDENTIALS:'/credentials.json' \
#     -e GOOGLE_APPLICATION_CREDENTIALS='/credentials.json' \
#     fstq-demo -- \
#         --queue 'fstq-demo' \
#         --max_batch_size 5