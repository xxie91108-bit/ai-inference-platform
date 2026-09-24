import torch
import torch.nn as nn


class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)

    def forward(self, x):
        return self.linear(x)


model = SimpleModel()

with torch.no_grad():
    model.linear.weight.fill_(2.0)
    model.linear.bias.fill_(1.0)

model.eval()


# -------------------------
# Model Warm-up
# -------------------------

dummy_input = torch.tensor(
    [[0.0]],
    dtype=torch.float32
)

with torch.inference_mode():
    model(dummy_input)

print("Model warm-up completed")