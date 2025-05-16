# PicStitch (“拼好图”)

一个简单实用的“挖圆并拼接”工具，把图片拆成多张带小圆形的图层，再通过暗度混合还原原图，有点戏谑地避开内容审查。

## 功能特性

- **分割**：将输入图片拆分成  
  - `base.png`：带有圆形白洞的底图  
  - `circle_00.png` … `circle_09.png`：每层只保留相应的圆形补丁  
- **合成**：自动检测目录中所有图片，选最暗图为底，再依次用暗度（取更暗像素）混合还原原图  
- **交互模式**：无参数运行即可获得引导式操作  
- 自动根据图片尺寸选取合理圆半径  
- 支持大小写混合的 `.png`、`.jpg`、`.jpeg`

---

## 安装

1. 克隆或下载本仓库，或直接将 `main.py` 放进项目目录：  
   ```bash
   git clone https://github.com/yourname/picstitch.git
   cd picstitch
   ```  
2. 创建虚拟环境并安装依赖：  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install Pillow
   ```  
3. 赋可执行权限：  
   ```bash
   chmod +x main.py
   ```

---

## 使用说明

### 交互模式

直接运行，无需任何参数：
```bash
$ python main.py
欢迎使用 ‘拼好图’，请选择操作：
1) 分割
2) 合成
输入 1 或 2:
```
根据提示输入源图片路径/目录及输出路径，即可完成分割或合成。

---

### 命令行模式

#### 分割

```bash
python main.py split <源图片> <输出目录>
```

- `<源图片>`：待拆分的原图（如 `in.jpg`）  
- `<输出目录>`：保存 `base.png` 和 `circle_*.png` 的目录  
- **默认参数**：10 层 × 400 圆；半径 = 短边 ÷ 60  

示例：
```bash
python main.py split input.jpg fragments/
# → fragments/base.png
# → fragments/circle_00.png … circle_09.png
```

#### 合成

```bash
python main.py merge <碎片目录> <还原后图片>
```

- `<碎片目录>`：包含 `base.png` 与圆补丁图的目录（支持大小写混合的扩展名）  
- `<还原后图片>`：输出文件名（如 `restore.png`）  

示例：
```bash
python main.py merge fragments/ restored.png
# 自动检测最暗文件为底，再叠加其余图层，输出 restore.png
```

---

## 工作原理

1. **分割**  
   - 复制原图为 `base.png`；  
   - 对 10 层：随机在 `base` 上挖 400 个圆洞（填白），并把对应圆区裁切到新白底图层，保存为 `circle_XX.png`。  
2. **合成**  
   - 扫描目录中所有图片文件（大小写不敏感）；  
   - 按平均亮度选取最暗者为 `base`；  
   - 对每个圆补丁图依次应用暗度混合（取像素最小值），还原原始像素；  
   - 保存最终图像。

---

## 定制 & 进阶

- **层数/圆数**：在 `split_image()` 中调整 `layers` 与 `circles`。  
- **半径**：修改 `// 60` 的除数来控制圆大小。  
- **混合模式**：`merge_image()` 默认使用 `ImageChops.darker`，也可改用乘法 (`multiply`) 或其他模式。

---

## 许可证

MIT © HerbertGao
