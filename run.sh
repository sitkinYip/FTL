#!/usr/bin/env bash
# ──────────────────────────────────────────────
#  FTL - Font Tool Lite  一键启动脚本
#  用法：bash run.sh  或  ./run.sh
# ──────────────────────────────────────────────

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 项目根目录（脚本所在目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"
MAIN="$SCRIPT_DIR/main.py"

echo -e "${CYAN}${BOLD}"
echo "  ███████╗████████╗██╗     "
echo "  ██╔════╝╚══██╔══╝██║     "
echo "  █████╗     ██║   ██║     "
echo "  ██╔══╝     ██║   ██║     "
echo "  ██║        ██║   ███████╗"
echo "  ╚═╝        ╚═╝   ╚══════╝"
echo "  Font Tool Lite  🚀"
echo -e "${NC}"

# ── 辅助函数 ──────────────────────────────────

# 尝试用 sudo 执行命令（提示用户输入密码）
run_with_sudo() {
    echo -e "${YELLOW}  ⚠ 需要管理员权限，请输入密码...${NC}"
    if sudo "$@"; then
        return 0
    else
        echo -e "${RED}  ✗ 权限验证失败或命令执行出错${NC}"
        return 1
    fi
}

# 确保 Homebrew 已安装，未安装则尝试自动安装
ensure_homebrew() {
    if command -v brew &>/dev/null; then
        echo -e "${GREEN}  ✓ Homebrew 已安装${NC}"
        return 0
    fi

    echo -e "${YELLOW}  → 未检测到 Homebrew，尝试自动安装...${NC}"
    echo -e "${CYAN}  ℹ Homebrew 是 macOS 上常用的包管理器，用于安装 Python 等工具${NC}"

    # Homebrew 官方安装脚本
    HOMEBREW_INSTALL_URL="https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"

    if /bin/bash -c "$(curl -fsSL "$HOMEBREW_INSTALL_URL")"; then
        echo -e "${GREEN}  ✓ Homebrew 安装成功${NC}"
    else
        echo -e "${YELLOW}  → 普通权限安装失败，尝试使用 sudo 重新安装...${NC}"
        if run_with_sudo /bin/bash -c "$(curl -fsSL "$HOMEBREW_INSTALL_URL")"; then
            echo -e "${GREEN}  ✓ Homebrew 安装成功（sudo）${NC}"
        else
            echo -e "${RED}  ✗ Homebrew 安装失败，请手动安装后重试${NC}"
            echo -e "${RED}    安装命令：/bin/bash -c \"\$(curl -fsSL $HOMEBREW_INSTALL_URL)\"${NC}"
            exit 1
        fi
    fi

    # 将 brew 加入当前 shell 的 PATH（Apple Silicon 与 Intel 路径不同）
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi

    if ! command -v brew &>/dev/null; then
        echo -e "${RED}  ✗ Homebrew 安装后仍无法找到 brew 命令，请重新打开终端后重试${NC}"
        exit 1
    fi
}

# 通过 Homebrew 安装 Python
install_python_via_brew() {
    ensure_homebrew

    echo -e "${YELLOW}  → 通过 Homebrew 安装 Python...${NC}"

    if brew install python@3; then
        echo -e "${GREEN}  ✓ Python 安装成功${NC}"
    else
        echo -e "${YELLOW}  → 安装失败，尝试使用 sudo 重新安装...${NC}"
        if run_with_sudo brew install python@3; then
            echo -e "${GREEN}  ✓ Python 安装成功（sudo）${NC}"
        else
            echo -e "${RED}  ✗ Python 安装失败，请手动安装 Python 3.9+${NC}"
            exit 1
        fi
    fi

    # 刷新 PATH，确保能找到新安装的 python3
    hash -r 2>/dev/null || true
}

# 检查 Python 版本是否满足要求（>= 3.9）
check_python_version() {
    local cmd="$1"
    local version major minor
    version=$($cmd --version 2>&1 | awk '{print $2}')
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)

    if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
        echo "$version"
        return 0
    fi
    return 1
}

# ── 1. 检查 Python 3 ──────────────────────────
echo -e "${YELLOW}[1/4] 检查 Python 环境...${NC}"

PY_CMD=""
PY_VERSION=""

# 依次尝试 python3、python
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        if version=$(check_python_version "$candidate"); then
            PY_CMD="$candidate"
            PY_VERSION="$version"
            break
        fi
    fi
done

# 没有找到合适的 Python，尝试自动安装
if [ -z "$PY_CMD" ]; then
    # 检查是否有 Python 但版本过低
    if command -v python3 &>/dev/null; then
        OLD_VER=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${YELLOW}  ⚠ 当前 Python 版本 $OLD_VER 过低（需要 3.9+）${NC}"
    elif command -v python &>/dev/null; then
        OLD_VER=$(python --version 2>&1 | awk '{print $2}')
        echo -e "${YELLOW}  ⚠ 当前 Python 版本 $OLD_VER 过低（需要 3.9+）${NC}"
    else
        echo -e "${YELLOW}  ⚠ 未找到 Python${NC}"
    fi

    # 仅 macOS 支持自动安装
    if [ "$(uname -s)" = "Darwin" ]; then
        echo -e "${CYAN}  ℹ 检测到 macOS，将尝试通过 Homebrew 自动安装 Python...${NC}"
        install_python_via_brew

        # 安装后重新查找
        for candidate in python3 python; do
            if command -v "$candidate" &>/dev/null; then
                if version=$(check_python_version "$candidate"); then
                    PY_CMD="$candidate"
                    PY_VERSION="$version"
                    break
                fi
            fi
        done

        if [ -z "$PY_CMD" ]; then
            echo -e "${RED}✗ Python 安装后仍无法满足版本要求（需要 3.9+），请手动处理${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ 非 macOS 系统，请手动安装 Python 3.9+${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Python $PY_VERSION ($PY_CMD)${NC}"

# ── 2. 创建 / 复用虚拟环境 ────────────────────
echo -e "${YELLOW}[2/4] 准备虚拟环境...${NC}"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "  → 创建虚拟环境 .venv ..."
    $PY_CMD -m venv "$VENV_DIR"
    echo -e "${GREEN}  ✓ 虚拟环境创建完成${NC}"
else
    echo -e "${GREEN}  ✓ 复用已有虚拟环境${NC}"
fi

# 激活虚拟环境
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# ── 3. 安装 / 更新依赖 ────────────────────────
echo -e "${YELLOW}[3/4] 检查依赖...${NC}"

if [ ! -f "$REQUIREMENTS" ]; then
    echo -e "${RED}✗ 未找到 requirements.txt${NC}"
    deactivate
    exit 1
fi

# 检查是否需要安装（比较 requirements.txt 修改时间与标记文件）
STAMP_FILE="$VENV_DIR/.deps_installed"

if [ ! -f "$STAMP_FILE" ] || [ "$REQUIREMENTS" -nt "$STAMP_FILE" ]; then
    echo -e "  → 安装依赖（首次或 requirements.txt 已更新）..."
    pip install --quiet --upgrade pip
    pip install --quiet -r "$REQUIREMENTS"
    touch "$STAMP_FILE"
    echo -e "${GREEN}  ✓ 依赖安装完成${NC}"
else
    echo -e "${GREEN}  ✓ 依赖已是最新，跳过安装${NC}"
fi

# ── 4. 启动应用 ───────────────────────────────
echo -e "${YELLOW}[4/4] 启动 FTL...${NC}"
echo -e "${GREEN}${BOLD}─────────────────────────────────────────────${NC}"

cd "$SCRIPT_DIR"
exec python "$MAIN"
