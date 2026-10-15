import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LocalLLM:
    def __init__(self, name: str, device: str = "cuda", dtype: str = "float16"):
        self.tok = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForCausalLM.from_pretrained(name, dtype=getattr(torch, dtype), device_map=device)
        self.model.eval()

    def complete(self, prompt_text: str, max_new_tokens: int = 400, temperature: float = 0.3, top_p: float = 0.9, stop_strings=None) -> str:
        inputs = self.tok(prompt_text, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p,
                                      do_sample=temperature > 0, pad_token_id=self.tok.eos_token_id,
                                      repetition_penalty=1.15,
                                      stop_strings=stop_strings or [],
                                      tokenizer=self.tok,)
        return self.tok.decode(out[0][inputs["input_ids"].shape[1]:],
                               skip_special_tokens=True).strip()

    def chat(self, messages, max_new_tokens: int = 400, temperature: float = 0.3, top_p: float = 0.9) -> str:
        prompt = self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tok(prompt, return_tensors="pt").to(self.model.device)
        gen_kwargs = dict(max_new_tokens=max_new_tokens, pad_token_id=self.tok.eos_token_id)
        if temperature > 0:
            gen_kwargs.update(temperature=temperature, top_p=top_p, do_sample=True)
        else:
            gen_kwargs.update(do_sample=False)
        with torch.no_grad():
            out = self.model.generate(**inputs, **gen_kwargs)
        return self.tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()