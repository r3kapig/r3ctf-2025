import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from datasets import load_dataset
import numpy as np
from PIL import Image
import time
from model import SimpleCNN
import random


class MNISTDataset(Dataset):
    """Custom Dataset class for MNIST data from HuggingFace datasets"""

    def __init__(self, split="train", transform=None):
        self.dataset = load_dataset("mnist")[split]  # type: ignore
        self.index = list(range(len(self.dataset)))
        random.shuffle(self.index)
        self.transform = transform

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[self.index[idx]]
        image = item["image"]
        label = item["label"]

        # Convert PIL image to numpy array and normalize
        image_array = np.array(image, dtype=np.float32) / 255.0

        # Add channel dimension (1, 28, 28)
        image_tensor = torch.from_numpy(image_array).unsqueeze(0)

        return image_tensor, torch.tensor(label, dtype=torch.long)


class MNISTClassifier:
    """Main classifier class that handles training and evaluation"""

    def __init__(self, learning_rate=0.001, batch_size=64, device=None):
        self.device = (
            device
            if device
            else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.batch_size = batch_size
        self.learning_rate = learning_rate

        # Initialize model
        self.model = SimpleCNN().to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        # self.optimizer = optim.SGD(self.model.parameters(), lr=learning_rate)

        print(f"Using device: {self.device}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")

    def prepare_data(self):
        """Prepare train and test data loaders"""
        print("Loading MNIST dataset...")

        train_dataset = MNISTDataset("test")
        test_dataset = MNISTDataset("test")

        self.train_loader = DataLoader(
            train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=2
        )

        self.test_loader = DataLoader(
            test_dataset, batch_size=self.batch_size, shuffle=False, num_workers=2
        )

        print(f"Training samples: {len(train_dataset)}")
        print(f"Test samples: {len(test_dataset)}")

    def train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)

            # Zero gradients
            self.optimizer.zero_grad()

            # Forward pass
            output = self.model(data)
            # probabilities = F.softmax(output, dim=1)
            # loss = self.criterion(probabilities, target)
            loss = self.criterion(output, target)

            # Backward pass
            loss.backward()
            self.optimizer.step()

            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()

            if batch_idx % 200 == 0:
                print(
                    f"Batch {batch_idx}/{len(self.train_loader)}, "
                    f"Loss: {loss.item():.4f}, "
                    f"Acc: {100.*correct/total:.2f}%"
                )

        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = 100.0 * correct / total

        return epoch_loss, epoch_acc

    def evaluate(self):
        """Evaluate on test set"""
        self.model.eval()
        test_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in self.test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                # probabilities = F.softmax(output, dim=1)
                # test_loss += self.criterion(probabilities, target).item()
                test_loss += self.criterion(output, target).item()

                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()

        test_loss /= len(self.test_loader)
        test_acc = 100.0 * correct / total

        print(f"{correct} / {total} = {test_acc}")
        return test_loss, test_acc

    def train(self, epochs=5):
        """Train the model for specified number of epochs"""
        print(f"\nStarting training for {epochs} epochs...")
        print("-" * 50)

        best_acc = 0

        for epoch in range(epochs):
            start_time = time.time()

            # Train
            train_loss, train_acc = self.train_epoch()

            # Evaluate
            test_loss, test_acc = self.evaluate()

            epoch_time = time.time() - start_time

            print(f"\nEpoch {epoch+1}/{epochs}:")
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            print(f"Test Loss: {test_loss:.4f}, Test Acc: {test_acc:.2f}%")
            print(f"Time: {epoch_time:.2f}s")
            print("-" * 50)

            if test_acc >= 100.0:
                break

            # Save best model
            if test_acc > best_acc:
                best_acc = test_acc
                self.save_model("best_mnist_cnn.pth")
                print(f"New best accuracy: {best_acc:.2f}% - Model saved!")

        print(f"\nTraining completed! Best test accuracy: {best_acc:.2f}%")

    def save_model(self, filepath):
        """Save model state"""
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
            },
            filepath,
        )

    def load_model(self, filepath):
        """Load model state"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        # self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        print(f"Model loaded from {filepath}")

    def predict_single(self, image):
        """Predict a single image"""
        self.model.eval()

        if isinstance(image, Image.Image):
            image_array = np.array(image, dtype=np.float32) / 255.0
            image_tensor = torch.from_numpy(image_array).unsqueeze(0).unsqueeze(0)
        else:
            image_tensor = image.unsqueeze(0) if image.dim() == 3 else image

        image_tensor = image_tensor.to(self.device)

        with torch.no_grad():
            output = self.model(image_tensor)
            probabilities = F.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()  # type: ignore

        return predicted_class, confidence


def main():
    # Initialize classifier
    classifier = MNISTClassifier(learning_rate=1e-4, batch_size=71)

    # Prepare data
    classifier.prepare_data()

    classifier.load_model("best_mnist_cnn.pth")

    # Train the model
    classifier.train(epochs=2000)

    # Final evaluation
    print("\nFinal Evaluation:")
    test_loss, test_acc = classifier.evaluate()
    print(f"Final Test Accuracy: {test_acc:.2f}%")

    # Example prediction on a few test samples
    print("\nExample predictions:")
    test_dataset = MNISTDataset("test")
    for i in range(5):
        image, true_label = test_dataset[i]
        predicted_label, confidence = classifier.predict_single(image)
        print(
            f"Sample {i+1}: True={true_label}, Predicted={predicted_label}, Confidence={confidence:.3f}"
        )


if __name__ == "__main__":
    main()
