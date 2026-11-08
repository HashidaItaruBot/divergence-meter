# divergence-meter

世界线变动率探知机 (Divergence Meter) — 以《命运石之门》风格的七段数码管 (seven-segment) ASCII 大字显示世界线变动率的命令行工具。

纯 Python 标准库实现, 无第三方依赖, 需要 Python 3.9+。

## 用法

```bash
# 显示指定的变动率 (共 7 位数字, 形如 x.xxxxxx, 范围 -9.999999 ~ 9.999999)
python3 divergence_meter.py 1.048596

# 随机生成 0.000000 ~ 9.999999 的变动率并显示
python3 divergence_meter.py --random

# 帮助
python3 divergence_meter.py -h
```

### 示例

```console
$ python3 divergence_meter.py 1.048596
         _       _   _   _   _
  |     | | |_| |_| |_  |_| |_   %
  |  .  |_|   | |_|  _|  _| |_|

$ python3 divergence_meter.py -0.571024
     _       _   _       _   _
___ | |     |_    |   | | |  _| |_|  %
    |_|  .   _|   |   | |_| |_    |

$ python3 divergence_meter.py --random
 _       _   _   _   _   _   _
|_|     |_|  _|   |   | |_| |_   %
|_|  .   _|  _|   |   |  _|  _|
```

末尾带 `%`; 负数在最左侧显示负号段。

### 非法输入

非法输入会打印明确的中文错误信息并以非零退出码退出:

| 情况 | 示例 | 退出码 |
| --- | --- | --- |
| 不是数字 / 空输入 / `nan` / `inf` | `python3 divergence_meter.py abc` | 1 |
| 超出可显示范围 (±9.999999 之外) | `python3 divergence_meter.py 42.5` | 1 |
| 参数数量不对 / 缺少参数 | `python3 divergence_meter.py` | 2 |

错误输出示例:

```console
$ python3 divergence_meter.py 42.5
错误: 变动率 42.500000% 超出可显示范围 -9.999999 ~ 9.999999 (显示位数为形如 x.xxxxxx 的 7 位数字)
```

### 显示规则

- 变动率固定显示 7 位数字 `x.xxxxxx`, 末尾带 `%`
- 支持负数, 如 `-0.571024`
- 小数超过 6 位按四舍五入处理; `1` 会被格式化为 `1.000000`, `.5` 为 `0.500000`
- `-0.0` 归一化为 `0.000000`

## 测试

```bash
python3 -m unittest discover -s tests -v
```

覆盖范围: 正常值解析与格式化、负数、非法输入 (非数字 / `nan` / `inf` / 越界)、七段数码管渲染结构、`--random` 固定 seed 可复现 (`random.Random(42)` 恒为 `1.867825`)、以及 CLI 子进程端到端测试 (退出码、真实输出、随机读数可反向解析回合法数字)。

当前结果: `Ran 26 tests ... OK`。

## 项目结构

```text
divergence-meter/
├── divergence_meter.py          # CLI 实现
├── tests/
│   └── test_divergence_meter.py # 单元测试 (unittest)
└── README.md
```

El Psy Kongroo.
