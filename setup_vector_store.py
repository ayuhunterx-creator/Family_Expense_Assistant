from pathlib import Path

from family_expense_assistant.common import client, VECTOR_STORE_ID


BASE = Path(__file__).resolve().parent
RULES_PATH = BASE / "data" / "house_rules.md"


def update_house_rules():
    if not VECTOR_STORE_ID:
        raise RuntimeError("請在 .env 設定 VECTOR_STORE_ID")

    if not RULES_PATH.is_file():
        raise FileNotFoundError(RULES_PATH)

    # 1. 找出既有家規文件
    old_files = []

    for vs_file in client.vector_stores.files.list(
        vector_store_id=VECTOR_STORE_ID
    ):
        file_info = client.files.retrieve(vs_file.id)

        if file_info.filename == RULES_PATH.name:
            old_files.append(vs_file.id)

    # 避免誤刪多個同名文件
    if len(old_files) > 1:
        raise RuntimeError(
            "找到多個同名家規文件，請先人工確認。"
        )

    # 2. 上傳新版並等待索引完成
    with RULES_PATH.open("rb") as f:
        new_file = client.vector_stores.files.upload_and_poll(
            vector_store_id=VECTOR_STORE_ID,
            file=f,
        )

    if new_file.status != "completed":
        raise RuntimeError(
            f"新版家規索引失敗：{new_file.last_error}"
        )

    print("新版家規已上傳：", new_file.id)

    # 3. 索引成功後，移除舊版與 Vector Store 的關聯
    for old_file_id in old_files:
        client.vector_stores.files.delete(
            file_id=old_file_id,
            vector_store_id=VECTOR_STORE_ID,
        )
        print("已移除舊版：", old_file_id)

    print("家規更新完成")
    print("Vector Store ID：", VECTOR_STORE_ID)


if __name__ == "__main__":
    update_house_rules()