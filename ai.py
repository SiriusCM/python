import matplotlib.pyplot
import torch
import torchvision

# device = torch.device("cuda:0")
device = torch.device("cpu")


class Net(torch.nn.Module):

    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(28 * 28, 64)
        self.fc2 = torch.nn.Linear(64, 64)
        self.fc3 = torch.nn.Linear(64, 64)
        self.fc4 = torch.nn.Linear(64, 10)

    def forward(self, x):
        x = torch.nn.functional.relu(self.fc1(x))
        x = torch.nn.functional.relu(self.fc2(x))
        x = torch.nn.functional.relu(self.fc3(x))
        x = torch.nn.functional.log_softmax(self.fc4(x), dim=1)
        return x


def get_data_loader(is_train):
    to_tensor = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])
    data_set = torchvision.datasets.MNIST("", is_train, transform=to_tensor, download=True)
    return torch.utils.data.DataLoader(data_set, batch_size=100, shuffle=True)


def evaluate(test_data, net):
    n_correct = 0
    n_total = 0
    with torch.no_grad():
        for (x, y) in test_data:
            x = x.to(device)
            outputs = net.forward(x.view(-1, 28 * 28)).to(device)
            for i, output in enumerate(outputs):
                if torch.argmax(output) == y[i]:
                    n_correct += 1
                n_total += 1
    return n_correct / n_total


def main():
    train_data = get_data_loader(is_train=True)
    test_data = get_data_loader(is_train=False)

    net = Net().to(device)
    print("initial accuracy:", evaluate(test_data, net))
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)

    for epoch in range(2):
        for (x, y) in train_data:
            net.zero_grad()

            x = x.to(device)
            x = net.forward(x.view(-1, 28 * 28))
            y = y.to(device)
            loss = torch.nn.functional.nll_loss(x, y).to(device)

            loss.backward()
            optimizer.step()
        print("epoch", epoch, "accuracy:", evaluate(test_data, net))
    for (n, (x, _)) in enumerate(test_data):
        if n > 2:
            break
        p = x[0]

        x = x.to(device)
        x = net.forward(x[0].view(-1, 28 * 28))
        predict = torch.argmax(x).to(device)

        matplotlib.pyplot.figure(n)
        matplotlib.pyplot.imshow(p.view(28, 28))
        matplotlib.pyplot.title("prediction: " + str(int(predict)))
    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
