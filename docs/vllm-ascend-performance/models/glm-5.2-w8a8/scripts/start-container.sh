#!/usr/bin/env bash
#
# GLM-5.2-W8A8 Container Creation (User-verified baseline)
# Do not modify this command without creating a new Decision and updating BASELINE.md
#

set -euo pipefail

CONTAINER_NAME="model-test-zyg-a3"
IMAGE="quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3"

echo "Checking if container already exists..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Container '${CONTAINER_NAME}' already exists."
  echo "To recreate, first run: docker rm -f ${CONTAINER_NAME}"
  exit 1
fi

echo "Creating container: ${CONTAINER_NAME}"
echo "Image: ${IMAGE}"

docker run -itd \
  --name=model-test-zyg-a3 \
  --privileged=true \
  --net=host \
  --shm-size=512g \
  --device /dev/davinci0 \
  --device /dev/davinci1 \
  --device /dev/davinci2 \
  --device /dev/davinci3 \
  --device /dev/davinci4 \
  --device /dev/davinci5 \
  --device /dev/davinci6 \
  --device /dev/davinci7 \
  --device /dev/davinci8 \
  --device /dev/davinci9 \
  --device /dev/davinci10 \
  --device /dev/davinci11 \
  --device /dev/davinci12 \
  --device /dev/davinci13 \
  --device /dev/davinci14 \
  --device /dev/davinci15 \
  --device /dev/davinci_manager \
  --device /dev/devmm_svm \
  --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /etc/hccn.conf:/etc/hccn.conf \
  -v /data/tiankuan:/data/tiankuan \
  -v /home:/home \
  quay.io/ascend/vllm-ascend:nightly-releases-v0.24.0rc-a3 \
  /bin/bash

echo "Container created successfully: ${CONTAINER_NAME}"
echo "To enter: docker exec -it ${CONTAINER_NAME} bash"
