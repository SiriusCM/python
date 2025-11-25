import matplotlib.pyplot
import torch
import torchvision

transform = torchvision.transforms.ToTensor()
train_dataset = torchvision.datasets.MNIST("", True, transform=transform, download=True)
test_dataset = torchvision.datasets.MNIST("", False, transform=transform, download=True)

train_data = torch.utils.data.DataLoader(train_dataset, batch_size=100, shuffle=True)
test_data = torch.utils.data.DataLoader(test_dataset, batch_size=100, shuffle=True)

device = torch.device("cuda:0")
# device = torch.device("cpu")


class VisionModel(torch.nn.Module):

    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(28 * 28, 64)
        self.fc2 = torch.nn.Linear(64, 64)
        self.fc3 = torch.nn.Linear(64, 64)
        self.fc4 = torch.nn.Linear(64, 10)

    def forward(self, i):
        i = torch.nn.functional.relu(self.fc1.forward(i))
        i = torch.nn.functional.relu(self.fc2.forward(i))
        i = torch.nn.functional.relu(self.fc3.forward(i))
        o = torch.nn.functional.log_softmax(self.fc4.forward(i), dim=1)
        return o


def vision_evaluate(model: VisionModel):
    n_correct = 0
    n_total = 0
    with torch.no_grad():
        for (img, label) in test_data:
            img = img.to(device)
            predicts = model.forward(img.view(100, 28 * 28))
            for i, predict in enumerate(predicts):
                if torch.argmax(predict) == label[i]:
                    n_correct += 1
                n_total += 1
    return n_correct / n_total


def vision_train(times: int):
    model = VisionModel().to(device)
    print("initial accuracy:", vision_evaluate(model))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(times):
        for (img, label) in train_data:
            img = img.to(device)
            label = label.to(device)

            model.zero_grad()
            predicts = model.forward(img.view(-1, 28 * 28))

            loss = torch.nn.functional.nll_loss(predicts, label)
            loss.backward()

            optimizer.step()
        print("epoch", epoch, "accuracy:", vision_evaluate(model))
    return model


def vision_test(model: VisionModel):
    model.eval()
    for (batch, (img, label)) in enumerate(test_data):
        if batch > 3:
            break

        x = img[0].to(device)
        predict = model.forward(x.view(-1, 28 * 28))
        label = torch.argmax(predict)

        matplotlib.pyplot.figure(batch)
        matplotlib.pyplot.imshow(img[0].view(28, 28))
        matplotlib.pyplot.title("prediction: " + str(int(label)))
    matplotlib.pyplot.show()


def main():
    model = vision_train(5)
    # model = VisionModel()

    torch.save(model.state_dict(), 'visionModel_dict.pth')
    torch.save(model, "visionModel.pth")

    # model = VisionModel().to(device)
    # vision_test(model)
    #
    # model.load_state_dict(torch.load("visionModel_dict.pth", map_location=device))
    # vision_test(model)
    #
    # model = torch.load("visionModel.pth", map_location=device, weights_only=False)
    # vision_test(model)
    pass


if __name__ == "__main__":
    main()
