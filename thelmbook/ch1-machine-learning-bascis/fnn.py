import os

import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

inputs = torch.tensor(
    [
        [22, 25],
        [25, 35],
        [47, 80],
        [52, 95],
        [46, 82],
        [56, 90],
        [23, 27],
        [30, 50],
        [40, 60],
        [39, 57],
        [53, 95],
        [48, 88],
    ],
    dtype=torch.float32,
)

labels = torch.tensor(
    [[0], [0], [1], [1], [1], [1], [0], [1], [1], [0], [1], [1]], dtype=torch.float32
)

print("inputs shape: ", inputs.shape)


def show_dataset():
    plt.scatter(inputs[:, 0], inputs[:, 1], c=labels.squeeze())
    plt.xlabel("feature 1")
    plt.ylabel("feature 2")
    plt.title("Dataset")
    plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.png"))
    plt.show()


class SimpleFNN:
    def __init__(self):
        self.model = nn.Sequential(nn.Linear(inputs.shape[1], 1), nn.Sigmoid())

        self.optimizer = optim.SGD(self.model.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()  # binary cross-entropy loss
        self.losses = []

    def train(self):
        for step in range(500):
            self.optimizer.zero_grad()
            loss = self.criterion(self.model(inputs), labels)
            loss.backward()
            self.optimizer.step()
            self.losses.append(loss.item())

    def plot_loss(self):
        plt.plot(self.losses)
        plt.xlabel("step")
        plt.ylabel("loss")
        plt.title("Training loss")
        plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "loss.png"))
        plt.show()

    def predict(self, samples):
        self.model.eval()
        with torch.no_grad():
            return self.model(samples)


# model = SimpleFNN()
# show_dataset()
# model.train()
# model.plot_loss()

# samples = torch.tensor([
#     [24, 30], [50, 90], [35, 55]
# ], dtype=torch.float32)

# predictions = model.predict(samples)

# print(predictions)


class SimpleFNNRewritten(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(inputs.shape[1], 1)
        self.sigmoid = nn.Sigmoid()

        self.optimizer = optim.SGD(self.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()  # binary cross-entropy loss
        self.losses = []

    def forward(self, x):
        return self.sigmoid(self.linear(x))

    def fit(self):
        for step in range(500):
            self.optimizer.zero_grad()
            loss = self.criterion(self(inputs), labels)
            loss.backward()
            self.optimizer.step()
            self.losses.append(loss.item())

    def plot_loss(self):
        plt.plot(self.losses)
        plt.xlabel("step")
        plt.ylabel("loss")
        plt.title("Training loss")
        plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "loss.png"))
        plt.show()


samples = torch.tensor([[24, 30], [50, 90], [35, 55]], dtype=torch.float32)

model2 = SimpleFNNRewritten()
model2.fit()
model2.plot_loss()

model2.eval()
with torch.no_grad():
    predictions2 = model2(samples)

print(predictions2)
