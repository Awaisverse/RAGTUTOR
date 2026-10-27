"""Local Hugging Face models: no API keys, no network calls at answer time.

  Generator  GEN_MODEL   (default models/Qwen2.5-Math-1.5B-Instruct)
             GEN_ADAPTER (optional LoRA folder produced by train/colab_train.ipynb)
  Vision     VISION_MODEL (default models/Qwen2-VL-2B-Instruct)

Models load lazily on first use and stay in memory. The GPU is used when torch sees one,
otherwise the CPU is used (slow for the generator, but it works).
"""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
GEN_MODEL = os.environ.get("GEN_MODEL", str(ROOT / "models" / "Qwen2.5-Math-1.5B-Instruct"))
GEN_ADAPTER = os.environ.get("GEN_ADAPTER", str(ROOT / "models" / "gen-lora"))
VISION_MODEL = os.environ.get("VISION_MODEL", str(ROOT / "models" / "Qwen2-VL-2B-Instruct"))

_gen = None
_vis = None


def _device_and_dtype():
    import torch
    if torch.cuda.is_available():
        native_bf16 = torch.cuda.get_device_capability()[0] >= 8  # T4 (7.5) has no native bf16: use fp16
        return "cuda", (torch.bfloat16 if native_bf16 else torch.float16)
    return "cpu", torch.bfloat16


def _has_weights(folder):
    """A model folder counts only when its weight files are complete (not a partial download)."""
    p = pathlib.Path(folder)
    return p.is_dir() and any(p.glob("*.safetensors")) and (p / "config.json").exists()


def generator_available():
    return _has_weights(GEN_MODEL)


def vision_available():
    return _has_weights(VISION_MODEL)


def _load_generator():
    global _gen
    if _gen is not None:
        return _gen
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    device, dtype = _device_and_dtype()
    tok = AutoTokenizer.from_pretrained(GEN_MODEL)
    model = AutoModelForCausalLM.from_pretrained(GEN_MODEL, dtype=dtype)
    if GEN_ADAPTER and pathlib.Path(GEN_ADAPTER).exists():
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, GEN_ADAPTER)
        model = model.merge_and_unload()
    model.to(device).eval()
    _gen = (tok, model, device, torch)
    return _gen


def generate(messages, max_new_tokens=2048, temperature=0.0):
    """Greedy decoding by default (deterministic, which matters for maths). temperature > 0 samples, used for a retry
    after a reply failed its own checks. Returns the assistant text."""
    tok, model, device, torch = _load_generator()
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt").to(device)
    opts = {"do_sample": True, "temperature": temperature, "top_p": 0.95} if temperature > 0 else {"do_sample": False}
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, pad_token_id=tok.eos_token_id, **opts)
    return tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def _load_vision():
    global _vis
    if _vis is not None:
        return _vis
    import torch
    from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
    device, dtype = _device_and_dtype()
    proc = AutoProcessor.from_pretrained(VISION_MODEL)
    model = Qwen2VLForConditionalGeneration.from_pretrained(VISION_MODEL, dtype=dtype)
    model.to(device).eval()
    _vis = (proc, model, device, torch)
    return _vis


def read_image(pil_image, instruction, max_new_tokens=1200):
    """Ask the local vision-language model about one image. Returns the assistant text."""
    proc, model, device, torch = _load_vision()
    messages = [{"role": "user", "content": [
        {"type": "image", "image": pil_image},
        {"type": "text", "text": instruction},
    ]}]
    text = proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = proc(text=[text], images=[pil_image], return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    trimmed = out[:, inputs["input_ids"].shape[1]:]
    return proc.batch_decode(trimmed, skip_special_tokens=True)[0]
