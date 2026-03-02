import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# =========================
# Device
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[CLIP] Using device: {device}")

# =========================
# Model
# =========================
model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
).to(device)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)

# =========================
# Prompts
# =========================

positive_prompts = [
    "Two plates of Japanese izakaya food on a table",
    "Two beer glasses on a wooden table at a Japanese pub",
    "Dinner table with food for two people in an izakaya",
    "A person sitting across the table in a Japanese restaurant, face not visible",
    "Two sets of chopsticks placed opposite each other",
]

negative_prompts = [
    "One person eating alone at a bar counter",
    "Single beer glass on a table",
    "Only one plate of food on the table",
    "A group of many people drinking together",
    "A family dinner with many dishes and people",
]

all_prompts = positive_prompts + negative_prompts

# =========================
# Prediction
# =========================
def predict(image_path: str) -> float:
    image = Image.open(image_path).convert("RGB")

    inputs = processor(
        text=all_prompts,
        images=image,
        return_tensors="pt",
        padding=True
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image
        probs = logits.softmax(dim=1)[0]

    # ポジティブ平均
    pos_score = probs[:len(positive_prompts)].mean()

    # ネガティブ平均
    neg_score = probs[len(positive_prompts):].mean()

    # 差分スコア
    final_score = (pos_score - neg_score).item()

    print(
        f"[DEBUG] pos={pos_score:.3f} "
        f"neg={neg_score:.3f} "
        f"final={final_score:.3f}",
        flush=True
    )

    return final_score
