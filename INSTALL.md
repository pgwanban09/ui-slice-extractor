# 安装到 Codex

这个仓库是一个 Codex Skill，不是需要单独启动的应用。Skill 位于 `skills/ui-slice-extractor/`，符合 Codex 的标准安装路径。

用户可以直接把下面这句话发给 Codex：

```text
帮我安装这个 Skill：https://github.com/pgwanban09/ui-slice-extractor
```

Codex 应自动识别仓库中的 `skills/ui-slice-extractor`，调用 GitHub Skill 安装器并安装到当前用户的 Codex Skill 目录。若当前 Codex 版本要求显式路径，使用仓库路径 `skills/ui-slice-extractor`。

## Windows

在 PowerShell 中执行：

```powershell
git clone git@github.com:pgwanban09/ui-slice-extractor.git
Set-Location .\ui-slice-extractor
.\install.ps1
```

如果 PowerShell 阻止脚本运行，可以只对当前进程放开脚本限制后重试：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
```

更新已经安装的版本：

```powershell
git pull
.\install.ps1 -Force
```

安装位置：

```text
%USERPROFILE%\.codex\skills\ui-slice-extractor
```

安装后重启 Codex。不要把仓库复制到项目的 `skills` 目录，也不需要把 API Key、Token 或 SSH 私钥放进仓库。

## 使用

直接给 Codex 一张 PNG、JPG 或 UI 截图，并说明：

```text
使用 UI Slice Extractor，扫描整张图并提取所有前端可复用资产。
请区分裁切、SVG 重绘、脚本重建、生图重建和背景重建，输出资源包、manifest、预览图和校验报告。
```

也可以显式调用：

```text
$ui-slice-extractor 从这张扁平 UI 截图中提取 logo、icon、背景、组件壳和透明装饰。
```

默认输出目录为 `ui-slice-output/`，包含 `icons/`、`backgrounds/`、`overlays/`、`components/`、`previews/`、`manifest.json`、`validation-report.json` 和 ZIP 资源包。

## 运行辅助脚本

脚本需要 Python 3。进入 `skills/ui-slice-extractor/` 后，可以执行：

```powershell
python scripts/validate_assets.py <output_dir>
python scripts/make_preview.py <output_dir>
python scripts/package_assets.py <output_dir> <project_name>
```

生图、背景重建和透明化所需的模型能力由 Codex 当前可用的工具决定；仓库不保存任何密钥。
