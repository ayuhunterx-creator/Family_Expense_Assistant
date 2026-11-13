from common import client
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent / "data" / "house_rules.md"

# 1. 建立 Vector Store
vector_store = client.vector_stores.create(
    name="家庭記帳小管家"
)
print("Vector Store ID:", vector_store.id)

# 2. 上傳家規文件
with open(RULES_PATH, "rb") as f:
    uploaded_file = client.files.create(
        file=f,
        purpose="assistants"
    )

print("File ID:", uploaded_file.id)

# 3. 將文件加入 Vector Store 並等待索引完成
vector_store_file = client.vector_stores.files.create_and_poll(
    vector_store_id=vector_store.id,
    file_id=uploaded_file.id
)

# 4. 確認結果
if vector_store_file.status == "completed":
    print("家規文件已準備完成")
    print("VECTOR_STORE_ID =", vector_store.id)
else:
    print("索引失敗:", vector_store_file.last_error)