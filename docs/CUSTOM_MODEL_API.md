# RoboLab Custom Model API

This is the model-serving and training layer for a RoboLab-specific model. It is an API and fine-tuning pipeline, **not a pre-trained frontier model**. To obtain a genuinely competitive model, start from a strong code-capable base model and fine-tune it on a high-quality, licensed robotics dataset; then evaluate it against held-out engineering and coding tasks.

## Serve a trained adapter/model

Set:

```env
ROBO_MODEL_ID=robolab-code
ROBO_MODEL_PATH=/models/robolab-code
ROBO_MODEL_API_KEY=change-this-secret
```

Run:

```bash
pip install -r requirements-model-api.txt
python -m robolab_model_api
```

Endpoints:

- `GET /health`
- `GET /v1/models`
- `POST /generate`
- `POST /v1/chat/completions`

## Train a RoboLab adapter

Install training dependencies and run:

```bash
pip install -r requirements-model-training.txt
python training/train_lora.py --base-model <CODE_CAPABLE_BASE_MODEL> --data training/data/robolab_train.jsonl --output artifacts/robolab-adapter
```

The sample dataset is intentionally tiny and is only a schema/example. A production model needs a much larger, carefully curated and licensed dataset, domain-specific evaluations, red-team tests, and repeated training runs.

## Connect RoboLab

Set the main application:

```env
AI_PROVIDER=robolab
ROBO_MODEL_URL=https://YOUR-MODEL-SERVICE
ROBO_MODEL_API_KEY=your-server-secret
AI_MODEL=robolab-code
```

The frontend talks to RoboLab; RoboLab talks to this model gateway. The model gateway is therefore replaceable without changing the RoboLab UI or stage API.
