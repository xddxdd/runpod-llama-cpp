FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

RUN pip install runpod && rm -rf /root/.cache/pip
RUN apt-get update \
    && apt-get install -y supervisor \
    && apt-get clean

RUN git clone https://github.com/ggerganov/llama.cpp \
    && cd llama.cpp \
    && cmake \
    -DLLAMA_CUDA=ON \
    -DLLAMA_NATIVE=OFF \
    -DLLAMA_LTO=ON \
    -DLLAMA_AVX=ON \
    -DLLAMA_AVX2=ON \
    -DLLAMA_FMA=ON \
    -DLLAMA_F16C=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -B build \
    && cd build && make -j$(nproc) && make install \
    && cd / && rm -rf llama-cpp


ARG LLAMA_CPP_MODEL_URL
RUN curl -L "${LLAMA_CPP_MODEL_URL}" -o /model.gguf

COPY /supervisor-conf.d /etc/supervisor/conf.d
COPY /workspace /workspace

CMD ["/usr/bin/supervisord", "-n"]
