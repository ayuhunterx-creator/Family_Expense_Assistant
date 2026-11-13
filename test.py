from common import client, VECTOR_STORE_ID

if not VECTOR_STORE_ID:
    raise RuntimeError("請設定 VECTOR_STORE_ID")

print("Vector Store ID:", VECTOR_STORE_ID)

# 確認向量庫存在
store = client.vector_stores.retrieve(
    vector_store_id=VECTOR_STORE_ID
)

print("名稱：", store.name)
print("狀態：", store.status)
print("文件數量：", store.file_counts)

# 確認附加文件
files = client.vector_stores.files.list(
    vector_store_id=VECTOR_STORE_ID
)

for file in files.data:
    print("File ID:", file.id)
    print("文件狀態：", file.status)
    print("錯誤：", file.last_error)