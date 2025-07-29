import torch.nn as nn
import torch.nn.functional as F


class SimpleCNN(nn.Module):
    """Simple CNN architecture for MNIST classification with 2 conv layers"""

    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()

        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 6, kernel_size=3)  # 28x28 -> 26x26
        self.conv2 = nn.Conv2d(6, 10, kernel_size=3)  # 13x13 -> 11x11

        # Pooling layer
        self.pool = nn.MaxPool2d(2, 2)  # Reduces size by half

        # Dropout for regularization
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)

        # Fully connected layers
        self.fc1 = nn.Linear(10 * 5 * 5, 32)
        self.fc2 = nn.Linear(32, num_classes)

    def forward(self, x):
        # First conv block
        x = F.relu(self.conv1(x))
        x = self.pool(x)  # 26x26 -> 13x13

        # Second conv block
        x = F.relu(self.conv2(x))
        x = self.pool(x)  # 11x11 -> 5x5
        x = self.dropout1(x)

        # Flatten for fully connected layers
        x = x.view(-1, 10 * 5 * 5)

        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        x = self.fc2(x)

        return x
