import torch
from torchvision import models
from torch.utils.data import Dataset
from torch import nn
from torchvision import transforms


class MobileNet(nn.Module):
    """MobileNetV3(small)"""

    def __init__(self, num_classes):
        super().__init__()
        self.net = models.mobilenet_v3_small()
        self.net.classifier = nn.Linear(576, num_classes)

    def forward(self, x):
        x = self.net(x)
        return x


class Resnet18(nn.Module):
    """Resnet18"""

    def __init__(self, num_classes):
        super().__init__()
        self.net = models.resnet18()
        self.net.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.net(x)
        return x


class Resnet50(nn.Module):
    """Resnet50"""

    def __init__(self, num_classes):
        super().__init__()
        self.net = models.resnet50()
        self.net.fc = nn.Linear(2048, num_classes)

    def forward(self, x):
        x = self.net(x)
        return x


class WellDataset(Dataset):
    def __init__(self, well_imgs, class_idxs):
        self.well_imgs = well_imgs
        self.class_idxs = class_idxs

        self.transforms = transforms.Compose(
            [
                # transforms.Grayscale(num_output_channels=1),
                transforms.ToTensor(),
                transforms.Resize([32, 32]),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomRotation(180),
                transforms.RandomAffine(0, shear=10, scale=(0.8, 1.2)),
            ]
        )

    def __len__(self):
        print("len(self.class_idxs):", len(self.class_idxs))
        return len(self.class_idxs)

    def __getitem__(self, idx):
        img = self.well_imgs[idx] / 255.0
        img = self.transforms(img)
        label = self.class_idxs[idx]
        return img.to(torch.float32), torch.tensor(label).to(torch.float32)
