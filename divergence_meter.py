#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""世界线变动率探知机 (Divergence Meter)。

以七段数码管 (seven-segment) 风格的 ASCII 大字显示世界线变动率。

用法:
    python3 divergence_meter.py <变动率>    显示指定变动率, 如 1.048596
    python3 divergence_meter.py --random    随机生成 0.000000 ~ 9.999999 的变动率
    python3 divergence_meter.py -h|--help   显示帮助

变动率形如 x.xxxxxx (数字共 7 位), 显示时末尾带 %。
"""

from __future__ import annotations

import math
import random
import sys

DECIMALS = 6  # x.xxxxxx: 1 位整数 + 6 位小数

# 七段数码管字形: 每个字符 3 行, 每行 3 列
GLYPHS: dict[str, tuple[str, str, str]] = {
    "0": (" _ ", "| |", "|_|"),
    "1": ("   ", "  |", "  |"),
    "2": (" _ ", " _|", "|_ "),
    "3": (" _ ", " _|", " _|"),
    "4": ("   ", "|_|", "  |"),
    "5": (" _ ", "|_ ", " _|"),
    "6": (" _ ", "|_ ", "|_|"),
    "7": (" _ ", "  |", "  |"),
    "8": (" _ ", "|_|", "|_|"),
    "9": (" _ ", "|_|", " _|"),
    ".": ("   ", "   ", " . "),
    "-": ("   ", "___", "   "),
}

USAGE = """\
用法:
  python3 divergence_meter.py <变动率>   显示指定变动率 (形如 x.xxxxxx, 范围 -9.999999 ~ 9.999999)
  python3 divergence_meter.py --random   随机生成 0.000000 ~ 9.999999 的变动率
  python3 divergence_meter.py -h|--help  显示本帮助

示例:
  python3 divergence_meter.py 1.048596
  python3 divergence_meter.py -0.571024
  python3 divergence_meter.py --random\
"""

MAX_ABS = 10 - 10 ** -DECIMALS  # 9.999999


class DivergenceMeterError(ValueError):
    """无效的变动率输入。"""


def parse_divergence(raw: str) -> float:
    """把字符串解析为变动率, 非法输入抛出 DivergenceMeterError。

    接受任意可被 float 解析的数字写法 (含负数、省略前导 0),
    按 6 位小数四舍五入; 超出可显示范围 (-9.999999 ~ 9.999999) 视为非法。
    """
    text = raw.strip()
    if not text:
        raise DivergenceMeterError("变动率不能为空, 请输入形如 x.xxxxxx 的数字")
    try:
        value = float(text)
    except ValueError:
        raise DivergenceMeterError(
            f"'{raw}' 不是有效的变动率数字, 应形如 x.xxxxxx (示例: 1.048596)"
        ) from None
    if not math.isfinite(value):
        raise DivergenceMeterError(
            f"'{raw}' 不是有限的变动率数字, 应形如 x.xxxxxx (示例: 1.048596)"
        )
    value = round(value, DECIMALS)
    if value == 0:  # 归一化 -0.0
        value = 0.0
    if abs(value) >= 10.0:
        raise DivergenceMeterError(
            f"变动率 {format_divergence(value)}% 超出可显示范围 "
            f"-{MAX_ABS:.6f} ~ {MAX_ABS:.6f} (显示位数为形如 x.xxxxxx 的 7 位数字)"
        )
    return value


def format_divergence(value: float) -> str:
    """把变动率格式化为 x.xxxxxx (负数带符号, 共 7 位数字)。"""
    return f"{value:.{DECIMALS}f}"


def generate_random_divergence(rng: random.Random | None = None) -> float:
    """随机生成 0.000000 ~ 9.999999 的变动率。

    传入 random.Random 实例可复现 (例如 random.Random(42))。
    """
    source = rng if rng is not None else random
    max_units = 10 ** (DECIMALS + 1) - 1  # 9_999_999 -> 最大 9.999999
    return source.randint(0, max_units) / 10 ** DECIMALS


def render_divergence(text: str, unit: str = "%") -> str:
    """把形如 x.xxxxxx 的文本渲染成七段数码管风格的 3 行 ASCII 大字。"""
    glyphs: list[tuple[str, str, str]] = []
    for char in text:
        glyph = GLYPHS.get(char)
        if glyph is None:
            raise DivergenceMeterError(f"无法用七段数码管显示字符: {char!r}")
        glyphs.append(glyph)
    rows = [" ".join(glyph[row] for glyph in glyphs) for row in range(3)]
    if unit:
        rows[1] += "  " + unit  # 末尾带 %
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    """CLI 入口; 返回进程退出码。"""
    args = list(sys.argv[1:]) if argv is None else list(argv)
    if "-h" in args or "--help" in args:
        print(USAGE)
        return 0
    if len(args) != 1:
        print("错误: 需要恰好一个参数 (变动率数字) 或 --random", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    arg = args[0]
    try:
        if arg == "--random":
            value = generate_random_divergence()
        else:
            value = parse_divergence(arg)
    except DivergenceMeterError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    print(render_divergence(format_divergence(value)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
