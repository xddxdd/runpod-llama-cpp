#!/bin/sh

if [ "${LLAMA_CPP_MODEL_URL}" != "" ]; then
    MODEL_FILENAME="/$(basename "${LLAMA_CPP_MODEL_URL}" | cut -d'?' -f1).gguf"
    if [ ! -f "${MODEL_FILENAME}" ]; then
        aria2c -s 5 -x 5 -o "${MODEL_FILENAME}" "${LLAMA_CPP_MODEL_URL}"
    fi
fi

exec /usr/bin/supervisord -n
