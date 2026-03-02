import torch
from transformers import AutoProcessor, AutoModel
from PIL import Image
import logging

# ログ抑制
logging.getLogger("transformers").setLevel(logging.ERROR)

# =========================
# Device
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[SigLIP] Using device: {device}", flush=True)

# =========================
# Model（SigLIP）
# =========================
model = AutoModel.from_pretrained(
    "google/siglip-base-patch16-224"
).to(device)

processor = AutoProcessor.from_pretrained(
    "google/siglip-base-patch16-224"
)

# =========================
# Prompts
# =========================

positive_prompts = [
    # レストラン
    "Two plates on a restaurant table facing each other",
    "Dinner table set for two people with two glasses",
    "A woman sitting across the table, her face not visible",

    # 居酒屋
    "Two beer glasses on a wooden table at a Japanese izakaya",
    "Two sets of chopsticks placed opposite each other",

    # カフェ
    "A cafe table with desserts for two people",
    "Two drinks and pancakes on a table",
    "Brunch date with someone sitting opposite",
    "Another person's arm visible across the table",
    "Two forks placed on a dessert table",

    # 家ディナー
    "Someone cutting food with a knife across the table",
    "A dinner scene with another person eating",
    "A romantic dinner at home with someone sitting opposite",
    "A person using a knife at the dinner table across from you",
    "A home dinner with a partner",
]

negative_prompts = [
    "A clearly solo dining scene with only one plate visible",
    "A person eating completely alone at a table",
    "Solo dining with only one chair visible",
    "A selfie while eating alone",
    "A large group of many people at a party",
]

all_prompts = positive_prompts + negative_prompts


# =========================
# Prediction（Sigmoid独立評価）
# =========================
def predict(image_path: str) -> float:
    image = Image.open(image_path).convert("RGB")

    inputs = processor(
        text=all_prompts,
        images=image,
        return_tensors="pt",
        padding="max_length"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image

        # SigLIPはsoftmaxではなくsigmoid
        probs = torch.sigmoid(logits)[0]

    # 上位2つを平均
    pos_score = probs[:len(positive_prompts)].topk(2).values.mean()
    neg_score = probs[len(positive_prompts):].topk(2).values.mean()

    final_score = (pos_score - neg_score).item()

    print(
        f"[DEBUG] pos={pos_score:.3f} "
        f"neg={neg_score:.3f} "
        f"final={final_score:.3f}",
        flush=True
    )

    # どのプロンプトが効いているか確認
    for i, p in enumerate(all_prompts):
        print(f"{probs[i]:.3f} : {p}", flush=True)

    return final_score
