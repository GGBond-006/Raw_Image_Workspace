import argparse
import os
import sys

# 将当前目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import BatchImageEngine


def main():
    parser = argparse.ArgumentParser(description="批量自动化生图系统 CLI (支持多平台生图模型 API)")
    parser.add_argument(
        "--task",
        default=os.path.join(os.path.dirname(__file__), "tasks", "rc4661_task.json"),
        help="单品生图任务 JSON 配置文件路径 (默认: tasks/rc4661_task.json)",
    )
    parser.add_argument(
        "--provider",
        default="qiuqiutoken",
        help="选择生图 API 平台标识 (默认: qiuqiutoken)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="指定生图模型名称 (默认读取平台配置，球球Token 默认为 gpt-image-2)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="API 令牌 (也可通过环境变量 QIUQIU_API_TOKEN 设置)",
    )
    parser.add_argument(
        "--quality",
        default=None,
        choices=["low", "medium", "high", "auto"],
        help="生图质量档位 (low / medium / high / auto，默认 high)",
    )
    parser.add_argument(
        "--filter",
        default="all",
        help=(
            "过滤要生成的图片：\n"
            "  all    - 生成全套所有图片 (默认)\n"
            "  sample - 每个图类各抽 1 张代表图进行快速测试\n"
            "  关键词 - 按文件名或类别过滤，逗号分隔，例如: '主图1.jpg,RC4661A_RC4226A.jpg,RC4661A俄文1.jpg'"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="自定义输出目录路径",
    )
    parser.add_argument(
        "--list-jobs",
        action="store_true",
        help="仅预览待生成的图片清单、参考图路径与 Prompt（不消耗 API 额度）",
    )
    parser.add_argument(
        "--force-api",
        action="store_true",
        help="即使白底副图开启了原厂白底直通，也强制调用生图 API 重新生成",
    )

    args = parser.parse_args()

    engine = BatchImageEngine(
        task_json_path=args.task,
        output_dir=args.output_dir,
        provider_id=args.provider,
        model_name=args.model,
        api_token=args.token,
        quality=args.quality,
    )

    selected = engine.filter_jobs(args.filter)
    missing = engine.validate_reference_files(selected)

    if args.list_jobs:
        print(f"============================================================")
        print(f"任务预览 (Dry-Run): SPU={engine.spu_code} | 匹配任务数={len(selected)} / 总任务数={len(engine.jobs)}")
        print(f"参考图完整性检查: {'全部通过 (0 缺失)' if not missing else f'缺失 {len(missing)} 项!'}")
        print(f"============================================================")
        for i, j in enumerate(selected, start=1):
            refs = [os.path.basename(r) for r in j.get("reference_images", [])]
            print(f"[{i:02d}] {j['filename']:<28} | {j['category']:<20} | {j['target_width']}x{j['target_height']} | 参考图: {refs}")
            print(f"     Prompt: {j['prompt'][:140]}...")
        if missing:
            print("\n[错误] 缺失参考图:")
            for m in missing:
                print("  -", m)
            sys.exit(1)
        return

    engine.run(filter_expr=args.filter, force_api=args.force_api)


if __name__ == "__main__":
    main()
