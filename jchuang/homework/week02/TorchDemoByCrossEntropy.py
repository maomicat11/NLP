import torch
import torch.nn as nn
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

"""

用交叉熵实现一个多分类任务，五维随机向量最大的数字在哪维就属于哪一类。

"""


class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        # 线性层
        self.linear = nn.Linear(input_size, 5)
        self.activation = nn.Softmax(dim=1)
        # loss函数采用交叉熵损失
        self.loss = nn.CrossEntropyLoss()

    # 当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x, y=None):
        y_pred = self.linear(x)  # (batch_size, input_size) -> (batch_size, 5)
        # y_pred = self.activation(x)  # (batch_size, 5) -> (batch_size, 1)
        if y is not None:
            return self.loss(y_pred, y)  # 预测值和真实值计算损失
        else:
            return self.activation(y_pred)  # 输出预测结果


# 生成一个样本, 样本的生成方法，代表了我们要学习的规律
def build_sample():
    x = np.random.random(5)
    y = np.argmax(x)
    return x, y


# 随机生成一批样本
# 正负样本均匀生成
def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(np.array(X)), torch.LongTensor(np.array(Y))


# 测试代码
# 用来测试每轮模型的准确率
def test(model):
    model.eval()
    test_sample_num = 100
    x, y_true = build_dataset(test_sample_num)
    class_counts = [0] * 5
    for label in y_true:
        class_counts[int(label.item())] += 1
    print(f"各类别样本数：{class_counts}")
    correct, wrong = 0, 0
    # 不计算梯度
    with torch.no_grad():
        y_pred = model(x)
        y_pred = torch.argmax(y_pred, dim=1)
        for y_p, y_t in zip(y_pred, y_true):  # 与真实标签进行对比
            if y_p == y_t:
                correct += 1
            else:
                wrong += 1
    print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)


def main():
    # 训练轮数
    epoch_num = 20
    # 每次训练样本个数
    batch_size = 20
    # 每轮训练总共训练的样本总数
    train_sample = 5000
    # 输入向量维度
    input_size = 5
    # 学习率
    learning_rate = 0.001
    # 建立模型
    model = TorchModel(input_size)
    # 选择优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 创建训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample)
    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size: (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size: (batch_index + 1) * batch_size]
            # 计算loss  model.forward(x,y)
            loss = model(x, y)
            # 计算梯度
            loss.backward()
            # 更新权重
            optim.step()
            # 梯度归零
            optim.zero_grad()
            watch_loss.append(loss.item())
        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = test(model)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "model.bin")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return


# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    model = TorchModel(input_size)
    # 加载训练好的权重
    model.load_state_dict(torch.load(model_path))
    print(model.state_dict())
    # 测试模式
    model.eval()
    # 不计算梯度
    with torch.no_grad():
        # 模型预测
        pre_result = model.forward(torch.FloatTensor(input_vec))

    print("\n--- 预测结果 ---")
    for vec, res in zip(input_vec, pre_result):
        # 打印结果
        print("输入：%s, 预测类别：%d" % (vec, np.argmax(res)))


if __name__ == '__main__':
    main()
    # input_vec = [[0.07889086, 0.15229675, 0.31082123, 0.03504317, 0.88920843],
    #             [0.74963533, 0.5524256, 0.95758807, 0.95520434, 0.84890681],
    #             [0.00797868, 0.67482528, 0.13625847, 0.34675372, 0.19871392],
    #             [0.09349776, 0.59416669, 0.92579291, 0.41567412, 0.1358894]]
    # predict("model.bin", input_vec)
