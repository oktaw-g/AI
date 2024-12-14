# -*- coding: utf-8 -*-
"""P5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ER6LWos-ogDO3u7v6hzvk-r-ibFAoOoY

#Wczytanie danych z biblioteki TorchVision

Zmiana normalize na znaleziony w internecie
Wycięcie środka ze zdjęć, stracono po 2 piksele na bokach, więc można pominąć, wczytujemy CIFAR10
"""

from torchvision.datasets import CIFAR10
import torchvision.transforms as transforms
import numpy as np
from torch.utils.data import DataLoader


# transformacje dla pre-processingu
transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
        #transforms.Resize((28,28))
        #transforms.CenterCrop(28)
    ]
)

# FashionMNIST dataset
train_dataset = CIFAR10(root='./data', train=True, download=True, transform=transform)
test_dataset = CIFAR10(root='./data', train=False, download=True, transform=transform)

# Data loader
batch_size = 32

train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

"""#EDA

zmiana labeli, nie wiem jak działa tutaj imshow, to bez zmian, grunt, że wyświetla
"""

from matplotlib import pyplot as plt
LABELS = {
  0: "airplane",
  1: "automobile",
  2: "bird",
  3: "cat",
  4: "deer",
  5: "dog",
  6: "frog",
  7: "horse",
  8: "ship",
  9: "truck"
}

fig, axes = plt.subplots(ncols=3, nrows=5, figsize=(4, 5))
axes = axes.flatten()

for i,(img, label) in enumerate(train_dataset):
  if i >= 15: break

  axes[i].imshow(img[0, :, :], cmap="gray")
  axes[i].axis("off")
  axes[i].set_title(LABELS[label])

plt.tight_layout()
plt.show()

"""#Definiowane dwóch modeli konwolucyjnych"""

# WŁASNA SIEĆ NEURONOWA


import torch
import torch.nn as nn
import torch.nn.functional as F


class CustomCNN(nn.Module):
    def __init__(self):
        super().__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=8, kernel_size=3)  # 32x32 -> 30x30
        self.conv2 = nn.Conv2d(in_channels=8, out_channels=16, kernel_size=3) # 30x30 -> 28x28
        # Pooling layer
        self.pool = nn.AvgPool2d(2, 2)  # Pooling: 28x28 -> 14x14 -> 12x12 -> 6x6
        # Fully connected layers
        self.fc1 = nn.Linear(16 * 6 * 6, 128)  # Adjusted for the output size
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # 32x32 -> 30x30 -> 15x15
        x = self.pool(F.relu(self.conv2(x)))  # 15x15 -> 13x13 -> 6x6
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


model_custom = CustomCNN()

# RESNET18

from torchvision.models import resnet18, ResNet18_Weights

# Load pre-trained ResNet18
model_resnet = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

# Modify the first convolutional layer for 32x32 input
model_resnet.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)



# Print the modified model for verification
print(model_resnet)

print(f"Custom model: {sum(p.numel() for p in model_custom.parameters() if p.requires_grad)} trenowalnych parametrów")

print(f"ResNet18: {sum(p.numel() for p in model_resnet.parameters() if p.requires_grad)} trenowalnych parametrów")

!pip install torchview
from torchview import draw_graph

model_visualizer = draw_graph(model_custom, input_size=(batch_size, 3, 32, 32)) # input_size=(batch_size, 1, 28, 28) - rozmiar wejściowy (B, C, H, W)
# na 3 channele, bo kolory, rozmiar zdjęć zjechaliśmy z 32 na 28 więc zostawiamy
model_visualizer.visual_graph

model_visualizer = draw_graph(model_resnet, input_size=(batch_size, 3, 32, 32)) # input_size=(batch_size, 1, 28, 28) - rozmiar wejściowy (B, C, H, W), to samo co wyżej
model_visualizer.visual_graph

"""#Trenowanie modeli"""

def plot_loss(train_loss, val_loss, val_accuracy, save_name):

    fig, axes = plt.subplots(ncols=2, figsize=(8, 4))


    axes[0].plot(val_loss, marker='.', label='Validation')
    axes[0].plot(train_loss, marker='.', label='Train')
    axes[1].plot(val_accuracy, marker='.', label='Validation')

    axes[0].legend()
    axes[1].legend()

    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")

    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")

    fig.tight_layout()
    fig.show()

    fig.savefig(save_name, dpi=300, bbox_inches='tight')

from torch import optim
from tqdm import tqdm

def train(model, save_name, epochs=5):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters())

    train_loss = []
    val_loss = []
    val_accuracy = []

    for epoch in range(epochs):

        model.train()
        losses = []

        for i, (inputs, labels) in tqdm(enumerate(train_dataloader, 0),desc=f"[{epoch + 1}/{epochs}] Training"):

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            losses.append(loss.item())

        train_loss.append(np.mean(losses))

        # validation loss
        model.eval()
        losses = []
        correct_preds = 0

        for i, (inputs, labels) in tqdm(enumerate(test_dataloader),desc=f"[{epoch + 1}/{epochs}] Validation"):
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            losses.append(loss.item())
            correct_preds += (outputs.argmax(dim=1) == labels).float().mean().item()

        val_accuracy.append(correct_preds/len(test_dataloader))
        val_loss.append(np.mean(losses))

        # print loss
        print(f'\ttrain loss: {train_loss[-1]:.4f} | val loss: {val_loss[-1]:.4f}| val acc.: {val_accuracy[-1]*100.0:.2f}\n')

    torch.save(model.state_dict(), save_name)

    return train_loss, val_loss, val_accuracy

train_loss, val_loss, val_accuracy = train(model_custom, 'model_custom.pth', epochs=10)

plot_loss(train_loss, val_loss, val_accuracy, 'model_custom.png')

"""**Resnet**"""

train_loss, val_loss, val_accuracy = train(model_resnet, 'model_resnet.pth', epochs=10)

plot_loss(train_loss, val_loss, val_accuracy, 'model_resnet.png')

del model_custom, model_resnet

"""#Walidacja"""

# 1.6. Czytanie modelu

model_custom = CustomCNN()
model_resnet = resnet18()
model_resnet.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)

model_custom.load_state_dict(torch.load("model_custom.pth", weights_only=True))
model_resnet.load_state_dict(torch.load("model_resnet.pth", weights_only=True))

# Prosta ewaluacja - ACCURACY / DOKŁADNOŚĆ modelu (globalna)

def evaluate(model):
    correct_preds = 0

    model.eval()
    with torch.no_grad():
        for images, labels in test_dataloader:
            correct_preds += (model(images).argmax(dim=1) == labels).float().mean().item()

    accuracy = correct_preds * 100 / len(test_dataloader)

    print(f'Global accuracy on test set: {accuracy:.2f}%')

print("Custom model:")
evaluate(model_custom)

"""**Resnet**"""

print("ResNet18:")
evaluate(model_resnet)

# Confusion matrix / macierz pomyłek
# Jak model radzi sobie z poszczególnymi klasami

def confusion_matrix(model, n_classes=10):
    matrix = np.zeros((n_classes, n_classes),dtype=int)

    model.eval()
    with torch.no_grad():
        for images, labels in test_dataloader:

            predicted = torch.max(model(images).data, 1)[1]

            for p,l in zip(predicted, labels):
                p,l = p.item(), l.item()
                matrix[p,l] += 1

    return matrix

matrix_custom = confusion_matrix(model_custom)

"""**Resnet**"""

matrix_resnet = confusion_matrix(model_resnet)

fig,ax = plt.subplots(1,2, figsize=(10,5))
ax[0].imshow(matrix_custom, cmap='Blues')
ax[0].set_title("Custom CNN")
ax[0].set_xticks(list(LABELS.keys()))
ax[0].set_yticks(list(LABELS.keys()))

ax[0].set_ylabel("Predicted")
ax[0].set_xlabel("Ground Truth")

for i in range(10):
    for j in range(10):
        ax[0].text(j, i, matrix_custom[i, j], ha="center", va="center", color="black", fontsize=8)


ax[1].imshow(matrix_resnet, cmap='Blues')
ax[1].set_title("ResNet18")
ax[1].set_xticks(list(LABELS.keys()))
ax[1].set_yticks(list(LABELS.keys()))

ax[1].set_ylabel("Predicted")
ax[1].set_xlabel("Ground Truth")

for i in range(10):
    for j in range(10):
        ax[1].text(j, i, matrix_resnet[i, j], ha="center", va="center", color="black", fontsize=8)

plt.show()

# Analiza macierzy pomyłek
# Wyznaczenie metryk dla poszczególnych klas
# Wyznaczenie metryk globalnych - uśrednienie po klasach

def analyze_matrix(matrix):
    global_res = {"accuracy": np.zeros(matrix.shape[0]), "precision": np.zeros(matrix.shape[0]), "recall": np.zeros(matrix.shape[0]), "f1": np.zeros(matrix.shape[0])}
    for i,c in LABELS.items():
        print(f'{c}:')
        tp = matrix[i,i]
        fp = np.sum(matrix[i,:]) - tp
        fn = np.sum(matrix[:,i]) - tp
        tn = np.sum(matrix) - tp - fp - fn

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * precision * recall / (precision + recall)
        accuracy = (tp+tn) / (tp+fp+fn+tn)

        global_res["accuracy"][i] = accuracy
        global_res["precision"][i] = precision
        global_res["recall"][i] = recall
        global_res["f1"][i] = f1

        print(f'\taccuracy: {accuracy*100.0:.2f}, precision: {precision*100.0:.2f}, recall: {recall*100.0:.2f}, F1: {f1*100.0:.2f}')

    print(f'-------------\nGlobal (macro) results:')
    print(f'\taccuracy: {np.mean(global_res["accuracy"])*100.0:.2f}, precision: {np.mean(global_res["precision"])*100.0:.2f}, recall: {np.mean(global_res["recall"])*100.0:.2f}, F1: {np.mean(global_res["f1"])*100.0:.2f}')

analyze_matrix(matrix_custom)

"""**Resnet**"""

analyze_matrix(matrix_resnet)