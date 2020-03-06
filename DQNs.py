import torch.nn as nn
import torch.nn.functional as F
import torch

class DQN(nn.Module):
    def __init__(self, img_height, img_width):
        super().__init__()

        self.fc1 = nn.Linear(in_features=img_height * img_width * 3, out_features=24)
        self.fc2 = nn.Linear(in_features=24, out_features=32)
        self.out = nn.Linear(in_features=32, out_features=2)

    def forward(self, t):
        t = t.flatten(start_dim=1)
        t = F.relu(self.fc1(t))
        t = F.relu(self.fc2(t))
        t = self.out(t)
        return t

class DQN_CNN1(nn.Module):
    def __init__(self, cfg, num_classes = 4, init_weights=True):
        super().__init__()

        self.cfg = cfg
        self.cnn = self.make_layers(batch_norm=False)
        self.classifier = nn.Sequential(nn.Linear(256,256),
                                        nn.ReLU(True),
                                        nn.Linear(256,num_classes)
                                        )
        # nn.Dropout(0.3),  # BZX: optional [TRY]
        if init_weights:
            self._initialize_weights()

    def forward(self, x):
        x = self.cnn(x)
        x = torch.flatten(x, start_dim=1)
        x = self.classifier(x)
        return x

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def make_layers(self, batch_norm=False):
        '''
        Return a nn.Sequential object containing all layers before the fully-connected layers in the VGG11 network.

        Args:
          cfg: list
          batch_norm: bool, default: False. If set to True, a BatchNorm layer should be added after each convolutional layer.

        Return:
          features: torch.nn.Sequential. Containers for all feature extraction layers. For use of torch.nn.Sequential, please refer to PyTorch documents.
        '''
        layers = []
        tmp_channel = 0
        for i, layer in enumerate(self.cfg):
            if isinstance(layer, int):
                if i == 0:  # first conv layer
                    layers.append(nn.Conv2d(4, layer, kernel_size=3, padding=1)) #first input channel should be 4
                    tmp_channel = layer
                else:
                    layers.append(nn.Conv2d(tmp_channel, layer, kernel_size=3, padding=1))
                    tmp_channel = layer
                    # BN-ReLU
                if batch_norm:
                    layers.append(nn.BatchNorm2d(layer))
                layers.append(nn.ReLU(True))
            else:  # "M"
                layers.append(nn.MaxPool2d(2))

        features = nn.Sequential(*layers)

        return features