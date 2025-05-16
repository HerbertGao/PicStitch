#!/usr/bin/env python3
import os, glob, argparse, random
import sys
from PIL import Image, ImageDraw, ImageChops

def split_image(src_path, out_dir):
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    layers = 10
    circles = 400
    # 半径：短边的 1/ 60
    r = max(1, min(w, h) // 60)

    # 剩余图：从原图开始，每层挖圆洞（涂白）
    remaining = img.copy()
    draw_rem = ImageDraw.Draw(remaining)

    for i in range(layers):
        layer = Image.new("RGB", (w, h), "white")
        mask = Image.new("L", (w, h), 0)
        draw_mask = ImageDraw.Draw(mask)

        for _ in range(circles):
            # Allow circles to overlap edges by choosing centers from -r to w+r / h+r
            x = random.randint(-r, w + r)
            y = random.randint(-r, h + r)
            bbox = (x - r, y - r, x + r, y + r)
            draw_mask.ellipse(bbox, fill=255)
            draw_rem.ellipse(  # 在剩余图里挖洞
                bbox, fill="white"
            )

        # 只保留这层的“圆”区域
        layer.paste(img, mask=mask)
        layer.save(f"{out_dir}/circle_{i:02d}.png")

    remaining.save(f"{out_dir}/base.png")
    print(f"[√] Split OK → {layers} layers + base.png in “{out_dir}”  （r={r}px）")

def merge_image(src_dir, out_path):
    # 扫描目录中所有文件，按扩展名过滤（大小写不敏感）
    files = [
        os.path.join(src_dir, f) for f in os.listdir(src_dir)
        if os.path.isfile(os.path.join(src_dir, f))
        and os.path.splitext(f)[1].lower() in {'.png', '.jpg', '.jpeg'}
    ]
    if not files:
        print(f"[!] No image files found in '{src_dir}'")
        return

    # 计算每张图的平均亮度，作为判断 base 的依据（最暗者为 base）
    def avg_brightness(path):
        im = Image.open(path).convert("L")
        stat = list(im.getdata())
        return sum(stat) / len(stat)

    brightness = {f: avg_brightness(f) for f in files}
    # 找最暗的图作为 base
    base_path = min(brightness, key=brightness.get)
    # 其余作为 circle layers
    layer_paths = sorted([f for f in files if f != base_path])

    print(f"[i] Detected base image: {os.path.basename(base_path)}")
    base = Image.open(base_path).convert("RGB")
    result = base

    for p in layer_paths:
        ci = Image.open(p).convert("RGB")
        bg = detect_bg_color(ci)
        if bg == 'white':
            # 白底：用暗度混合，将白色区域（255）保留下来
            result = ImageChops.darker(result, ci)
        else:
            # 黑底：用提亮混合，将黑色区域（0）保留下来
            result = ImageChops.lighter(result, ci)

    result.save(out_path)
    print(f"[√] Merge OK → {out_path}")

def detect_bg_color(img):
    # 判断四个角的灰度平均值，<128 则当作黑底，否则当作白底
    gray = img.convert("L")
    w, h = gray.size
    corners = [
        gray.getpixel((0, 0)),
        gray.getpixel((w-1, 0)),
        gray.getpixel((0, h-1)),
        gray.getpixel((w-1, h-1)),
    ]
    return 'black' if sum(corners) / 4 < 128 else 'white'

def main():
    # 如果未提供命令行参数，则进入交互式引导
    if len(sys.argv) == 1:
        print("欢迎使用 ‘拼好图’，请选择操作：")
        print("1) 分割")
        print("2) 合成")
        choice = input("输入 1 或 2: ").strip()
        if choice == "1":
            src = input("请输入原始图片路径: ").strip()
            out = input("请输入输出目录: ").strip()
            os.makedirs(out, exist_ok=True)
            split_image(src, out)
        elif choice == "2":
            src_dir = input("请输入包含分割结果的目录: ").strip()
            out = input("请输入还原后输出图片路径: ").strip()
            os.makedirs(src_dir, exist_ok=True)
            merge_image(src_dir, out)
        else:
            print("无效选项，程序退出。")
        return
    p = argparse.ArgumentParser(
        description="“拼好图”——把图挖洞分层，再秒回原图。")
    sp = p.add_subparsers(dest="cmd", required=True)

    ps = sp.add_parser("split", help="拆分：生成 base.png + circle_*.png")
    ps.add_argument("src", help="输入图片，比如 in.jpg")
    ps.add_argument("out", help="输出目录，会自动创建")

    pm = sp.add_parser("merge", help="合成：base.png + circle_*.png → 原图")
    pm.add_argument("src_dir", help="包含 base.png 和 circle_*.png 的目录")
    pm.add_argument("out", help="还原后的输出图，比如 restored.jpg")

    args = p.parse_args()
    if args.cmd == "split":
        os.makedirs(args.out, exist_ok=True)
    else:
        os.makedirs(args.src_dir, exist_ok=True)

    if args.cmd == "split":
        split_image(args.src, args.out)
    else:
        merge_image(args.src_dir, args.out)

if __name__ == "__main__":
    main()