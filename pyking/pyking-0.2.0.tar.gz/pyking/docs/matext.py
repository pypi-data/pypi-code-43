text1 = """
## 绘制函数的数据输入类型

所有绘图函数都需要np.array或np.ma.masked_array对象作为输入类型 。 如果是 “类数组（array-like）” 对象（如pandas数据对象和np.matrix）可能会或可能不会按预期工作。最好在绘图之前将它们转换为np.array对象。

例如，要转换pandas.DataFrame

```python
a = pandas.DataFrame(np.random.rand(4,5), columns = list('abcde'))
a_asndarray = a.values
```

以及转换np.matrix
```python
b = np.matrix([[1,2],[3,4]])
b_asarray = np.asarray(b)
```

## 常见的图表绘制

进行图表绘制时，我们通常使用pyplot对象，具体教程，请参照Pyplot教程。官方文档写的挺不错，深入浅出，建议要入门的铁子们看看。

### 折线图
绘制单个函数的代码如下所示

```python
import matplotlib.pyplot as plt 
import numpy as np
t = np.arange(0., 5., 0.2)
'''
    arange的作用类似于内置函数range，用于生成
    在范围内的一组数据。此处，生成的是在[0,5)之间的，
    相邻数差是0.2的数据。
     
'''
plt.plot(t, t ** 2, 'r--')
'''
    plot用于绘图， t表示横坐标， t ** 2表示t的二次方，
    表示纵坐标。r--则表示线是红色(red)，以'--'形式表现
'''
plt.show()
```
![avatar](https://imimg.mydw.xyz/2019/10/18/8bd0f675a73370f0.png)

如果要绘制包含多个函数的折线图，只要多调用几次plot()函数，或者在同一个plot()函数中填入多个函数即可。

```python
import numpy as np
 
t = np.arange(0., 5., 0.2)
 
plt.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')
'''
   bs表示blue square, 蓝色正方形
   g^表示green 三角形。
'''
plt.show()
```
![avatar](https://imimg.mydw.xyz/2019/10/18/6613b905afbbcf5f.png)
### 柱状图

对于柱状图，我们可以调用plt.bar()。代码示例如下：
```python
names = ['group_a', 'group_b', 'group_c']
values = np.arange(25,100, 25)
plt.bar(names, values)
plt.show()
```

效果如下

![avatar](https://imimg.mydw.xyz/2019/10/18/2956dc17d1fd60f7.png)

现在为止，我们画的都是只有一张图的画板，那有没有那种可以在画板figure上画多个图的实例呢？当然是有的，趁此机会，我们可以学习一下新的功能。

```python
names = ['group_a', 'group_b', 'group_c']
values = [1, 10, 100]
 
plt.figure(1, figsize=(9, 3))
# 设置画板大小，总大小为9，分为3块
plt.subplot(1, 3, 1)
'''
    subplot表示的是一张子图，(1, 3)表示的是整张大图的大小为1 x 3，
    大图里面的每个小图，都有自己的索引，索引从左上角向右依次到
    右下角，逐渐增大，这里的子图索引为1。
'''
plt.bar(names, values) # 绘制柱状图
plt.subplot(132)
'''
    当三个参数都小于10的时候，可以将逗号省略。
'''
plt.scatter(names, values) # 绘制散点图
plt.subplot(133)
plt.plot(names, values) # 绘制折线图
plt.suptitle('Categorical Plotting') # 设置父图的标题
plt.show()
```

效果如下

![avator](https://imimg.mydw.xyz/2019/10/18/d000be27a8e8ba8c.png)

### 散点图

绘制散点图时，需要给定两个np.array，在绘图时，plot会将两个array压缩成一对对的坐标，用于在图像中表示，示例代码如下

```python
plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')
# ro 表示红色(red), 以圆圈(o)形式展示
plt.axis([0, 6, 0, 20])
# 规定横坐标和纵坐标的上下限， x ∈ (0, 6), y ∈ (0, 20) 
plt.show()
```
效果如下

![avator](https://imimg.mydw.xyz/2019/10/18/dbafb609cd400ed2.png)

### 饼状图

最后一个饼图， 除了基本饼图外 ，下列案例中，添加了几个可选项：
- 切片标签
- 自动标记百分比 autopct
- 用explode偏移切片
- 投影 shadow
- 自定义初始角度

请注意，自定义起点角度：

默认的起始角度 startangle 为0 ， 这将在正x轴上开始“Frogs”切片。 此示例将 startangle设置为90 ， 以便将所有对象逆时针旋转90度，并且切片从正y轴开始。

示例代码如下：

```python
import matplotlib.pyplot as plt
 
labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
sizes = [15, 30, 45, 10]
explode = (0, 0.1, 0, 0)
# 分离第二块切片
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True)
ax1.axis('equal')  
# 相等的长宽比可确保将饼图绘制为圆形。
plt.show()
```
效果如下：

![avator](https://imimg.mydw.xyz/2019/10/18/df65cedbbc69a26f.png)

"""
