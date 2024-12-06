# DataMining

## Backup data mongo
``` bash
mongorestore --host localhost --port 27017 --db Data ./backup/Data
```
## File backup
```cpp
#include<bits/stdc++.h>
using namespace std;
int main(){
    cout << "Download in https://links";
    return 0;
}
```
## Quy tình chạy
```bash
python API/main.py
```
```bash
Golive Server
```
## Docker
## Gõ lệnh vào cmd ngay tại thư mục này
```bash
docker-compose up --build -d
```

## Note
- Có dùng volume để tại dữ liệu cho mongoDB tránh lãng phí thời gian

```
├── README.md
├── docker-compose.yml
├── logs
│   └── api.log
├── requirements.txt
├── src
│   ├── API
│   │   ├── Dockerfile
│   │   ├── Models
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── Data
│   │   ├── Core
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── yolov8n.pt
│   ├── Mongo
│   │   └── Dockerfile
│   ├── Public
│   │   ├── Dockerfile
│   │   ├── index.html
│   │   ├── phamcum.html
│   │   ├── phamcum.js
│   │   ├── phamcumcot.html
│   │   ├── phancumcot.js
│   │   ├── rate.html
│   │   ├── rate.js
│   │   ├── script.js
│   │   ├── style.css
│   │   ├── xetheogio.html
│   │   └── xetheogio.js
│   └── Service
│       ├── Dockerfile
│       ├── main.py
│       └── requirements.txt
└── yolov8n.pt


```