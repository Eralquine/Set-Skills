---
name: omnivoice
description: Generate speech (TTS) with OmniVoice — zero-shot voice cloning from a short reference clip, or voice design from attributes (gender/age/pitch/accent/dialect), across 600+ languages. Use whenever the user wants to synthesize speech, clone a voice from an audio sample, or design a voice by description, and hasn't already named a specific TTS provider. Local, open-source (k2-fsa/OmniVoice), no API key — needs a GPU (or Apple Silicon/Intel Arc) and PyTorch.
---

# OmniVoice (k2-fsa/OmniVoice)

Massively multilingual zero-shot TTS (600+ languages, diffusion-language-model
architecture). Runs locally — no API key, no per-request cost — but needs
PyTorch and, realistically, a GPU (CPU works but is slow); it downloads model
weights from Hugging Face (`k2-fsa/OmniVoice`) on first use.

## Setup (first use in a session)

```bash
python3 -c "import omnivoice" 2>/dev/null || pip install omnivoice
```

Needs PyTorch installed first, matching the hardware:
- NVIDIA GPU: `pip install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu128` (match the CUDA version)
- Apple Silicon: `pip install torch torchaudio` (use `device_map="mps"`)
- Intel Arc (XPU): see the repo's XPU install notes (`device_map="xpu"`, no `flash_attn`, falls back to SDPA)
- No GPU: CPU works but is slow — fine for a quick one-off, not for batches

If HuggingFace downloads are slow/blocked, set `export HF_ENDPOINT="https://hf-mirror.com"` first.

## Three generation modes

All three use the same `model.generate()` call — pick by what the user gave you (a reference clip → clone, a description → design, neither → auto).

**Voice cloning** — clone from a short (3-10s) reference clip:
```python
from omnivoice import OmniVoice
import soundfile as sf, torch

model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)
audio = model.generate(text="Hello, this is a test.", ref_audio="ref.wav", ref_text="Transcription of ref.wav.")
sf.write("out.wav", audio[0], 24000)
```
`ref_text` is optional — omitted, OmniVoice auto-transcribes `ref_audio` with Whisper. To reuse a cloned voice across sessions without re-encoding: `model.create_voice_clone_prompt(...).save("voice.pt")`, then `VoiceClonePrompt.load("voice.pt")` later.

**Voice design** — describe the voice, no reference audio (see `references/voice-design.md` for the full attribute table — gender, age, pitch, style, English accent, Chinese dialect):
```python
audio = model.generate(text="...", instruct="female, young adult, high pitch, british accent")
```

**Auto voice** — omit both `ref_audio` and `instruct`; the model picks a voice.

## CLI (same features, no Python needed)

```bash
omnivoice-demo --ip 0.0.0.0 --port 8001              # web UI
omnivoice-infer --model k2-fsa/OmniVoice --text "..." --ref_audio ref.wav --output out.wav       # clone
omnivoice-infer --model k2-fsa/OmniVoice --text "..." --instruct "male, british accent" --output out.wav  # design
omnivoice-infer-batch --model k2-fsa/OmniVoice --test_list test.jsonl --res_dir results/  # batch, multi-GPU
```
Batch mode takes a JSONL file, one object per line: `{"id", "text"}` mandatory, plus optional `ref_audio`, `ref_text`, `instruct`, `language_id`, `duration`, `speed`.

## Fine-grained control

- **Non-verbal tags** inline in text: `[laughter]`, `[sigh]`, `[confirmation-en]`, `[question-en/ah/oh/ei/yi]`, `[surprise-ah/oh/wa/yo]`, `[dissatisfaction-hnn]`.
- **Pronunciation**: Chinese via pinyin+tone number inline (`ZHE4`), English via CMU dict in brackets (`[B EY1 S]`).
- **Number normalization**: pass `normalize_text=True` (needs `pip install "omnivoice[tn]"`) so "2345" reads as words instead of digit-by-digit.
- Full parameter list (num_step, guidance_scale, duration vs speed, chunking for long-form) in `references/generation-parameters.md`.

## Before you generate

- Check `references/tips.md` for known gotchas: short clips (<2s) need a reference audio to be reliable; Min Nan Chinese (Hokkien) needs Tai-lo romanization, not characters; conflicting `ref_audio` + `instruct` favors the reference audio's style.
- Check `references/languages.md` if the target language is anything other than mainstream English/Chinese — it lists all 646 supported languages with their OmniVoice language ID.
- Voice design is trained on Chinese/English; other languages may be unstable — say so rather than promising quality you haven't seen.

## Responsible use

Voice cloning from a reference clip can reproduce a real person's voice.
Only clone a voice with the speaker's consent (their own recording, or
material they've authorized) — don't clone a voice to impersonate someone
without it.

## Source

[k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice) — Apache 2.0, model on
[Hugging Face](https://huggingface.co/k2-fsa/OmniVoice), paper on
[arXiv](https://arxiv.org/abs/2604.00688). Training/fine-tuning docs exist in
the repo (`docs/training.md`, `docs/lora_finetuning.md`) but aren't included
here — this skill covers inference only.
