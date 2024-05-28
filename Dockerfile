FROM runpod/base:0.6.2-cuda11.8.0

RUN pip install runpod && rm -rf /root/.cache/pip
RUN apt-get update \
    && apt-get install -y supervisor aria2 \
    && apt-get clean

RUN git clone https://github.com/ggerganov/llama.cpp \
    && cd llama.cpp \
    && cmake \
    -DLLAMA_CUDA=ON \
    -DLLAMA_NATIVE=OFF \
    -DLLAMA_LTO=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -B build \
    && cd build && make -j$(nproc) && make install \
    && cd / && rm -rf llama-cpp


ARG LLAMA_CPP_MODEL_URL
RUN [ "${LLAMA_CPP_MODEL_URL}" != "" ] && aria2c -s 5 -x 5 -o "/$(basename "${LLAMA_CPP_MODEL_URL}" | cut -d'?' -f1).gguf" "${LLAMA_CPP_MODEL_URL}" || true

COPY /supervisor-conf.d /etc/supervisor/conf.d
COPY /workspace /workspace
COPY --chmod=755 /start.sh /start.sh

EXPOSE 3000

CMD ["/start.sh"]
