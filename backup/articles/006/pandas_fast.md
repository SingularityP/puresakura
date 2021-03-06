
### 8.1 Pandas 十分钟
这是一个关于 Pandas 的简短教程，主要适用于新手。

#### 1 导包
要致富，先修路，只有先导入相关包才能使用 Pandas 软件。

值得一提的是，Pandas 是基于 NumPy 的一种数据处理工具，所以使用前还要导入 NumPy。

也正因如此，Pandas 支持 NumPy 的数据。


```python
import numpy as np
import pandas as pd
```

#### 2 创建对象

**(1) 创建一个序列（Series）**

通过 `pandas.Series([data, index, dtype, name, copy, …])` 函数来创建一个 Pandas 序列，其中 `data` 可以是 Python 的列表、元组，也可以是 NumPy 的数组。


```python
s1 = pd.Series([1, 3, 5, np.nan, 6, 8])
print(s1)

print()

s2 = pd.Series((2, 4, 6, np.pi, 3.14159, 2.71828))
print(s2)

print()

s3 = pd.Series(np.array((-2, 0, 2, np.nan, np.pi)))
print(s3)
```

    0    1.0
    1    3.0
    2    5.0
    3    NaN
    4    6.0
    5    8.0
    dtype: float64
    
    0    2.000000
    1    4.000000
    2    6.000000
    3    3.141593
    4    3.141590
    5    2.718280
    dtype: float64
    
    0   -2.000000
    1    0.000000
    2    2.000000
    3         NaN
    4    3.141593
    dtype: float64
    

**(2) 创建一个数据帧（DataFrame）**

通过 `pandas.DataFrame([data, index, columns, dtype, copy])` 来创建一个 Pandas 数据帧，其中 `data` 可以是 Python 的列表、元组或字典，也可以是 NumPy 的数组。

还可以通过 `DataFrame.reindex()` 函数从已有的数据帧中创建新的数据帧，这之中的数据转移方式是深拷贝。

`index` 是索引列，默认为自然数，`column` 是标题列，默认为自然数。

下面是一些关于创建的例子：


```python
# 使用数组创建
df = pd.DataFrame(np.random.randn(6,4))
print(df)

print()

# 使用列表创建

a = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16],[17,18,19,20],[21,22,23,24]]
df = pd.DataFrame(a)
print(df)

print()

# index、columns 参数的使用
dates = pd.date_range('20190101', periods=6) # 先获取今年的时间数据
print(dates)
df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list('ABCD'))
print(df)
```

              0         1         2         3
    0 -0.072819  0.998099  0.987995  0.443549
    1  0.207642  0.695893 -0.391768  1.605417
    2  0.114123  0.362941  0.416007  0.083608
    3  1.138622 -0.454717  0.893896  1.126942
    4 -1.273439  0.021799 -0.208722  0.712970
    5  1.730062 -1.942459 -1.404361  1.145998
    
        0   1   2   3
    0   1   2   3   4
    1   5   6   7   8
    2   9  10  11  12
    3  13  14  15  16
    4  17  18  19  20
    5  21  22  23  24
    
    DatetimeIndex(['2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04',
                   '2019-01-05', '2019-01-06'],
                  dtype='datetime64[ns]', freq='D')
                       A         B         C         D
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742
    2019-01-04  1.818637 -0.764855  1.045117  0.528153
    2019-01-05 -2.004982  1.277226  0.582606 -0.535835
    2019-01-06  1.332436 -0.745609  0.161661 -0.019354
    


```python
# 使用字典创建
df2 = pd.DataFrame({'A': 1.,
                    'B': pd.Timestamp('20130102'),
                    'C': pd.Series(1, index=list(range(4)), dtype='float32'),
                    'D': np.array([3] * 4, dtype='int32'),
                    'E': pd.Categorical(["test", "train", "test", "train"]),
                    'F': 'foo'})
print(df2)
print()
print(df2.dtypes) # 允许各列使用不同的数据类型
```

         A          B    C  D      E    F
    0  1.0 2013-01-02  1.0  3   test  foo
    1  1.0 2013-01-02  1.0  3  train  foo
    2  1.0 2013-01-02  1.0  3   test  foo
    3  1.0 2013-01-02  1.0  3  train  foo
    
    A           float64
    B    datetime64[ns]
    C           float32
    D             int32
    E          category
    F            object
    dtype: object
    


```python
# 从已有的 DataFrame 创建
df1 = df.reindex(index=dates[0:4], columns=list(df.columns) + ['E'])
print(df1)
```

                       A         B         C         D   E
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576 NaN
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948 NaN
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742 NaN
    2019-01-04  1.818637 -0.764855  1.045117  0.528153 NaN
    

#### 3 查询数据
**(1) 查询首尾信息**

使用 `DataFrame.head([n])` 可以查阅开始的某些行，使用 `DataFrame.tail([n])` 可以查阅末尾的某些行。

例如：


```python
print(df.head())
print()
print(df.tail(3))
```

                       A         B         C         D
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742
    2019-01-04  1.818637 -0.764855  1.045117  0.528153
    2019-01-05 -2.004982  1.277226  0.582606 -0.535835
    
                       A         B         C         D
    2019-01-04  1.818637 -0.764855  1.045117  0.528153
    2019-01-05 -2.004982  1.277226  0.582606 -0.535835
    2019-01-06  1.332436 -0.745609  0.161661 -0.019354
    

**(2) 查询索引、列标签信息**

可以通过 `DataFrame.index`、`DataFrame.columns` 等属性查看数据帧的某些信息。

举个例子：


```python
print(df.index)
print()
print(df.columns)
```

    DatetimeIndex(['2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04',
                   '2019-01-05', '2019-01-06'],
                  dtype='datetime64[ns]', freq='D')
    
    Index(['A', 'B', 'C', 'D'], dtype='object')
    

**(3) 查询概况**

函数 `DataFrame.describe([percentiles, include, …])` 可以显示数据的简要信息。

比如：


```python
print(df.describe())
```

                  A         B         C         D
    count  6.000000  6.000000  6.000000  6.000000
    mean   0.413607 -0.209861 -0.249200 -0.128901
    std    1.463895  1.095974  1.027259  0.403134
    min   -2.004982 -1.763192 -1.700093 -0.535835
    25%   -0.297340 -0.760043 -0.867626 -0.413367
    50%    0.837720 -0.309516 -0.239911 -0.214548
    75%    1.460613  0.489661  0.477370  0.053623
    max    1.818637  1.277226  1.045117  0.528153
    

**(4) 转换为 `ndarray`**

如果想要将 DataFrame 转换成 ndarray 显示，可以使用 `DataFrame.to_numpy()`。

需要注意的是，一个 NumPy 数组（ndarray）有一种数据类型，然而一个 Pandas 数据帧（DataFrame） 每列有一种数据类型，所以 `to_numpy()` 函数会先寻找一个适合所有列的数据类型，直到 `object` 类型，来作为转换后的数组数据类型。

**注意：**

* 对于包含多种数据类型的数据帧，函数可能会造成很大的资源开销。
* 对于全部数据类型为 float 的数据帧，其转换时非常快的，并且不需要复制数据。
* 函数 `to_numpy()` 在 0.24.0 版本后的 Pandas 中才出现，出错的朋友们要注意一下版本。

下面是一个例子：


```python
print(df.to_numpy())
print()
print(df2.to_numpy())
```

    [[ 1.50333906  0.12657773 -0.94300689 -0.41457598]
     [ 0.34300398 -1.76319162 -0.6414834   0.07794826]
     [-0.51078865  0.61068814 -1.70009316 -0.40974162]
     [ 1.81863699 -0.76485479  1.04511694  0.52815318]
     [-2.0049825   1.2772258   0.58260609 -0.53583533]
     [ 1.33243603 -0.74560903  0.16166125 -0.01935447]]
    
    [[1.0 Timestamp('2013-01-02 00:00:00') 1.0 3 'test' 'foo']
     [1.0 Timestamp('2013-01-02 00:00:00') 1.0 3 'train' 'foo']
     [1.0 Timestamp('2013-01-02 00:00:00') 1.0 3 'test' 'foo']
     [1.0 Timestamp('2013-01-02 00:00:00') 1.0 3 'train' 'foo']]
    

**(5) 转置**

属性 `DataFrame.T` 提供数据的转置视图。

如下：


```python
print(df.T)
```

       2019-01-01  2019-01-02  2019-01-03  2019-01-04  2019-01-05  2019-01-06
    A    1.503339    0.343004   -0.510789    1.818637   -2.004982    1.332436
    B    0.126578   -1.763192    0.610688   -0.764855    1.277226   -0.745609
    C   -0.943007   -0.641483   -1.700093    1.045117    0.582606    0.161661
    D   -0.414576    0.077948   -0.409742    0.528153   -0.535835   -0.019354
    

**(6) 排序**

要获得某个维度排序后的视图，可以用 `DataFrame.sort_index([axis, level, …])` 函数。

要获得某个列名排序后的视图，可以用 `DataFrame.sort_values(by[, axis, ascending, …])` 函数。

举个栗子：


```python
print('根据第 1 维（列 "A"）进行降序排序：\n')
print(df.sort_index(axis=1, ascending=False))
print('\n根据列 "B" 进行升序排序：\n')
print(df.sort_values(by='B'))
```

    根据第 1 维（列 "A"）进行降序排序：
    
                       D         C         B         A
    2019-01-01 -0.414576 -0.943007  0.126578  1.503339
    2019-01-02  0.077948 -0.641483 -1.763192  0.343004
    2019-01-03 -0.409742 -1.700093  0.610688 -0.510789
    2019-01-04  0.528153  1.045117 -0.764855  1.818637
    2019-01-05 -0.535835  0.582606  1.277226 -2.004982
    2019-01-06 -0.019354  0.161661 -0.745609  1.332436
    
    根据列 "B" 进行升序排序：
    
                       A         B         C         D
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948
    2019-01-04  1.818637 -0.764855  1.045117  0.528153
    2019-01-06  1.332436 -0.745609  0.161661 -0.019354
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742
    2019-01-05 -2.004982  1.277226  0.582606 -0.535835
    

#### 4 选择数据
关于 Pandas 的数据选择操作，可以使用 Python/Numpy 的选择和赋值的表达语法，但是在实际的开发生产中，Pandas 更加推荐使用优化后的数据选择方法：`.at`，`.iat`，`.loc`，`.iloc`。

**(1) 沿用 Python/NumPy 的选择方式**

Pandas 数据帧和序列支持使用方括号的形式进行索引和切片。例如：


```python
print(df['A'])
print()
print(df[0:3])
```

    2019-01-01    1.503339
    2019-01-02    0.343004
    2019-01-03   -0.510789
    2019-01-04    1.818637
    2019-01-05   -2.004982
    2019-01-06    1.332436
    Freq: D, Name: A, dtype: float64
    
                       A         B         C         D
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742
    

**(2) 通过标签选择**

这里的标签指的是 index 和 column，即索引名称和列名。对标签使用函数 `.loc` 和 `.at` 来选择行列的某些数据，语法与 Python/NumPy 索引和切片方式一样。

其中，如果只选取一个值，用 `.at` 方法会更加高效。 关于 `.loc` 和 `.at` 的其他详细区别，这里不深入讨论。

例如：


```python
# 选取第 0 维 index 为 '2019-01-01' 的一行数据
print(df.loc['2019-01-01'])
# 选取第 1 维 column 为 'A' 和 'B' 的两列数据
print()
print(df.loc[:,['A','B']])
# 选取行为 '20190102'、'20190104'，列为 'A'，'B' 的数据
print()
print(df.loc['20190102':'20190104', ['A', 'B']])
# 两种函数选取单个值，后者更加高效
print()
print(df.loc[dates[0], 'A'])
print(df.at[dates[0], 'A'])
```

    A    1.503339
    B    0.126578
    C   -0.943007
    D   -0.414576
    Name: 2019-01-01 00:00:00, dtype: float64
    
                       A         B
    2019-01-01  1.503339  0.126578
    2019-01-02  0.343004 -1.763192
    2019-01-03 -0.510789  0.610688
    2019-01-04  1.818637 -0.764855
    2019-01-05 -2.004982  1.277226
    2019-01-06  1.332436 -0.745609
    
                       A         B
    2019-01-02  0.343004 -1.763192
    2019-01-03 -0.510789  0.610688
    2019-01-04  1.818637 -0.764855
    
    1.5033390640885553
    1.5033390640885553
    

**(3) 通过坐标选择**

无论是之前的标签选择，还是现在的坐标选择，其索引和切片使用方式本质上是一样的。这里要提醒一下，Pandas 和 Python 以及 NumPy 一样，坐标，或者说是下标，都是从 0 开始的。

同样的，如果只选取一个值，用 `.at` 方法会更加高效。 关于 `.loc` 和 `.at` 的其他详细区别，这里不深入讨论。

下面看看例子就明白了。


```python
# 选取第 0 维坐标为 3 的数据
print(df.iloc[3])
# 选取第 0 维坐标 3 至 坐标 5 ，第 1 维坐标 0 至 坐标 2 的数据
print()
print(df.iloc[3:5, 0:2])
# 坐标支持类似 Python/NumPy 切片的缺省语法
print()
print(df.iloc[1:3, :])
print(df.iloc[:, 1:3])
# 两种函数选取单个值，后者更加高效
print()
print(df.iloc[1,1])
print(df.iat[1,1])
```

    A    1.818637
    B   -0.764855
    C    1.045117
    D    0.528153
    Name: 2019-01-04 00:00:00, dtype: float64
    
                       A         B
    2019-01-04  1.818637 -0.764855
    2019-01-05 -2.004982  1.277226
    
                       A         B         C         D
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742
                       B         C
    2019-01-01  0.126578 -0.943007
    2019-01-02 -1.763192 -0.641483
    2019-01-03  0.610688 -1.700093
    2019-01-04 -0.764855  1.045117
    2019-01-05  1.277226  0.582606
    2019-01-06 -0.745609  0.161661
    
    -1.7631916181724878
    -1.7631916181724878
    

**(4) 通过布尔选择**

正如 Python/NumPy 的索引和切片支持使用布尔类型的集合一样，Pandas 同样有类似的索引和切片方式。

大家过来看看：


```python
# 使用单列布尔值选择数据帧
print(df.B > 0)
print(df[df.B > 0])
# 使用整帧布尔值选择数据帧
print()
print(df > 0)
print(df[df > 0])
```

    2019-01-01     True
    2019-01-02    False
    2019-01-03     True
    2019-01-04    False
    2019-01-05     True
    2019-01-06    False
    Freq: D, Name: B, dtype: bool
                       A         B         C         D
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742
    2019-01-05 -2.004982  1.277226  0.582606 -0.535835
    
                    A      B      C      D
    2019-01-01   True   True  False  False
    2019-01-02   True  False  False   True
    2019-01-03  False   True  False  False
    2019-01-04   True  False   True   True
    2019-01-05  False   True   True  False
    2019-01-06   True  False   True  False
                       A         B         C         D
    2019-01-01  1.503339  0.126578       NaN       NaN
    2019-01-02  0.343004       NaN       NaN  0.077948
    2019-01-03       NaN  0.610688       NaN       NaN
    2019-01-04  1.818637       NaN  1.045117  0.528153
    2019-01-05       NaN  1.277226  0.582606       NaN
    2019-01-06  1.332436       NaN  0.161661       NaN
    

#### 5 更新数据
能选择就能更新，即上一小节选择的数据能够直接赋值以更新，但要注意维度的匹配。

赋值的数据来源可以是列表、元组、NmuPy 数组和 Pandas 的序列、数据帧。

下面用例子熟悉熟悉就 OK 了。


```python
# 使用序列更新整列
s1 = pd.Series([1, 2, 3, 4, 5, 6], index=pd.date_range('20190102', periods=6)) # 一个序列
print('s1 = \n', s1)
df['F'] = s1
print(df)

# 使用 ndarray 更新整列
print()
df.loc[:, 'D'] = np.array([5] * len(df))
print(df)
```

    s1 = 
     2019-01-02    1
    2019-01-03    2
    2019-01-04    3
    2019-01-05    4
    2019-01-06    5
    2019-01-07    6
    Freq: D, dtype: int64
                       A         B         C         D    F
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576  NaN
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948  1.0
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742  2.0
    2019-01-04  1.818637 -0.764855  1.045117  0.528153  3.0
    2019-01-05 -2.004982  1.277226  0.582606 -0.535835  4.0
    2019-01-06  1.332436 -0.745609  0.161661 -0.019354  5.0
    
                       A         B         C  D    F
    2019-01-01  1.503339  0.126578 -0.943007  5  NaN
    2019-01-02  0.343004 -1.763192 -0.641483  5  1.0
    2019-01-03 -0.510789  0.610688 -1.700093  5  2.0
    2019-01-04  1.818637 -0.764855  1.045117  5  3.0
    2019-01-05 -2.004982  1.277226  0.582606  5  4.0
    2019-01-06  1.332436 -0.745609  0.161661  5  5.0
    


```python
# 标签选择并更新
df.at[dates[0], 'A'] = 0
print(df)
# 坐标选择并更新
print()
df.iat[0, 1] = 0
print(df)
# 布尔选择并更新
print()
df2 = df.copy() # 深拷贝
df2[df2 > 0] = -df2
print(df2)
```

                       A         B         C  D    F
    2019-01-01  0.000000  0.126578 -0.943007  5  NaN
    2019-01-02  0.343004 -1.763192 -0.641483  5  1.0
    2019-01-03 -0.510789  0.610688 -1.700093  5  2.0
    2019-01-04  1.818637 -0.764855  1.045117  5  3.0
    2019-01-05 -2.004982  1.277226  0.582606  5  4.0
    2019-01-06  1.332436 -0.745609  0.161661  5  5.0
    
                       A         B         C  D    F
    2019-01-01  0.000000  0.000000 -0.943007  5  NaN
    2019-01-02  0.343004 -1.763192 -0.641483  5  1.0
    2019-01-03 -0.510789  0.610688 -1.700093  5  2.0
    2019-01-04  1.818637 -0.764855  1.045117  5  3.0
    2019-01-05 -2.004982  1.277226  0.582606  5  4.0
    2019-01-06  1.332436 -0.745609  0.161661  5  5.0
    
                       A         B         C  D    F
    2019-01-01  0.000000  0.000000 -0.943007 -5  NaN
    2019-01-02 -0.343004 -1.763192 -0.641483 -5 -1.0
    2019-01-03 -0.510789 -0.610688 -1.700093 -5 -2.0
    2019-01-04 -1.818637 -0.764855 -1.045117 -5 -3.0
    2019-01-05 -2.004982 -1.277226 -0.582606 -5 -4.0
    2019-01-06 -1.332436 -0.745609 -0.161661 -5 -5.0
    

#### 6 处理数据

**(1) 处理缺失数据**

缺失数据处理是数据处理中一个常见的问题。Pandas 默认使用 NumPy 的 np.nan 值作为缺失数据，且默认情况下不参与到 Pandas 的各种运算中。

Pandas 提供了一下函数用于简单地处理缺失数据：

* `DataFrame.dropna([axis, how, thresh, …])` - 移除缺失值
* `DataFrame.fillna([value, method, axis, …])` - 填充缺失值，这里使用给出的 method 填充 value 值
* `DataFrame.replace([to_replace, value, …])` - 使用给出的 value，替换 to_replace 值

对于 np.nan 这样特殊的值，还要补充一下其判断方法：

* `pandas.isna(DataFrame)` - 判断缺失值，返回布尔类型的数据帧

**注释：**

* 上面的移除操作是移除整行，只要该行有缺失值就移除。
* 以上操作会返回新数据帧，而不会修改原有的数据帧。

稍微看看例子：


```python
# 准备一下例子
df1.loc[dates[0]:dates[1], 'E'] = 1
print(df1)
# 移除缺失值
print()
print(df1.dropna(how='any'))
# 填充缺失值
print()
print(df1.fillna(value=5))
# 替换缺失值
print()
print(df1.replace(np.nan, 999))
# 判断缺失值
print()
print(pd.isna(df1))
```

                       A         B         C         D    E
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576  1.0
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948  1.0
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742  NaN
    2019-01-04  1.818637 -0.764855  1.045117  0.528153  NaN
    
                       A         B         C         D    E
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576  1.0
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948  1.0
    
                       A         B         C         D    E
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576  1.0
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948  1.0
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742  5.0
    2019-01-04  1.818637 -0.764855  1.045117  0.528153  5.0
    
                       A         B         C         D      E
    2019-01-01  1.503339  0.126578 -0.943007 -0.414576    1.0
    2019-01-02  0.343004 -1.763192 -0.641483  0.077948    1.0
    2019-01-03 -0.510789  0.610688 -1.700093 -0.409742  999.0
    2019-01-04  1.818637 -0.764855  1.045117  0.528153  999.0
    
                    A      B      C      D      E
    2019-01-01  False  False  False  False  False
    2019-01-02  False  False  False  False  False
    2019-01-03  False  False  False  False   True
    2019-01-04  False  False  False  False   True
    

**(2) 统计**

Pandas 提供对数据的统计功能，诸如均值、时间滚动、简单运算。

更多更具体的函数可以参考 Pandas 官方 API DataFrame 的 Binary operator funcitons。

下面进行简单的示例以抛砖引玉。


```python
# 求均值
print(df.mean())
print(df.mean(0))
print(df.mean(1))
# 时间滚动
print()
s = pd.Series([1, 3, 5, np.nan, 6, 8], index=dates)
print(s)
print(s.shift(2))
# 
print()
print(df)
print(df.sub(s, axis="index"))
```

    A    0.163051
    B   -0.230957
    C   -0.249200
    D    5.000000
    F    3.000000
    dtype: float64
    A    0.163051
    B   -0.230957
    C   -0.249200
    D    5.000000
    F    3.000000
    dtype: float64
    2019-01-01    1.014248
    2019-01-02    0.787666
    2019-01-03    1.079961
    2019-01-04    2.019780
    2019-01-05    1.770970
    2019-01-06    2.149698
    Freq: D, dtype: float64
    
    2019-01-01    1.0
    2019-01-02    3.0
    2019-01-03    5.0
    2019-01-04    NaN
    2019-01-05    6.0
    2019-01-06    8.0
    Freq: D, dtype: float64
    2019-01-01    NaN
    2019-01-02    NaN
    2019-01-03    1.0
    2019-01-04    3.0
    2019-01-05    5.0
    2019-01-06    NaN
    Freq: D, dtype: float64
    
                       A         B         C  D    F
    2019-01-01  0.000000  0.000000 -0.943007  5  NaN
    2019-01-02  0.343004 -1.763192 -0.641483  5  1.0
    2019-01-03 -0.510789  0.610688 -1.700093  5  2.0
    2019-01-04  1.818637 -0.764855  1.045117  5  3.0
    2019-01-05 -2.004982  1.277226  0.582606  5  4.0
    2019-01-06  1.332436 -0.745609  0.161661  5  5.0
                       A         B         C    D    F
    2019-01-01 -1.000000 -1.000000 -1.943007  4.0  NaN
    2019-01-02 -2.656996 -4.763192 -3.641483  2.0 -2.0
    2019-01-03 -5.510789 -4.389312 -6.700093  0.0 -3.0
    2019-01-04       NaN       NaN       NaN  NaN  NaN
    2019-01-05 -8.004982 -4.722774 -5.417394 -1.0 -2.0
    2019-01-06 -6.667564 -8.745609 -7.838339 -3.0 -3.0
    

**(3) 函数作用**

通过函数 `DataFrame.apply(func[, axis, broadcast, …])` 可以沿着数据帧中的某一个维度，应用一次 func 参数所指的函数。

下面看看例子。


```python
print(df.apply(np.cumsum))
print()
print(df.apply(lambda x: x.max() - x.min()))
```

                       A         B         C   D     F
    2019-01-01  0.000000  0.000000 -0.943007   5   NaN
    2019-01-02  0.343004 -1.763192 -1.584490  10   1.0
    2019-01-03 -0.167785 -1.152503 -3.284583  15   3.0
    2019-01-04  1.650852 -1.917358 -2.239467  20   6.0
    2019-01-05 -0.354130 -0.640132 -1.656860  25  10.0
    2019-01-06  0.978306 -1.385741 -1.495199  30  15.0
    
    A    3.823619
    B    3.040417
    C    2.745210
    D    0.000000
    F    4.000000
    dtype: float64
    

**(4) 直方图化**

直方图化是对数据帧或序列中的数据进行统计归类，使其能够直接用于相关的直方图显示。


```python
s = pd.Series(np.random.randint(0, 7, size=10))
print(s)
print(s.value_counts())
```

    0    6
    1    2
    2    5
    3    6
    4    0
    5    0
    6    3
    7    5
    8    1
    9    6
    dtype: int32
    6    3
    5    2
    0    2
    3    1
    2    1
    1    1
    dtype: int64
    

**(5) 字符串方法**

有时候，序列或数据帧中的数据可能是字符串，这时候，可以专门对这些字符串进行一些处理。

通过 `str` 属性可以获得这些字符串，然后就可以进行字符串的操作了。

下面是一个将字符串转换为小写的例子：


```python
s = pd.Series(['A', 'B', 'C', 'Aaba', 'Baca', np.nan, 'CABA', 'dog', 'cat'])
print(s.str.lower())
```

    0       a
    1       b
    2       c
    3    aaba
    4    baca
    5     NaN
    6    caba
    7     dog
    8     cat
    dtype: object
    
