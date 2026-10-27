# The hosted model service (service/app.py), for a Hugging Face Space (SDK: docker) or any container host with a GPU.
# The web app on Vercel does not use this file. Models are downloaded from the Hugging Face Hub on first start and cached;
# nothing is trained or copied in. GEN_ADAPTER must be set to the Hub repo that holds the trained LoRA adapter.
FROM python:3.12-slim
WORKDIR /app
COPY requirements-service.txt .
RUN pip install --no-cache-dir -r requirements-service.txt
COPY . .
ENV PORT=7860 \
    WARM=1 \
    HF_HOME=/tmp/hf \
    GEN_MODEL=Qwen/Qwen2.5-Math-1.5B-Instruct \
    VISION_MODEL=Qwen/Qwen2-VL-2B-Instruct
EXPOSE 7860
CMD ["python", "service/app.py"]
