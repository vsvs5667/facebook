from models import DeepPacketCNN, StackedAutoEncoder
import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.utils.data as Data
import os
# from pytorch_lightning.utilities.seed import seed_everything
# from pytorch_lightning import Trainer
# from pytorch_lightning.callbacks import EarlyStopping
import random
def generate_test_data(num):
    train_x = []
    train_y = []
    for i in range(num):
        train_x.append([])
        train_y.append(random.randint(0, 1))
        for j in range(1500):
            train_x[i].append(random.random())
        
    return np.array(train_x), np.array(train_y)

EPOCH = 30
BATCH_SIZE= 1
LR = 0.0005
if_use_gpu = 1 
num_classes = 2
sava_path = '/home/traffic/TDL/model/'
def load_data(fpath):
    #对数据进行预处理，返回样本和标签
    return train_x, train_y

def adjust_learning_rate(optimizer, echo):
    #这个方法不一定要用
    lr = LR*(0.2**(echo/EPOCH))
    for para_group in optimizer.param_groups:
        para_group['lr'] = lr

def get_result(output, true_y):
    pred_y = torch.argmax(output).numpy()
    accuracy = (pred_y == true_y.numpy()).sum().item() * 1.0 / float(true_y.size(0))
    return pred_y, accuracy


def run(feature_file):
    #x, y = load_data(feature_file)
    x,y = generate_test_data(200)
    #seed_everything(seed=9876, workers=True)
    mymodel = DeepPacketCNN(num_classes)

    if if_use_gpu:
        mymodel = mymodel.cuda()

    optimizer = torch.optim.Adam(mymodel.parameters(), lr = LR, weight_decay = 0.001)
    loss_func = nn.CrossEntropyLoss()
    train_x = x #torch.unsqueeze(torch.from_numpy(x), dim = 1)
    #print(train_x)
    #train_x = train_x.view(train_x.size(0), 1)
    train_x = torch.from_numpy(x)
    #train_x = train_x.view(200, 1500)
    train_y = torch.from_numpy(y).type(torch.float)
    # print(train_x.size())
    # print(train_y.size())
    # print(train_y[0])
    train_data = Data.TensorDataset(train_x, train_y)
    train_loader = Data.DataLoader(dataset = train_data, batch_size=BATCH_SIZE, shuffle=True)

    mymodel.train()

    for epoch in range(EPOCH):
        adjust_learning_rate(optimizer, epoch)#这个不一定需要
        for step, (tr_x, tr_y) in enumerate(train_loader):
            batch_x = Variable(tr_x.cuda())
            batch_x = batch_x.view(BATCH_SIZE,1,1500).float()
            batch_y = Variable(tr_y.cuda())
            output = mymodel(batch_x)
            _, accuracy = get_result(output.cpu(), tr_y.cpu())
            # print('predy:',_)

            del batch_x
            # print(batch_y)
            # print(output.size(), batch_y[0].size())
            loss = loss_func(output.unsqueeze(0), batch_y[0].unsqueeze(0).long())
            del batch_y
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            del output

            if step % 100 == 0:
                print(epoch, step, accuracy, loss.item())

    torch.save(mymodel.state_dict(), os.path.join(sava_path, '1.pth'))

run('111')
