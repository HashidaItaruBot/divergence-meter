# -*- coding: utf-8 -*-
"""divergence_meter.py 的单元测试。

运行:
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import random
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "divergence_meter.py"
sys.path.insert(0, str(REPO_ROOT))

import divergence_meter as dm  # noqa: E402


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """以子进程方式运行 CLI。"""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def display_text_from_stdout(stdout: str) -> str:
    """从七段数码管 ASCII 渲染结果中反向解析出原始文本 (如 '1.048596')。"""
    lines = stdout.rstrip("\n").split("\n")
    assert len(lines) == 3, f"渲染结果应为 3 行, 实际 {len(lines)} 行"
    lines[1] = lines[1][: -len("  %")]  # 去掉行尾的单位 %
    glyph_count = (len(lines[0]) + 1) // 4  # 每个字形占 3 列 + 1 列间隔
    reverse = {tuple(glyph): char for char, glyph in dm.GLYPHS.items()}
    chars = []
    for i in range(glyph_count):
        key = tuple(line[i * 4: i * 4 + 3] for line in lines)
        assert key in reverse, f"第 {i + 1} 个字形无法识别: {key}"
        chars.append(reverse[key])
    return "".join(chars)


class ParseTest(unittest.TestCase):
    """parse_divergence: 正常值 / 负数 / 非法输入。"""

    def test_normal_values(self):
        self.assertEqual(dm.parse_divergence("1.048596"), 1.048596)
        self.assertEqual(dm.parse_divergence("0.000000"), 0.0)
        self.assertEqual(dm.parse_divergence("9.999999"), 9.999999)

    def test_negative_values(self):
        self.assertEqual(dm.parse_divergence("-0.571024"), -0.571024)
        self.assertEqual(dm.parse_divergence("-9.999999"), -9.999999)

    def test_short_and_loose_forms(self):
        self.assertEqual(dm.parse_divergence("1"), 1.0)
        self.assertEqual(dm.parse_divergence("1.05"), 1.05)
        self.assertEqual(dm.parse_divergence(".5"), 0.5)
        self.assertEqual(dm.parse_divergence("-.5"), -0.5)

    def test_rounds_to_six_decimals(self):
        self.assertEqual(dm.format_divergence(dm.parse_divergence("1.05")), "1.050000")
        self.assertEqual(
            dm.format_divergence(dm.parse_divergence("1.0485963")), "1.048596"
        )

    def test_normalizes_negative_zero(self):
        self.assertEqual(dm.format_divergence(dm.parse_divergence("-0.0000004")), "0.000000")

    def test_invalid_not_a_number(self):
        for raw in ("abc", "", "1.2.3", "1,048", "--", "±0.5"):
            with self.assertRaises(dm.DivergenceMeterError, msg=repr(raw)):
                dm.parse_divergence(raw)

    def test_invalid_special_floats(self):
        for raw in ("nan", "-nan", "inf", "-inf", "infinity"):
            with self.assertRaises(dm.DivergenceMeterError, msg=raw):
                dm.parse_divergence(raw)

    def test_error_message_mentions_bad_input(self):
        with self.assertRaises(dm.DivergenceMeterError) as ctx:
            dm.parse_divergence("abc")
        self.assertIn("abc", str(ctx.exception))

    def test_out_of_range_raises(self):
        for raw in ("10", "10.000000", "42.5", "-10", "-10.000001", "9.9999996"):
            with self.assertRaises(dm.DivergenceMeterError, msg=raw):
                dm.parse_divergence(raw)

    def test_out_of_range_message_shows_range(self):
        with self.assertRaises(dm.DivergenceMeterError) as ctx:
            dm.parse_divergence("42.5")
        self.assertIn("9.999999", str(ctx.exception))


class FormatTest(unittest.TestCase):
    """format_divergence: 固定为 7 位数字 x.xxxxxx。"""

    def test_format_normal(self):
        self.assertEqual(dm.format_divergence(1.048596), "1.048596")
        self.assertEqual(dm.format_divergence(0.0), "0.000000")
        self.assertEqual(dm.format_divergence(9.999999), "9.999999")

    def test_format_negative(self):
        self.assertEqual(dm.format_divergence(-0.571024), "-0.571024")
        self.assertEqual(dm.format_divergence(-9.999999), "-9.999999")


class RenderTest(unittest.TestCase):
    """render_divergence: 七段数码管渲染结构。"""

    def test_render_zero_golden(self):
        self.assertEqual(dm.render_divergence("0", unit=""), " _ \n| |\n|_|")

    def test_render_has_three_rows_and_trailing_percent(self):
        out = dm.render_divergence("1.048596")
        lines = out.split("\n")
        self.assertEqual(len(lines), 3)
        self.assertEqual(
            lines[0], " ".join(dm.GLYPHS[c][0] for c in "1.048596")
        )
        self.assertTrue(lines[1].endswith("%"))
        self.assertNotIn("%", lines[0])
        self.assertNotIn("%", lines[2])

    def test_render_negative_starts_with_minus_bar(self):
        lines = dm.render_divergence("-1.048596").split("\n")
        self.assertTrue(lines[1].startswith(dm.GLYPHS["-"][1]))

    def test_render_rejects_unknown_char(self):
        with self.assertRaises(dm.DivergenceMeterError):
            dm.render_divergence("a")


class RandomTest(unittest.TestCase):
    """generate_random_divergence: 固定 seed 可复现, 范围 0.000000 ~ 9.999999。"""

    def test_fixed_seed_is_reproducible(self):
        self.assertEqual(dm.generate_random_divergence(random.Random(42)), 1.867825)
        self.assertEqual(
            dm.generate_random_divergence(random.Random(42)),
            dm.generate_random_divergence(random.Random(42)),
        )

    def test_values_stay_in_display_range(self):
        rng = random.Random(7)
        pattern = re.compile(r"^\d\.\d{6}$")
        for _ in range(300):
            value = dm.generate_random_divergence(rng)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 9.999999)
            self.assertRegex(dm.format_divergence(value), pattern)


class CliTest(unittest.TestCase):
    """端到端子进程测试: 退出码与真实输出。"""

    def test_cli_normal_value(self):
        proc = run_cli("1.048596")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, dm.render_divergence("1.048596") + "\n")
        self.assertIn("%", proc.stdout)

    def test_cli_negative_value(self):
        proc = run_cli("-0.571024")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, dm.render_divergence("-0.571024") + "\n")

    def test_cli_random_is_a_valid_reading(self):
        proc = run_cli("--random")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(len(proc.stdout.rstrip("\n").split("\n")), 3)
        self.assertIn("%", proc.stdout)
        text = display_text_from_stdout(proc.stdout)
        self.assertRegex(text, r"^\d\.\d{6}$")
        self.assertGreaterEqual(float(text), 0.0)
        self.assertLessEqual(float(text), 9.999999)

    def test_cli_invalid_input_exits_nonzero(self):
        proc = run_cli("abc")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("错误", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_cli_out_of_range_exits_nonzero(self):
        proc = run_cli("42.5")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("超出可显示范围", proc.stderr)

    def test_cli_missing_arg_exits_nonzero(self):
        proc = run_cli()
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("一个参数", proc.stderr)

    def test_cli_extra_args_exits_nonzero(self):
        proc = run_cli("1.048596", "0.000001")
        self.assertNotEqual(proc.returncode, 0)

    def test_cli_help_exits_zero(self):
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                proc = run_cli(flag)
                self.assertEqual(proc.returncode, 0)
                self.assertIn("--random", proc.stdout)


if __name__ == "__main__":
    unittest.main()
