import os
import cv2
import time
import torch
import numpy as np
from torchvision import transforms
from PySide6.QtCore import QThread, Signal

from ._nets import MobileNet, Resnet18, Resnet50, WellDataset


class Extractor:
    def __init__(self, dir, template_path):
        self.dir = dir
        self.t = None
        if os.path.exists(template_path):
            self.t = cv2.imdecode(
                np.fromfile(template_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
            )

    def resetTemplate(self, template_path):
        if os.path.exists(template_path):
            self.t = cv2.imdecode(
                np.fromfile(template_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
            )

    def wellExtract(self, img_name: str):
        match_thre = 0.15

        img_path = os.path.join(self.dir, img_name)
        src_color = cv2.imdecode(
            np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        src_gray = cv2.cvtColor(src_color, cv2.COLOR_BGR2GRAY)

        img_binary = cv2.adaptiveThreshold(
            src_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 10
        )

        result = cv2.matchTemplate(img_binary, self.t, cv2.TM_CCOEFF_NORMED)

        wells_loc = []
        while True:
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
            if maxVal < match_thre:
                break

            wells_loc.append(maxLoc)
            t_h, t_w = self.t.shape[::-1]

            p1 = (maxLoc[0] - t_w // 2, maxLoc[1] - t_h // 2)
            p2 = (maxLoc[0] + t_w // 2, maxLoc[1] + t_h // 2)
            cv2.rectangle(result, p1, p2, 0, thickness=cv2.FILLED)
        return wells_loc


def getWellsTensor(img, wells_loc):
    well_tensors = []
    for loc in wells_loc:
        x, y, w, h = loc
        well = img[y : y + h, x : x + w]
        well = cv2.resize(well, (32, 32))
        well_tensor = torch.from_numpy(well).permute(2, 0, 1).unsqueeze(0).float()
        well_tensor = well_tensor / 255.0
        norm = transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        well_tensor = norm(well_tensor)
        well_tensors.append(well_tensor)

    wells_tensor = torch.cat(well_tensors, dim=0)
    return wells_tensor


class ClassifyThread(QThread):
    finished = Signal()
    complete = Signal(int, int, name="complete")

    def __init__(
        self,
        info_c,
        model_path,
        img_names,
        parent=None,
    ):
        super(ClassifyThread, self).__init__(parent)
        self.is_stop = False

        self.info_c = info_c
        self.model_path = model_path
        self.img_names = img_names
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def isUsingCpu(self):
        return self.device == torch.device("cpu")

    def run(self):
        model = torch.load(self.model_path)
        model.to(self.device)
        model.eval()
        for idx, img_name in enumerate(self.img_names):
            if self.is_stop:
                break
            img_path = self.info_c.P_IMAGE.format(img_name=img_name)
            img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)

            wells_loc = []
            extract_path = self.info_c.P_EXTARCT.format(img_name=img_name)
            with open(extract_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    x, y, w, h, label = map(int, line.split(","))
                    wells_loc.append((x, y, w, h))

            wells = getWellsTensor(img, wells_loc)
            with torch.no_grad():
                wells = wells.to(self.device)
                output = model(wells)
                _, predicted = torch.max(output, 1)

            predicted = predicted.cpu().numpy()
            classified_path = self.info_c.P_CLASSIFIED.format(img_name=img_name)
            with open(classified_path, "w") as f:
                for loc, label in zip(wells_loc, predicted):
                    x, y, w, h = loc
                    f.write(f"{x},{y},{w},{h},{label}\n")

            self.complete.emit(idx + 1, len(self.img_names))

        self.finished.emit()

    def stop(self):
        self.is_stop = True


class TrainThread(QThread):
    finished = Signal()
    complete = Signal(int, int, float, name="complete")

    def __init__(
        self,
        info_c,
        model_path,
        model_type,
        max_epoch,
        batch_size,
        parent=None,
    ):
        super(TrainThread, self).__init__(parent)
        self.is_stop = False

        self.info_c = info_c
        self.model_path = model_path
        self.model_type = model_type
        self.max_epoch = max_epoch
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def isUsingCpu(self):
        return self.device == torch.device("cpu")

    def getDataset(self):
        img_names_edit = self.info_c.getImageNamesByFilter(
            _filter=([True, False], [True, False], [True])
        )
        if len(img_names_edit) == 0:
            raise ValueError("No image for training")  # TODO: add a warning dialog
        well_imgs = []
        class_idxs = []
        for img_name in img_names_edit:
            img_path = self.info_c.P_IMAGE.format(img_name=img_name)
            img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            edit_path = self.info_c.P_EDIT.format(img_name=img_name)
            with open(edit_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    x, y, w, h, label = map(int, line.split(","))
                    well_img = img[y : y + h, x : x + w]
                    well_imgs.append(well_img)
                    class_idxs.append(label)

        dataset = WellDataset(well_imgs, class_idxs)
        return dataset

    def saveModel(self, model):
        model_path = self.info_c.P_MODEL.format(
            model_type=self.model_type, time=self.time_str
        )
        torch.save(model, model_path)

    def run(self):
        self.time_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
        if not self.model_path:
            class_num = len(self.info_c.class_names)
            if self.model_type == "MobileNet":
                model = MobileNet(class_num)
            elif self.model_type == "Resnet18":
                model = Resnet18(class_num)
            elif self.model_type == "Resnet50":
                model = Resnet50(class_num)
            else:
                raise ValueError("Invalid model type")
        else:
            model = torch.load(self.model_path)

        model.to(self.device)
        model.train()
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        dataset = self.getDataset()
        dataloader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=True
        )
        min_loss = 0.0
        for epoch in range(self.max_epoch):
            for i, (inputs, labels) in enumerate(dataloader):
                if self.is_stop:
                    break
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)

                optimizer.zero_grad()
                outputs = model(inputs)
                print(outputs.shape, labels.shape)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                if loss.item() < min_loss:
                    min_loss = loss.item()
                    self.saveModel(model)

                if i % 10 == 0:
                    self.complete.emit(epoch + 1, i + 1, loss.item())
        self.finished.emit()

    def stop(self):
        self.is_stop = True


class AiContainer:
    def __init__(self):
        self.thread = None
