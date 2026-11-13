from common import client

stores = client.vector_stores.list()

for store in stores.data:
    print("名稱：", store.name)
    print("ID：", store.id)
    print("狀態：", store.status)
    print("到期設定：", store.expires_after)
    print("-" * 30)