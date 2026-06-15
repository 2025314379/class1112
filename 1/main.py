"""Smart-CS Agent 入口 —— CLI 交互式智能客服"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from agent import SmartCSAgent

console = Console()


def print_banner():
    banner = """
╔══════════════════════════════════════════╗
║   🤖 Smart-CS Agent                      ║
║   全能型电商智能客服助手                    ║
║                                          ║
║   Skills:                                ║
║   🎭 情绪感知 · 📚 知识库检索 · 🔧 工具调用 ║
╚══════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")
    console.print("输入 'quit' 或 'exit' 退出 | 输入 'clear' 清除对话历史\n", style="dim")


def print_emotion_indicator(emotion_info: dict):
    """打印情绪感知结果"""
    emotion = emotion_info["emotion"]
    emoji_map = {"positive": "😊", "neutral": "😐", "negative": "😡"}
    color_map = {"positive": "green", "neutral": "yellow", "negative": "red"}
    label_map = {"positive": "正向", "neutral": "中性", "negative": "负向"}

    console.print(
        f"[{color_map[emotion]}]用户情绪：{emoji_map[emotion]} {label_map[emotion]}[/{color_map[emotion]}]",
        end=""
    )
    if emotion_info["comfort_message"]:
        console.print(f"  → 已触发安抚策略", style="red italic")
    else:
        console.print()


def print_debug_info(result: dict):
    """打印调试信息"""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("key", style="dim")
    table.add_column("value")

    if result.get("kb_used"):
        table.add_row("📚 知识库命中", "、".join(result["kb_used"]))
    else:
        table.add_row("📚 知识库命中", "无")

    if result.get("tool_calls"):
        for tc in result["tool_calls"]:
            table.add_row(
                f"🔧 {tc['tool_name']}",
                f"参数: {tc['arguments']}",
            )
    console.print(table)


def main():
    print_banner()

    try:
        agent = SmartCSAgent()
    except Exception as e:
        console.print(f"\n[red]Agent 初始化失败: {e}[/red]")
        console.print("[yellow]请确保:[/yellow]")
        console.print("  1. 已安装依赖: pip install -r requirements.txt")
        console.print("  2. 已配置 .env 文件中的 API Key")
        console.print("  3. 网络连接正常\n")
        return

    while True:
        try:
            user_input = console.input("\n[bold green]🧑 您[/bold green]: ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]再见！[/yellow]")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[yellow]感谢使用 Smart-CS Agent，再见！[/yellow]")
            break

        if user_input.lower() == "clear":
            agent.clear_history()
            console.print("[dim]对话历史已清除[/dim]")
            continue

        # 处理中
        with console.status("[cyan]思考中...[/cyan]"):
            result = agent.chat(user_input)

        # 情绪感知
        print_emotion_indicator(result["emotion"])

        # 调试信息
        print_debug_info(result)

        # Agent 回复
        console.print()
        console.print(
            Panel(
                Markdown(result["reply"]),
                title="🤖 Smart-CS Agent",
                border_style="blue",
            )
        )


if __name__ == "__main__":
    main()
