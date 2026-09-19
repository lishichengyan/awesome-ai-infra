import nltk
import torch
import torch.nn.functional as F
from torch import nn

nltk.download("gutenberg")
from nltk.corpus import gutenberg

print(gutenberg.fileids())

from attn import Encoder


class TinyTransformerClassifier(nn.Module):
    def __init__(self, vocab_size, d, num_classes):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, d)
        self.encoder = Encoder(d)
        self.classifier = nn.Linear(d, num_classes)

    def forward(self, tokens):
        X = self.embedding(tokens)  # (n,) -> (n, d)
        X = self.encoder(X)  # (n, d)
        X = X.mean(dim=0)  # (n, d) -> (d,)
        logits = self.classifier(X)  # (d,) -> (num_classes,)
        return logits


texts = [
    ("I am happy", "positive"),
    ("I am unhappy", "negative"),
    ("he is really sad", "negative"),
    ("the whether looks pretty good", "positive"),
    ("i cannot put up with this anymore", "negative"),
    ("this is a cup of team", "neutral"),
    ("i am Chinese", "neutral"),
    ("I love you", "positive"),
]

words = set()
for text, _ in texts:
    words.update(text.lower().split())

vocab = {word: i for i, word in enumerate(words)}
labels = {"positive": 0, "negative": 1, "neutral": 2}

print("vocab: ", vocab)

classifier = TinyTransformerClassifier(len(vocab), d=256, num_classes=3)
optimizer = torch.optim.Adam(classifier.parameters(), lr=1e-3)


def train():
    for epoch in range(100):
        total_loss = 0

        for text, label in texts:
            tokens = torch.tensor([vocab[word] for word in text.lower().split()])

            target = torch.tensor(labels[label])

            optimizer.zero_grad()

            logits = classifier(tokens)

            loss = F.cross_entropy(logits.unsqueeze(0), target.unsqueeze(0))

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(epoch, total_loss)


def predict(text):
    tokens = torch.tensor([vocab[word] for word in text.lower().split()])

    with torch.no_grad():
        logits = classifier(tokens)
        pred = logits.argmax(dim=-1).item()

    id_to_label = {v: k for k, v in labels.items()}
    return id_to_label[pred]


train()

for text, _ in texts:
    print(text, "->", predict(text))

print(predict("he is unhappy"))
